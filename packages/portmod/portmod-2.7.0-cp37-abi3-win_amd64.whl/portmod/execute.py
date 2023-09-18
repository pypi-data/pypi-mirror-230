# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
import subprocess
import sys
from pathlib import Path
from shutil import which
from tempfile import TemporaryDirectory
from threading import Lock, Thread
from typing import AbstractSet, Iterable, List, Set, Tuple

from portmodlib.fs import is_parent
from portmodlib.l10n import l10n

from .config import get_config, get_config_value
from .globals import env
from .perms import Permissions
from .win32 import get_personal

if sys.platform == "win32":
    SBIE_LOCK = Lock()


def _required_exe(name: str) -> str:
    path = which(name)

    if not path:
        raise FileNotFoundError(l10n("missing-executable", file=name))
    return path


def resolve_paths(path: str) -> List[str]:
    """
    Returns all paths related to the symlink chain at paths
    If no symlinks exist, just returns path
    """
    paths = []
    prefix = ""
    for part in Path(path).parts:
        if os.path.islink(os.path.join(prefix, part)):
            last = os.path.join(prefix, part)
            paths.append(last)
            while os.path.islink(last):
                linkpath = os.readlink(last)
                if os.path.isabs(linkpath):
                    last = linkpath
                else:
                    last = os.path.normpath(
                        os.path.join(os.path.dirname(last), linkpath)
                    )
                paths.append(last)
        prefix = os.path.realpath(os.path.join(prefix, part))

    return paths


def parents(paths: Set[str]) -> Set[str]:
    results = set()
    for path in paths:
        for ppath in Path(path).parents:
            results.add(str(ppath))
    return results


def _dedup_subpaths(paths: Iterable[str]) -> List[str]:
    used: List[str] = []
    for path in sorted(paths):
        abspath = os.path.abspath(path)
        if os.path.exists(abspath):
            if any(is_parent(abspath, usedpath) for usedpath in used):
                continue
            used.append(abspath)

    return used


def get_paths(
    ro_paths: AbstractSet[str], rw_paths: AbstractSet[str]
) -> Tuple[Set[str], Set[str], Set[str]]:
    result_ro: Set[str] = set()
    result_rw: Set[str] = set()
    symlinks = set()

    def resolve_chain(path: str, path_set: Set[str]):
        chain = resolve_paths(path)
        if chain:
            # Elements are symlinks
            # the last is the end of the symlink chain.
            if os.path.islink(path):
                symlinks.add(path)

            path_set.add(os.path.realpath(path))
            for link in chain[:-1]:
                symlinks.add(link)
            # Ignore last element in chain, since it is
            # part of the resolved path (but not necessarily identical to the resolved
            # path if it's a directory symlink, but the original path pointed to either
            # a subdirectory of the symlink, or a file)
        else:
            path_set.add(path)

    for path in _dedup_subpaths(rw_paths):
        resolve_chain(path, result_rw)

    for path in _dedup_subpaths(ro_paths | rw_paths):
        if path not in result_rw:
            resolve_chain(path, result_ro)

    filtered_symlinks: Set[str] = set()
    for path in _dedup_subpaths(result_ro | result_rw | symlinks):
        if path in symlinks:
            filtered_symlinks.add(path)
    return result_ro, result_rw, filtered_symlinks


def sandbox_execute(
    command: List[str],
    permissions: Permissions,
    *,
    workdir: str,
    pipe_output: bool = False,
    profile: bool = True,
    **kwargs,
) -> subprocess.Popen:
    """
    Executes command within a sandbox

    On Windows/Sandboxie, this will start in a temporary directory rather than workdir,
    and must change directory itself, due to needing to start the process using ForceFolder,
    which can affect other processes run in the directory.

    args:
        command: The command to execute
        permissions: The permissions to set up the sandbox
        pipe_output: Whether or not output should go to a pipe in the returned process
                     object instead of stdout/stderr
        workdir: The starting directory of the process
        profile: If true, sets profile variables in the sandbox
        kwargs: Additional keyword arguments to pass to subprocess.Popen

    returns:
        Process object for the started process.
        This command does not block and wait for the process.
    """

    def cleanup():
        pass

    rw_paths = set(permissions.rw_paths)
    ro_paths = set(permissions.ro_paths)
    if env.TESTING:
        # Add source directory to whitelist so that we can get coverage from subprocesses
        rw_paths.add(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    environ = os.environ.copy()

    if profile:
        # Set profile variables as environment variables in the sandbox
        for key, value in get_config().items():
            if isinstance(value, str):
                environ[key] = value
            elif isinstance(value, bool):
                if value:
                    environ[key] = str(value)

    if permissions.tmp:
        environ["TMP"] = permissions.tmp
        os.makedirs(permissions.tmp, exist_ok=True)

    # ensure paths added at runtime are available
    if "PYTHONPATH" not in environ:
        environ["PYTHONPATH"] = ""
    if sys.platform == "win32":
        environ["PYTHONPATH"] += ";" + ";".join(sys.path)
    else:
        environ["PYTHONPATH"] += ":" + ":".join(sys.path)

    if sys.platform == "linux":
        if permissions.global_read:
            ro_paths.add("/")
        else:
            ro_paths |= {
                "/bin",
                "/etc",
                "/gnu",
                "/lib",
                "/lib32",
                "/lib64",
                "/run",
                "/nix",
                "/opt",
                "/usr",
                "/var",
            }

        ro_paths, rw_paths, symlinks = get_paths(ro_paths, rw_paths)

        ro_bind: List[str] = sum([["--ro-bind", path, path] for path in ro_paths], [])
        bind: List[str] = sum([["--bind", path, path] for path in rw_paths], [])
        symlink: List[str] = sum(
            [["--symlink", os.readlink(path), path] for path in symlinks], []
        )

        # Needs to be a list of command arguments
        # I.e. NOT a string
        if profile:
            user = get_config_value("SANDBOX_PERMISSIONS", [])
            if not isinstance(user, list):
                raise TypeError(
                    "SANDBOX_PERMISSIONS must be a list of arguments to bwrap"
                )
        else:
            user = []

        sandbox_command = (
            [_required_exe("bwrap")]
            + ro_bind
            + bind
            + symlink
            + [
                "--new-session",
                "--dev",
                "/dev",
                "--proc",
                "/proc",
                "--unshare-all",
                "--chdir",
                workdir,
                "--die-with-parent",
            ]
            + user
        )
        if permissions.network:
            sandbox_command.append("--share-net")
        if permissions.tmp:
            sandbox_command.extend(["--bind", permissions.tmp, permissions.tmp])
        else:
            os.makedirs(env.PYBUILD_TMP_DIR, exist_ok=True)
            sandbox_command.extend(["--bind", env.PYBUILD_TMP_DIR, env.PYBUILD_TMP_DIR])
            environ["TMP"] = env.PYBUILD_TMP_DIR

    elif sys.platform == "win32":
        global SBIE_LOCK
        SINI = _required_exe("sbieini.exe")
        start_exe = _required_exe("start.exe")

        SBIE_LOCK.acquire()
        BOXNAME = "Portmod"
        delete_commands = []

        # We use a tmeporary directory which is otherwise unused to launch the sandboxed process
        # The process must then chdir to the actual working directory.
        launchdir = TemporaryDirectory()
        workdir = launchdir.name

        def win32_cleanup():
            try:
                subprocess.check_call(  # nosec B603
                    f'"{start_exe}" /box:{BOXNAME} /silent /nosbiectrl delete_sandbox'
                )
            except subprocess.CalledProcessError:
                pass
            finally:
                # Remove Sandboxie.ini section for box
                subprocess.check_call(f'"{SINI}" set {BOXNAME} * ""')  # nosec B603
                SBIE_LOCK.release()
                launchdir.cleanup()

        cleanup = win32_cleanup  # noqa

        def add_command(command: str, typ: str, value: str, boxname=BOXNAME):
            nonlocal delete_commands
            subprocess.check_call(  # nosec B603
                f'"{SINI}" {command} {boxname} {typ} "{value}"'
            )

        if not permissions.network:
            add_command("set", "NetworkAccess", "*,Block")
            add_command("set", "AllowNetworkAccess", "n")
            add_command("set", "NotifyInternetAccessDenied", "n")
            # This enables a kernel-mode Windows Filtering Platform mechanism for
            # controlling network access, which should be more secure than the default
            # It requires reloading the driver, but we'll just enable it and hope the user
            # reloads at some point.
            add_command("set", "NetworkEnableWFP", "y", boxname="GlobalSettings")

        # Create a temporary directory that can be used without affecting the user's system
        if not permissions.tmp:
            environ["TMP"] = env.PYBUILD_TMP_DIR
        add_command("append", "WriteFilePath", environ["TMP"])

        # Required for use in git bash
        add_command("append", "OpenPipePath", r"\Device\NamedPipe\msys")

        ro_paths.add(os.path.normpath(os.environ["programfiles(x86)"]))
        ro_paths.add(os.path.normpath(os.environ["programfiles"]))

        ro_paths, rw_paths, symlinks = get_paths(ro_paths, rw_paths)

        if not permissions.global_read:
            add_command("append", "ClosedFilePath", get_personal())

        for path in rw_paths:
            add_command("append", "OpenPipePath", path)

        # A wrapper command is used, combined with ForceProcess, as starting the process
        # using sandboxie's start.exe would not give us any stdout or stderr.
        add_command("set", "ForceFolder", workdir)

        # Needs to be a list of command argument tuples
        user = get_config_value("SANDBOX_PERMISSIONS", [])
        if not isinstance(user, list):
            raise TypeError(
                "SANDBOX_PERMISSIONS must be a list with sbieini commands in the order of $command $type $value. "
                'E.g. ["append", "ClosedFilePath", "filename.txt"]'
            )
        for user_command, typ, value in user:
            add_command(user_command, typ, value)
        add_command("set", "Enabled", "y")

        sandbox_command = []
    elif sys.platform == "darwin":
        sandbox_command = [_required_exe("sandbox-exec"), "-p"]

        sandbox_profile = """
            (version 1)
            (deny default)
            (allow process-exec*)
            (allow signal (target self))
            (allow process-fork)
            (allow sysctl-read)
            (allow file-read*
                file-write-data
                (literal "/dev/null")
                (literal "/dev/zero")
            )
            (allow file-read*
                file-write-data
                file-ioctl
                (literal "/dev/dtracehelper")
            )
            (allow ipc-posix-shm)
        """

        if permissions.global_read:
            sandbox_profile += """
                (allow file-read*)
            """
        else:
            sandbox_profile += """
                (allow file-read-data file-read-metadata
                  (regex "^/dev/autofs.*")
                  (regex "^/Users/[^/]*/.gitconfig")
                  (literal "/var")
                  (literal "/dev/fd")
                  (literal "/dev/random")
                  (literal "/dev/urandom")
                  (literal "/var/db")
                  (literal "/var/db/xcode_select_link")
                  (literal "/")
                )
            """

            ro_paths |= {
                "/usr",
                "/System/Library",
                "/Applications",
                "/etc",
                "/private/etc",
                "/Library",
                "/opt",
            }

        if not permissions.tmp:
            environ["TMPDIR"] = env.PYBUILD_TMP_DIR
            os.makedirs(environ["TMPDIR"], exist_ok=True)
        rw_paths.add(environ["TMPDIR"])
        ro_paths.add("/private/var/select/sh")
        ro_paths, rw_paths, symlinks = get_paths(ro_paths, rw_paths)

        if not permissions.global_read:
            sandbox_profile += """
                (allow file-read*"""
            for path in ro_paths:
                sandbox_profile += f"""
                    (subpath "{path}")"""
            for path in parents(ro_paths | rw_paths):
                sandbox_profile += f"""
                    (literal "{path}")"""
            for path in symlinks:
                sandbox_profile += f"""
                    (literal "{path}")"""
            sandbox_profile += """
                )"""

        if permissions.network:
            sandbox_profile += "\n(allow network*)"

        sandbox_profile += """
            (allow file-write* file-read*"""
        for path in rw_paths:
            sandbox_profile += f"""
                (subpath "{path}")"""
        sandbox_profile += """
            )"""

        # Must be a string
        user = get_config_value("SANDBOX_PERMISSIONS", "")
        if not isinstance(user, str):
            raise TypeError(
                "SANDBOX_PERMISSIONS must be a string with sandbox-exec profile contents"
            )
        sandbox_profile += user

        sandbox_command.append(sandbox_profile)
    else:
        raise Exception("Unsupported Platform")

    try:
        kwargs = dict(kwargs)
        if pipe_output:
            # Pipe stdout, and redirect stderr to the same pipe
            kwargs["stdout"] = subprocess.PIPE
            kwargs["stderr"] = subprocess.STDOUT

        proc = subprocess.Popen(  # nosec B603
            sandbox_command + command,
            env=environ,
            encoding="utf-8",
            cwd=workdir,
            **kwargs,
        )

        def wait_and_cleanup():
            proc.wait()
            cleanup()

        Thread(target=wait_and_cleanup).start()
    except Exception as err:
        cleanup()
        raise err

    return proc
