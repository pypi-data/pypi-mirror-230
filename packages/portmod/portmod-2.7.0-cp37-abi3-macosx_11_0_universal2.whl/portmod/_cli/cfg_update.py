# Copyright 2022 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
import shutil
from logging import info
from tempfile import NamedTemporaryFile
from typing import Set

from portmod.cfg_protect import (
    get_changes,
    get_mergetool,
    get_redirections,
    merge_files,
    remove_redirection,
)
from portmod.config import variable_data_dir
from portmod.globals import env
from portmod.merge import global_updates
from portmod.prompt import prompt_num, prompt_options
from portmodlib.colour import bright
from portmodlib.l10n import l10n
from portmodlib.parsers.list import add_list, read_list


def apply_changes_to_file(dst: str, src: str, whitelist: Set[str]):
    whitelist_file = os.path.join(variable_data_dir(), "module-data", "file-whitelist")
    blacklist_file = os.path.join(variable_data_dir(), "module-data", "file-blacklist")
    # Display file changes to user and prompt
    original_src = src

    while True:
        output = get_changes(src, dst)
        if dst in whitelist:
            # User won't be prompted, so we should still display output, but supress it
            # unless running verbosely
            info("".join(output))
        else:
            print("".join(output))

        print()

        if dst not in whitelist and not env.INTERACTIVE:
            info(l10n("skipped-update-noninteractive", file=dst))
            break

        response = None
        if dst not in whitelist:
            options = [
                (l10n("yes-short"), l10n("apply-change")),
                (l10n("always-short"), l10n("merge-apply-always")),
                (l10n("skip-change.short"), l10n("skip-change")),
                (l10n("no-short"), l10n("merge-do-not-apply-change")),
                (l10n("never-short"), l10n("merge-apply-never")),
            ]
            mergetool = get_mergetool()
            if mergetool:
                options.append(
                    (
                        l10n("mergetool.short"),
                        l10n("mergetool", mergetool=f'"{mergetool}"'),
                    )
                )
            else:
                print(l10n("mergetool-info", var="MERGE_TOOL"))
                print()

            try:
                response = prompt_options(
                    l10n("apply-above-change-qn", file=bright(dst)), options
                )
            except EOFError:
                response = l10n("no-short")

        if response == l10n("skip-change.short"):
            break

        if dst in whitelist or response in (
            l10n("yes-short"),
            l10n("always-short"),
        ):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if os.path.exists(dst) or os.path.islink(dst):
                os.remove(dst)
            shutil.move(src, dst)
            # Remove the original file if src now points to a merged file
            if original_src != src:
                os.remove(original_src)

            if response == l10n("always-short"):
                add_list(whitelist_file, dst)

            remove_redirection(src, dst)
            break

        if response == l10n("mergetool.short"):
            with open(dst, "r") as file:
                contents = file.read()
            with NamedTemporaryFile(
                "w",
                delete=False,
                prefix="EDITME.",
                suffix="." + os.path.basename(dst),
            ) as tempfile:
                tempfile.write(contents)
                tempfile_path = tempfile.name
            # Merge against intermediate file
            merge_files(src, tempfile_path)
            # Don't break, as we must let the user accept the merged changes first
            src = tempfile_path

        if response in {l10n("no-short"), l10n("never-short")}:
            if response == l10n("never-short"):
                add_list(blacklist_file, dst)

            os.remove(src)
            remove_redirection(src, dst)
            break


def shortstat(src, dst):
    changes = get_changes(src, dst)
    if len(changes) > 2:
        added = sum(1 for line in changes[2:] if line.startswith("+"))
        deleted = sum(1 for line in changes[2:] if line.startswith("+"))
    return f"{added} insertions(+), {deleted} deletions(-)"


def cfg_update(args):
    files = get_redirections()
    if not files:
        info(l10n("cfg-update-nothing-to-do"))
        return

    # Read only once rather than once per file
    whitelist = set()
    whitelist_file = os.path.join(variable_data_dir(), "module-data", "file-whitelist")
    if os.path.exists(whitelist_file):
        whitelist = set(read_list(whitelist_file))

    while files:
        # Prompt for which file to update, then apply each update in order
        for index, (dst, newfiles) in enumerate(files.items()):
            print(
                str(index + 1) + ")",
                l10n("pending-updates-for-file", file=dst, num=len(newfiles)),
            )

        index = 0
        if len(files) > 1:
            try:
                index = prompt_num(
                    l10n("update-file-prompt"), max_val=len(files), cancel=True
                )
            except EOFError:
                break

        dst, newfiles = list(files.items())[index - 1]
        for index, file in enumerate(newfiles):
            info(l10n("cfg-update-file-index", index=index + 1, total=len(newfiles)))
            apply_changes_to_file(dst, file, whitelist)

        files = get_redirections()


def add_cfg_update_parser(subparsers, parents):
    parser = subparsers.add_parser(
        "cfg-update",
        help=l10n("cfg-update-help"),
        parents=parents,
        conflict_handler="resolve",
    )

    parser.set_defaults(func=cfg_update)


def add_module_update_parser(subparsers, parents):
    parser = subparsers.add_parser(
        "module-update",
        help=l10n("module-update-help"),
        parents=parents,
        conflict_handler="resolve",
    )

    parser.set_defaults(func=lambda args: global_updates())
