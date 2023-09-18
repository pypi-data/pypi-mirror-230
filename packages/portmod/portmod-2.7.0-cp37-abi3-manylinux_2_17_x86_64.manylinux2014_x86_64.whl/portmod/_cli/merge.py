# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""Interface for installing and removing packages"""

import argparse
import logging
import os
import sys
import traceback
from logging import error, info, warning
from shutil import move, rmtree
from typing import AbstractSet, Dict, Optional, Sequence

from portmod._deps import DepError, PackageDoesNotExist
from portmod.download import get_filename
from portmod.globals import env
from portmod.io import (
    InstallIO,
    MergeIO,
    MergeMode,
    Message,
    PhaseFunction,
    Progress,
    RemoveIO,
    Task,
    Transaction,
)
from portmod.loader import AmbiguousAtom, SandboxedProcess, load_all
from portmod.lock import exclusive_lock
from portmod.merge import InteractiveError, deselect, global_updates, merge
from portmod.news import display_unread_message
from portmod.prompt import prompt_bool, prompt_options
from portmod.pybuild import Pybuild
from portmod.query import FlagDesc, LocalFlagDesc
from portmod.repo import get_repo
from portmod.repo.keywords import WildcardKeyword
from portmod.repo.metadata import get_license
from portmod.transactions import print_transactions
from portmod.util import KeywordDep, LicenseDep, UseDep
from portmodlib.atom import Atom, FQAtom, InvalidAtom
from portmodlib.colour import bright, green, lblue, lgreen, red, yellow
from portmodlib.fs import onerror
from portmodlib.l10n import l10n

from . import atom_metavar


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def filter_mods(mods):
    atoms = []
    os.makedirs(env.DOWNLOAD_DIR, exist_ok=True)

    for mod in mods:
        if os.path.isfile(mod):
            for atom in load_all():
                for source in atom.get_source_manifests(matchall=True):
                    if source.check_file(mod):
                        move(mod, get_filename(source.name))
                        atoms.append(atom.ATOM)
            if os.path.exists(mod):
                warning(l10n("no-package-for-file", file=os.path.basename(mod)))
        else:
            atoms.append(mod)

    return atoms


def add_merge_parser(subparsers, parents):
    parser = subparsers.add_parser(
        "merge",
        help=l10n("merge-help"),
        description=l10n("merge-desc"),
        parents=parents,
        conflict_handler="resolve",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "packages",
        metavar=atom_metavar(archive=True, sets=True),
        help=l10n("package-help"),
        nargs="*",
    )
    parser.add_argument(
        "--ignore-default-opts",
        help=l10n("ignore-default-opts-help"),
        action="store_true",
    )
    parser.add_argument(
        "-c", "--depclean", help=l10n("depclean-help"), action="store_true"
    )
    parser.add_argument(
        "-x", "--auto-depclean", help=l10n("auto-depclean-help"), action="store_true"
    )
    parser.add_argument(
        "-C", "--unmerge", help=l10n("unmerge-help"), action="store_true"
    )
    parser.add_argument(
        "-1", "--oneshot", help=l10n("oneshot-help"), action="store_true"
    )
    parser.add_argument("-O", "--nodeps", help=l10n("nodeps-help"), action="store_true")
    parser.add_argument("-u", "--update", help=l10n("update-help"), action="store_true")
    parser.add_argument(
        "-n", "--noreplace", help=l10n("noreplace-help"), action="store_true"
    )
    parser.add_argument("-N", "--newuse", help=l10n("newuse-help"), action="store_true")
    parser.add_argument(
        "-e", "--emptytree", help=l10n("emptytree-help"), action="store_true"
    )
    parser.add_argument("-D", "--deep", help=l10n("deep-help"), action="store_true")
    parser.add_argument(
        "-w",
        "--select",
        type=str2bool,
        nargs="?",
        const=True,
        default=None,
        metavar=l10n("yes-or-no"),
        help=l10n("merge-select-help"),
    )
    parser.add_argument(
        "--deselect",
        type=str2bool,
        nargs="?",
        const=True,
        default=None,
        metavar=l10n("yes-or-no"),
        help=l10n("merge-deselect-help"),
    )
    parser.add_argument("--sort-vfs", help=argparse.SUPPRESS, action="store_true")
    parser.add_argument("--debug", help=l10n("merge-debug-help"), action="store_true")

    parser.set_defaults(func=merge_main)


@exclusive_lock()
def merge_main(args):
    atoms = filter_mods(args.packages)
    env.DEBUG = args.debug

    if args.nodeps and args.depclean:
        error(l10n("nodeps-depclean"))
        sys.exit(1)

    try:
        if atoms or args.depclean:
            # If deselect is supplied (is not None), only deselect if not removing.
            # If removing, remove normally, but deselect depending on supplied value.
            if args.deselect and not (args.unmerge or args.depclean):
                deselect(atoms)
            else:
                try:
                    merge(
                        atoms,
                        delete=args.unmerge,
                        depclean=args.depclean,
                        oneshot=args.oneshot,
                        verbose=args.verbose,
                        update=args.update or args.newuse or args.noreplace,
                        nodeps=args.nodeps,
                        deselect=args.deselect,
                        select=args.select,
                        auto_depclean=args.auto_depclean,
                        deep=args.deep,
                        emptytree=args.emptytree,
                        io=CLIMerge(),
                    )

                    # Note: When execeptions occur, TMP_DIR should be preserved
                    if not env.DEBUG and os.path.exists(env.TMP_DIR):
                        rmtree(env.TMP_DIR, onerror=onerror)
                        info(">>> " + l10n("cleaned-up", dir=env.TMP_DIR))
                except (
                    InvalidAtom,
                    PackageDoesNotExist,
                    AmbiguousAtom,
                    DepError,
                    InteractiveError,
                ) as e:
                    if args.debug:
                        traceback.print_exc()
                    error(f"{e}")
                    sys.exit(1)

        if args.sort_vfs:
            global_updates()

    finally:
        display_unread_message()


class CLIMerge(MergeIO):
    def display_transactions(
        self,
        mode: MergeMode,
        transactions: Sequence[Transaction],
        new_selected: AbstractSet[Pybuild],
    ):
        """
        Transaction list to display to the user

        args:
            transactions: List of transactions to perform, in order.
            new_selected: Packages which were selected for installation
                          these, along with previously selected packages
                          (use :py:func:`portmod.config.sets:is_selected`) should be
                          visually distinguished from packages which are installed
                          just as dependencies
        """
        print(l10n(mode.value))
        verbose = logging.root.level <= logging.DEBUG
        print_transactions(transactions, new_selected, verbose=verbose)
        print()

    def use_changes(self, use_flags: Sequence[UseDep], apply_callback: Task):
        """
        Display necessary flag changes to the user and prompt them to accept
        the changes

        args:
            use_flags: he use flag changes which are required
            apply_callback: Task, which when executed will apply the changes
        """
        display_flags: Dict[str, FlagDesc] = {}
        for use in use_flags:
            flag = use.flag.lstrip("-")
            desc = use.description
            if isinstance(desc, LocalFlagDesc):
                display_flags[Atom(desc.pkg.ATOM.CPF).use(flag)] = desc
            else:
                display_flags[flag] = desc or FlagDesc("<missing description>")

        for key, value in display_flags.items():
            print(l10n("use-flag-desc", desc=value, flag=bright(lgreen(key))))

        print()
        print(l10n("necessary-flag-changes"))
        for use in use_flags:
            comment = "\n    ".join(use.comment)
            if comment:
                comment += "\n    "
            if use.flag.startswith("-") and use.oldvalue == use.flag.lstrip("-"):
                print(
                    "   {}{} {} # {}".format(
                        comment,
                        lblue(use.atom),
                        red(use.flag),
                        l10n("enabled-comment"),
                    )
                )
            elif not use.flag.startswith("-") and use.oldvalue == "-" + use.flag:
                print(
                    "    {}{} {} # {}".format(
                        comment,
                        green(use.atom),
                        red(use.flag),
                        l10n("disabled-comment"),
                    )
                )
            else:
                print("    {}{} {}".format(comment, green(use.atom), red(use.flag)))
        if not env.INTERACTIVE or prompt_bool(l10n("apply-changes-qn")):
            apply_callback.run()
        else:
            sys.exit(1)

    def keyword_changes(self, keywords: Sequence[KeywordDep], apply_callback: Task):
        """
        Display necessary keyword changes to the user and prompt them to accept
        the changes

        args:
            keywords: The keyword changes which are required
            apply_callback: Task, which when executed will apply the changes
        """
        for keyword in keywords:
            if keyword.masked:
                error(
                    l10n(
                        "package-masked-keyword",
                        atom=keyword.atom.CPN,
                        arch=env.prefix().ARCH,
                    )
                )
                sys.exit(1)

        print(l10n("necessary-keyword-changes"))
        for keyword in keywords:
            if keyword.keyword == WildcardKeyword.ALWAYS:
                c = red
            else:
                c = yellow
            print("    {} {}".format(green(keyword.atom), c(keyword.keyword)))

        if not env.INTERACTIVE or prompt_bool(l10n("apply-changes-qn")):
            apply_callback.run()
        else:
            sys.exit(1)

    def license_changes(self, licenses: Sequence[LicenseDep], apply_callback: Task):
        """
        Display licenses which need to be accepted and prompt the user to accept them

        args:
            licenses: The licenses which must be accepted
            apply_callback: Task, which when executed will apply the changes
        """
        warning(l10n("necessary-license-changes"))
        for license in licenses:
            print("    {} {}".format(green(license.atom), license.license))
            # For EULA licenses, display the license and prompt the user to accept
            if license.is_eula and env.INTERACTIVE:
                print()

                def indent(text: str) -> str:
                    return "\n".join(["    " + line for line in text.split("\n")])

                print("    ---", l10n("license-start", license=license.license), "---")
                print(
                    indent(
                        get_license(get_repo(license.repo).location, license.license)
                    )
                )
                print("    ---", l10n("license-end", license=license.license), "---")

            if not env.INTERACTIVE or prompt_bool(l10n("apply-changes-qn")):
                pass
            else:
                sys.exit(1)

        apply_callback.run()

    def pkg_nofetch(self, package: FQAtom, instructions: str):
        """
        Display fetch information for the package

        args:
            package: The package which contains files which could not be fethed
            instructions: The instructions produced by the package describing how
                         to manually fetch the files
        """
        print(bright(yellow(l10n("fetch-instructions", atom=package))))
        print(instructions)
        print()

    def rebuild_warning(self, packages: Sequence[Atom], message: str):
        """
        Display message about packages which need to be rebuilt

        args:
            packages: The package which need to be rebuilt
            message: Message to display
        """
        warning(message)
        for atom in packages:
            print(f"    {green(atom)}")
        print(
            l10n(
                "rebuild-prompt",
                command=lgreen(f"portmod {env.PREFIX_NAME} merge @rebuild"),
            )
        )

    def pkg_messages(self, package: FQAtom, messages: Sequence[Message]):
        """
        Display custom messages for the package

        atgs:
            package: The package which produced the custom messages
            messages: Messages to display
        """
        print()
        print(">>> " + l10n("pkg-messages", atom=bright(green(package))))
        for message in messages:
            if message.typ == Message.Type.WARNING:
                warning(message.text)
            elif message.typ == Message.Type.INFO:
                info(message.text)
        print()

    def pkg_pretend(self, package: FQAtom, message: str):
        """
        Display pkg_pretend messages for the package

        args:
            package: The package which produced the message
            message: The output from pkg_pretend
        """
        print(message)

    def space_warning(self, package: FQAtom, message: str):
        """
        Display message about insufficient space

        args:
            package: The package which contains files which could not be fetched
            message: Message to display
        """
        # FIXME: indicate which package caused the warning
        warning(message)

    def merge_ready(self, start_callback: Task):
        """
        Called when all checks have passed and we are ready to merge

        args:
            start_callback: Task to indicate that the user wants to begin merge
        """
        if prompt_bool(l10n("continue-qn")):
            start_callback.run()
        else:
            sys.exit(1)

    def finished(self, message: str):
        """
        Called when the merge operation has finished. The message should be displayed to the user
        """

    def get_install_io(self, package: FQAtom) -> InstallIO:
        """
        Produce an InstallIO object for use when installing a package

        This will be called once for each package to be installed
        """
        return CLIInstall(package)

    def get_remove_io(self, package: FQAtom) -> RemoveIO:
        """
        Produce an InstallIO object for use when removing a package

        This will be called once for each package to be installed
        """
        return CLIRemove(package)


class CLIProgress(Progress):
    def get_bar(self, start: int, end: Optional[int]):
        try:
            from progressbar import GranularBar as Bar
        except ImportError:
            from progressbar import Bar
        from progressbar import (
            Percentage,
            ProgressBar,
            SimpleProgress,
            Timer,
            UnknownLength,
        )

        return ProgressBar(
            widgets=[
                Percentage(),
                " (",
                SimpleProgress(),
                ") ",
                Bar(),
                " ",
                Timer(),
            ],
            max_value=end or UnknownLength,
            initial_value=start,
        )

    def __init__(self, *, start: int = 0, end: Optional[int] = None):
        self.current = 0
        if sys.stdout.isatty():
            self.bar = self.get_bar(start=start, end=end)
            self.bar.start()
        else:
            from progressbar import NullBar

            self.bar = NullBar()

    def update(self, *, value: Optional[int] = None):
        if value:
            self.current = value
        else:
            self.current += 1
        self.bar.update(self.current)

    def done(self):
        self.bar.finish()


class CLIFetchProgress(CLIProgress):
    def __init__(self, _filename: str, start: int, end: Optional[int]):
        super().__init__(start=start, end=end)

    def get_bar(self, start: int, end: Optional[int]):
        try:
            from progressbar import GranularBar as Bar
        except ImportError:
            from progressbar import Bar
        from progressbar import (
            ETA,
            DataSize,
            FileTransferSpeed,
            Percentage,
            ProgressBar,
            UnknownLength,
        )

        return ProgressBar(
            widgets=[
                Percentage(),
                " ",
                Bar(),
                " ",
                ETA(),
                " ",
                FileTransferSpeed(),
                " ",
                DataSize(),
            ],
            max_value=end or UnknownLength,
            initial_value=start,
        )


class CLIRemove(RemoveIO):
    def __init__(self, atom):
        super().__init__(atom, False)

    def begin_removal(self):
        pass

    def phase_function(self, function: PhaseFunction, process: SandboxedProcess):
        pass

    def finished_removal(self):
        pass

    def remove_files(self, count: int) -> Progress:
        """Should return something which can handle displaying file installation progress"""
        return CLIProgress(end=count)


class CLIInstall(CLIRemove, InstallIO):
    def __init__(self, atom):
        super().__init__(atom)
        self.overwrite_all = False

    def begin_install(self):
        pass

    def finished_install(self):
        pass

    def check_conflicts(self, count: int) -> Progress:
        """Should return something which can handle displaying file conflict progress"""
        return CLIProgress(end=count)

    def install_files(self, count: int) -> Progress:
        """Should return something which can handle displaying file installation progress"""
        return CLIProgress(end=count)

    def get_fetch_progress(
        self, filename: str, start: int, end: Optional[int]
    ) -> Progress:
        """Returns a progress for displaying remote file fetching progress"""
        return CLIFetchProgress(filename, start=start, end=end)

    def can_overwrite(self, path: str) -> bool:
        if env.INTERACTIVE and not self.overwrite_all:
            result = prompt_options(
                l10n("pkg-file-conflict-prompt", file=path),
                [
                    (l10n("yes-short"), l10n("overwrite")),
                    (l10n("no-short"), l10n("dont-overwrite")),
                    (l10n("always-short"), l10n("always-overwrite")),
                ],
            )
        else:
            result = l10n("yes-short")

        if result == l10n("always-short"):
            self.overwrite_all = True

        return result in (l10n("yes-short"), l10n("always-short")) or self.overwrite_all
