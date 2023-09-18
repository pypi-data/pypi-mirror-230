# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import logging
import os
import shutil
import sys
import time
from io import StringIO
from logging import error, info, warning
from typing import Iterable, List, Optional

from portmod.io import MergeIO, MergeMode, Message, Task, Transaction
from portmod.pybuild import Pybuild
from portmodlib.atom import Atom, QualifiedAtom, atom_sat
from portmodlib.colour import bright, green
from portmodlib.fs import onerror
from portmodlib.l10n import l10n
from portmodlib.module_util import _add_redirection

from ._deprecated.rebuild import get_rebuild_manifest
from ._deprecated.vfs import (
    clear_vfs_sort,
    require_vfs_sort,
    sort_vfs,
    vfs_needs_sorting,
)
from ._deps import resolve
from .cfg_protect import get_protected_path, get_redirections
from .config import get_config
from .config.license import _user_package_accept_license_path
from .config.profiles import get_system
from .config.sets import BUILTIN_SETS, add_set, get_set, remove_set
from .config.use import _user_package_use_path, add_use
from .download import fetchable, find_download, is_downloaded
from .globals import env
from .loader import (
    AmbiguousAtom,
    _sandbox_execute_pybuild,
    load_all_installed,
    load_installed_pkg,
    load_pkg,
)
from .modules import (
    clear_module_updates,
    modules_need_updating,
    require_module_updates,
    update_modules,
)
from .package import install_pkg, remove_pkg
from .parsers.flags import add_flag
from .perms import Permissions
from .prompt import prompt_bool
from .query import get_flag_desc
from .repo.keywords import _user_package_accept_keywords_path, add_keyword
from .repo.loader import commit_moved
from .transactions import (
    Delete,
    New,
    Transactions,
    UseDep,
    generate_transactions,
    print_transactions,
    sort_transactions,
)
from .tsort import CycleException
from .util import KeywordDep, LicenseDep, select_package
from .vdb import VDB


class InteractiveError(Exception):
    """
    Indicates that the merge cannot continue without user input

    Manual intervention is required
    """


def global_prepare():
    """Performs global system changes which must be done prior to changes"""
    commit_moved()


def global_updates():
    """Performs updates to global configuration"""
    # Fix vfs ordering and update modules

    try:
        sort_vfs()
        clear_vfs_sort()
    except CycleException as e:
        error(f"{e}")

    update_modules()
    clear_module_updates()

    redirections = get_redirections()
    if redirections:
        total_updates = sum(len(src) for src in redirections.values())
        warning(
            l10n(
                "pending-cfg-updates",
                total_updates=total_updates,
                total_files=len(redirections),
                command=f"portmod {env.PREFIX_NAME} cfg-update",
            )
        )


def deselect(pkgs: Iterable[str]):
    all_to_remove = []

    for name in pkgs:
        atom = Atom(name)
        to_remove = []
        for mod in get_set("selected-packages"):
            if atom_sat(mod, atom):
                to_remove.append(mod)

        if len(to_remove) == 1:
            info(">>> " + l10n("remove-from-world", atom=green(to_remove[0])))
            all_to_remove.append(to_remove[0])
        elif len(to_remove) > 1:
            raise AmbiguousAtom(atom, to_remove)

    if not all_to_remove:
        print(">>> " + l10n("no-matching-world-atom"))
        return

    if not env.INTERACTIVE or prompt_bool(bright(l10n("remove-from-world-qn"))):
        for mod in all_to_remove:
            remove_set("selected-packages", mod)


def _update_keywords(keyword_changes: Iterable[KeywordDep], protect: bool):
    keyword_file = _user_package_accept_keywords_path()
    protect_file = None
    if protect:
        protect_file = create_protect_file(keyword_file)

    for keyword in keyword_changes:
        add_keyword(keyword.atom, keyword.keyword, protect_file=protect_file)


def _update_licenses(
    license_changes: Iterable[LicenseDep],
    protect: bool,
):
    license_file = _user_package_accept_license_path()
    protect_file = None
    if protect:
        protect_file = create_protect_file(license_file)

    for license in license_changes:
        add_flag(protect_file or license_file, license.atom, license.license)


def _update_use_flags(use_changes: Iterable[UseDep], protect: bool):
    protect_file = None
    if protect:
        protect_file = create_protect_file(_user_package_use_path())

    for use in use_changes:
        add_use(
            use.flag.lstrip("-"),
            use.atom,
            use.flag.startswith("-"),
            use.comment,
            protect_file=protect_file,
        )


def create_protect_file(path: str):
    # get_protected_path will return the same path
    # if the original file does not exist
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8"):
            pass
    protect_file = get_protected_path(path)
    try:
        shutil.copy2(path, protect_file)
    except FileNotFoundError:
        pass
    _add_redirection(protect_file, path)
    return protect_file


def get_messages(pkg: Pybuild) -> List[Message]:
    """
    Produces messages produced by Pybuild1.warn or Pybuild1.info
    during package phase functions
    """
    warning_path = os.path.join(env.WARNINGS_DIR, pkg.ATOM.CPF)
    info_path = os.path.join(env.WARNINGS_DIR, pkg.ATOM.CPF)
    messages = []
    if os.path.exists(warning_path):
        with open(warning_path, "r") as file:
            messages.append(Message(Message.Type.WARNING, file.read()))

    if os.path.exists(info_path):
        with open(info_path, "r") as file:
            messages.append(Message(Message.Type.INFO, file.read()))
    return messages


def merge(
    atoms: Iterable[str],
    *,
    io: MergeIO,
    delete: bool = False,
    depclean: bool = False,
    auto_depclean: bool = False,
    oneshot: bool = False,
    verbose: bool = False,
    update: bool = False,
    nodeps: bool = False,
    deselect: Optional[bool] = None,
    select: Optional[bool] = None,
    deep: bool = False,
    emptytree: bool = False,
):
    global_prepare()

    # Ensure that we always get the config before performing operations on packages
    # This way the config settings will be available as environment variables.
    get_config()

    targetlist = list(atoms)
    for modstr in targetlist:
        if modstr.startswith("@"):
            # Atom is actually a set. Load set instead
            targetlist.extend(get_set(modstr.replace("@", "")))
            continue

    to_remove = set()
    if delete or depclean:
        for modstr in targetlist:
            if modstr.startswith("@"):
                continue

            skip = False
            atom = Atom(modstr)
            for system_atom in get_system():
                if atom_sat(system_atom, atom):
                    warning(l10n("skipping-system-package", atom=system_atom))
                    skip = True
                    break

            if not skip:
                to_remove.add(atom)

    atomlist = [
        Atom(modstr)
        for modstr in targetlist
        if modstr not in to_remove and not modstr.startswith("@")
    ]

    selected = set(Atom(atom) for atom in atoms if not atom.startswith("@"))
    selected_sets = set(atom[1:] for atom in atoms if atom.startswith("@"))

    explicit = set(selected)
    for selected_set in selected_sets:
        explicit |= get_set(selected_set)

    if delete:
        # Do nothing. We don't care about deps
        transactions = Transactions()
        for atom in to_remove:
            ipkg = load_installed_pkg(atom)
            if not ipkg:
                raise Exception(l10n("not-installed", atom=atom))
            transactions.append(Delete(ipkg))
    elif nodeps:
        fqatoms = []
        enabled_flags = {}
        usedeps = []
        for atom in atomlist:
            pkg, _ = select_package(load_pkg(atom))
            fqatoms.append(pkg.ATOM)
            enabled_flags[pkg.ATOM] = pkg.get_use()
            for flag in atom.USE:
                usedeps.append(
                    UseDep(
                        pkg.ATOM,
                        flag,
                        description=get_flag_desc(pkg, flag),
                        oldvalue=None,
                        comment=("# Use requirement passed on command line",),
                    )
                )
                if flag.startswith("-"):
                    enabled_flags[pkg.ATOM].remove(flag.lstrip("-"))
                else:
                    enabled_flags[pkg.ATOM].add(flag)

        selected_cpn = set()
        for atom in selected:
            pkg, _ = select_package(load_pkg(atom))
            selected_cpn.add(QualifiedAtom(pkg.CPN))

        transactions = generate_transactions(
            fqatoms,
            [],
            set() if oneshot or depclean else selected_cpn,
            usedeps,
            enabled_flags,
            update=update,
            emptytree=emptytree,
        )
    else:
        transactions = resolve(
            atomlist,
            to_remove,
            explicit,
            set() if oneshot or depclean else selected,
            set() if oneshot or depclean else selected_sets,
            deep=deep
            or (depclean and not to_remove),  # No argument depclean implies deep
            update=update,
            depclean=auto_depclean or depclean,
            emptytree=emptytree,
        )

    transactions = sort_transactions(transactions)

    # Inform user of changes
    if transactions.pkgs:
        # Don't print transaction list when in quiet mode and no-confirm is passed
        if env.INTERACTIVE or logging.root.level < logging.WARN:
            if delete or depclean:
                io.display_transactions(
                    MergeMode.REMOVE, transactions.pkgs, transactions.new_selected
                )
            else:
                io.display_transactions(
                    MergeMode.INSTALL, transactions.pkgs, transactions.new_selected
                )
    elif (vfs_needs_sorting() or modules_need_updating()) and not transactions.pkgs:
        global_updates()
        io.finished(l10n("nothing-else-to-do"))
        return
    elif not transactions.pkgs:
        io.finished(l10n("nothing-to-do"))
        return

    tasks = []

    if transactions.config:
        protect = not env.INTERACTIVE and not env.TESTING

        keyword_changes = list(
            filter(lambda x: isinstance(x, KeywordDep), transactions.config)
        )
        if keyword_changes:
            keyword_task = Task(_update_keywords, keyword_changes, protect)
            tasks.append(keyword_task)
            io.keyword_changes(keyword_changes, keyword_task)

        license_changes = list(
            filter(lambda x: isinstance(x, LicenseDep), transactions.config)
        )
        if license_changes:
            license_task = Task(_update_licenses, license_changes, protect)
            tasks.append(license_task)
            io.license_changes(license_changes, license_task)

        use_changes = list(filter(lambda x: isinstance(x, UseDep), transactions.config))
        if use_changes:
            use_task = Task(_update_use_flags, use_changes, protect)
            tasks.append(use_task)
            io.use_changes(use_changes, use_task)

        # Note: Only CLI should be able to be non-interactive.
        if protect:
            # In non-interactive mode, don't continue if configuration changes are required
            while not all(task.done for task in tasks):
                time.sleep(0.01)
            info("")
            warning(
                l10n(
                    "configuration-changes-required",
                    command=f"portmod {env.PREFIX_NAME} cfg-update",
                ),
            )
            sys.exit(1)

    # Create a temporary VDB so that common packages needed for pkg_nofetch and pkg_pretend
    # but that haven't yet been installed can be found by the loader
    info("Making new common packages available to the packaging environment...")
    if os.path.exists(env.TMP_VDB):
        shutil.rmtree(env.TMP_VDB, onerror=onerror)

    for trans in transactions.pkgs:
        if isinstance(trans, New) and trans.pkg.CATEGORY == "common":
            os.makedirs(os.path.join(env.TMP_VDB, "common", trans.pkg.PN))
            shutil.copy2(
                trans.pkg.FILE, os.path.join(env.TMP_VDB, "common", trans.pkg.PN)
            )

    def get_restricted_fetch(transactions: Transactions):
        # Check for restricted fetch packages and print their nofetch notices
        restricted = 0
        for trans in transactions.pkgs:
            if not isinstance(trans, Delete):
                can_fetch = fetchable(trans.pkg, trans.flags)
                sources = trans.pkg.get_source_manifests(trans.flags)
                to_fetch = [
                    source for source in sources if find_download(source) is None
                ]
                if set(to_fetch) - set(can_fetch) and not is_downloaded(
                    trans.pkg, trans.flags
                ):
                    restricted += len(set(to_fetch) - set(can_fetch))
                    state = {
                        "UNFETCHED": to_fetch,
                        "A": sources,
                        "USE": trans.flags,
                    }
                    proc = _sandbox_execute_pybuild(
                        trans.pkg.FILE,
                        "nofetch",
                        Permissions(),
                        init=state,
                        pipe_output=True,
                    )
                    io.pkg_nofetch(trans.pkg.ATOM, proc.read_output(timeout=5))
                    proc.wait()
        return restricted

    info("Checking for restricted-fetch downloads...")
    restricted_downloads = get_restricted_fetch(transactions)

    tmp_dir = env.TMP_DIR
    # If TMP_DIR doesn't exist, either use the parent, or if that doesn't exist,
    # just create it
    if not os.path.exists(env.TMP_DIR):
        if os.path.exists(os.path.dirname(env.TMP_DIR)):
            tmp_dir = os.path.dirname(env.TMP_DIR)
        else:
            os.makedirs(tmp_dir, exist_ok=True)
    tmp_space = shutil.disk_usage(tmp_dir).free

    pre_merge_warnings = 0
    for trans in transactions.pkgs:
        if not isinstance(trans, Delete) and "pkg_pretend" in trans.pkg.FUNCTIONS:
            # TODO: There are various variables that should be set on mod during pkg_pretend
            info(">>> " + l10n("pkg-pretend", atom=green(trans.pkg.ATOM.CPF)))
            proc = _sandbox_execute_pybuild(
                trans.pkg.FILE,
                "pretend",
                Permissions(),
                save_state=True,
                init={"USE": trans.flags},
                pipe_output=True,
            )
            io.pkg_pretend(trans.pkg.ATOM, proc.read_output(timeout=5))
            proc.wait()

            total_size = 0
            for source in trans.pkg.get_source_manifests(trans.flags):
                total_size += source.size

            # We assume that files have a compression ratio of approximately 0.5
            # Thus we want at least twice the size of the archives in free space.
            if total_size * 2 > tmp_space:
                pre_merge_warnings += 1
                io.space_warning(
                    trans.pkg.ATOM,
                    l10n(
                        "tmp-space-too-small",
                        dir=env.TMP_DIR,
                        free=tmp_space / 1024 / 1024,
                        size=total_size * 2 / 1024 / 1024,
                    ),
                )
            pre_merge_warnings += len(
                {
                    message
                    for message in get_messages(trans.pkg)
                    if message.typ == Message.Type.WARNING
                }
            )

    if pre_merge_warnings:
        warning(l10n("pre-merge-warnings", warnings=pre_merge_warnings))

    if restricted_downloads and not env.INTERACTIVE:
        raise InteractiveError(l10n("exiting-non-interactive-nofetch"))

    # Wait for initial tasks to complete
    while not all(task.done for task in tasks):
        time.sleep(0.01)
    tasks.clear()

    def final_checks():
        nonlocal restricted_downloads

        if restricted_downloads:
            warning(l10n("restricted-fetch-summary", restricted=restricted_downloads))
            # Update restricted download count.
            new_restricted_downloads = get_restricted_fetch(transactions)
            if new_restricted_downloads >= restricted_downloads:
                raise InteractiveError(l10n("restricted-fetch-unchanged"))
            restricted_downloads = new_restricted_downloads

    while env.INTERACTIVE:
        ready_task = Task(final_checks)
        io.merge_ready(ready_task)
        while not ready_task.done:
            time.sleep(0.01)
        if restricted_downloads <= 0:
            break

    err = None
    merged: List[Transaction] = []
    try:
        # Install (or remove) packages in order
        for trans in transactions.pkgs:
            if isinstance(trans, Delete):
                remove_pkg(trans.pkg, io=io.get_remove_io(trans.pkg.ATOM))
                if deselect is None or deselect:
                    if trans.pkg.CPN in get_set("selected-packages"):
                        info(
                            ">>> "
                            + l10n("remove-from-world", atom=green(trans.pkg.CPN))
                        )
                        remove_set("selected-packages", trans.pkg.CPN)
                merged.append(trans)
            else:
                install_pkg(
                    trans.pkg, trans.flags, io=io.get_install_io(trans.pkg.ATOM)
                )

                if trans.pkg in transactions.new_selected and not oneshot:
                    if trans.pkg.CPN not in get_set("selected-packages"):
                        info(">>> " + l10n("add-to-world", atom=green(trans.pkg.CPN)))
                        add_set("selected-packages", trans.pkg.CPN)
                merged.append(trans)

            require_module_updates()
            if trans.pkg._PYBUILD_VER == 1:
                require_vfs_sort()
                sort_vfs()
                clear_vfs_sort()
    # Unable to install package. Aborting installing remaining packages
    except Exception as e:
        err = trans.pkg.ATOM
        raise e
    # Run final code even if package installation fails
    finally:
        for trans in merged:
            messages = get_messages(trans.pkg)

            if messages:
                io.pkg_messages(trans.pkg.ATOM, messages)

        for set_name in selected_sets:
            if set_name not in BUILTIN_SETS:
                if deselect or delete or depclean:
                    remove_set("selected-sets", Atom(set_name))
                else:
                    add_set("selected-sets", Atom(set_name))

        # If no packages successfully merged, there's nothing to update in the VDB
        with StringIO() as transstring:
            print_transactions(
                merged, set(), verbose=True, out=transstring, summarize=False
            )
            if err:
                # There was an error. We report the packages that were successfully merged and
                # note that an error occurred, however we still commit anyway.
                summary = l10n("merge-success-and-error", num=len(merged), atom=err)
            else:
                summary = l10n("merge-success", num=len(merged))

            if merged:
                # Commit changes to installed database
                with VDB(summary + "\n" + transstring.getvalue()):
                    pass
            if err:
                info(summary)
                io.finished(summary)
    # Check if packages were just modified and can be removed from the rebuild set
    # Any transaction type warrants removal, as they were either rebuilt,
    # and thus can be removed, or deleted, and no longer need to be rebuilt
    for atom in get_set("rebuild"):
        installed_pkg = load_installed_pkg(atom)
        if (
            not installed_pkg
            or installed_pkg.CPN in [trans.pkg.CPN for trans in merged]
            and installed_pkg._PYBUILD_VER == 1
        ):
            remove_set("rebuild", atom)

    for pkg in load_all_installed():
        # If no pybuild1 packages are installed, the rebuild feature isn't needed
        if pkg._PYBUILD_VER == 1:
            info(l10n("checking-rebuild"))
            break

    # Check if packages need to be added to rebuild set
    for pkg in load_all_installed():
        if pkg.CPN not in get_set("rebuild") and pkg.INSTALLED_REBUILD_FILES:
            seen = set()
            for entry in get_rebuild_manifest(
                pkg.get_installed_env().get("REBUILD_FILES", [])
            ):
                seen.add(entry.name)
                if pkg.INSTALLED_REBUILD_FILES.get(entry.name) != entry:
                    add_set("rebuild", pkg.CPN)
                    break
            if not all(entry in seen for entry in pkg.INSTALLED_REBUILD_FILES.entries):
                add_set("rebuild", pkg.CPN)

    if get_set("rebuild"):
        io.rebuild_warning(sorted(get_set("rebuild")), l10n("rebuild-message"))

    global_updates()
    info(summary)
    io.finished(summary)
