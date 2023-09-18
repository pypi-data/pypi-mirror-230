# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import csv
import filecmp
import os
from collections import defaultdict
from difflib import unified_diff
from logging import debug, info, warning
from pathlib import Path
from string import Template
from typing import Dict, List, Optional

from portmodlib.execute import execute
from portmodlib.fs import get_hash, match
from portmodlib.l10n import l10n
from portmodlib.parsers.list import read_list

from .config import get_config_value, variable_data_dir
from .globals import env


def get_protected_path(file: str) -> str:
    new_file = file
    i = 1
    while os.path.exists(new_file):
        name, ext = os.path.splitext(new_file)
        if ext.startswith(".__cfg_protect"):
            new_file = name + f".__cfg_protect_{i}__"
            i += 1
        else:
            new_file = file + ".__cfg_protect__"
    return new_file


def is_protected(file: str) -> bool:
    protected = get_config_value("CFG_PROTECT")
    if isinstance(protected, list):
        for pattern in protected:
            if match(Path(file).absolute().relative_to(env.prefix().ROOT), pattern):
                return True
    elif isinstance(protected, str):
        if match(Path(file).absolute().relative_to(env.prefix().ROOT), protected):
            return True
    return False


def get_mergetool() -> Optional[str]:
    """Returns user-configured mergetool"""
    result = get_config_value("MERGE_TOOL")
    if result:
        return str(result)
    return None


def merge_files(source: str, dest: str):
    """Invokes user-configured mergetool"""
    mergetool = get_mergetool()
    assert mergetool
    execute(
        Template(mergetool).substitute(
            orig=f'"{source}"', new=f'"{dest}"', merged=f'"{dest}"'
        )
    )


def get_redirections() -> Dict[str, List[str]]:
    """
    Iterates over all previously made file redirections and returns the (non-empty)
    results
    """
    results = defaultdict(list)
    to_remove = []
    if os.path.exists(os.path.join(env.prefix().CONFIG_PROTECT_DIR, "cfg_protect.csv")):
        with open(
            os.path.join(env.prefix().CONFIG_PROTECT_DIR, "cfg_protect.csv"), "r"
        ) as file:
            reader = csv.reader(file)
            for index, row in enumerate(reader):
                if not row:
                    continue
                if len(row) != 2:
                    warning(f"Invalid redirection in {file} on line {index}: {row}")
                    continue
                dst = row[0]
                src = row[1]

                if os.path.exists(src) and os.stat(src).st_size != 0:
                    results[dst].append(src)
                else:
                    to_remove.append((src, dst))

    for src, dst in to_remove:
        remove_redirection(src, dst)

    filtered = defaultdict(list)
    blacklist_file = os.path.join(variable_data_dir(), "module-data", "file-blacklist")
    blacklist = set()
    if os.path.exists(blacklist_file):
        blacklist = set(read_list(blacklist_file))

    for dst, newfiles in results.items():
        for newfile in newfiles:
            # If file is identical, ignore
            if os.path.exists(dst) and filecmp.cmp(newfile, dst, shallow=False):
                remove_redirection(newfile, dst)
                os.remove(newfile)
                continue

            if dst in blacklist:
                info(l10n("skipped-blacklisted-file", file=dst))
                remove_redirection(newfile, dst)
                os.remove(newfile)
                continue
            filtered[dst].append(newfile)

    for dst, newfiles in filtered.items():
        hashes: Dict[str, str] = {}
        # Do it backwards both so that we can remove from the list without breaking the iterator,
        # and to ensure we keep the most recent version of any duplicates.
        for path in reversed(newfiles):
            hash_value = get_hash(path)[0]
            if hash_value in hashes:
                # Double check
                if filecmp.cmp(path, hashes[hash_value], shallow=False):
                    debug(f"Removing old duplicate update file {path}")
                    remove_redirection(path, dst)
                    newfiles.remove(path)
                    os.remove(path)
            else:
                hashes[hash_value] = path
    return filtered


def remove_redirection(src: str, dst: str):
    path = os.path.join(env.prefix().CONFIG_PROTECT_DIR, "cfg_protect.csv")
    if os.path.exists(path):
        with open(path, "r") as file:
            reader = csv.reader(file)
            rows = list(reader)
        with open(path, "w") as output_file:
            writer = csv.writer(output_file)
            for row in rows:
                if not row:
                    continue
                row_dst = row[0]
                row_src = row[1]
                if row_dst != dst and row_src != src:
                    writer.writerow(row)


def get_changes(src: str, dst: str) -> List[str]:
    if os.path.islink(src):
        src_lines = [l10n("symlink-to", path=os.readlink(src)) + "\n"]
    else:
        try:
            with open(src, "r") as src_file:
                src_lines = src_file.readlines()
        except UnicodeDecodeError:
            src_lines = ["<" + l10n("binary-data") + ">\n"]
    dst_lines = []
    if os.path.lexists(dst):
        if os.path.islink(dst):
            dst_lines = [l10n("symlink-to", path=os.readlink(dst)) + "\n"]
        else:
            try:
                with open(dst, "r") as dst_file:
                    dst_lines = dst_file.readlines()
            except UnicodeDecodeError:
                dst_lines = ["<" + l10n("binary-data") + ">\n"]

    return list(unified_diff(dst_lines, src_lines, dst, src))
