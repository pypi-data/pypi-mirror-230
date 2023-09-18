# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
from typing import Dict, Optional, cast

from portmod.repo import BaseRepo, get_repo
from portmod.repos import get_local_repos, get_remote_repos
from portmod.sync import sync
from portmodlib.l10n import l10n


def sync_args(args):
    local_repos = get_local_repos()
    remote_repos = get_remote_repos()
    to_sync: Dict[str, BaseRepo] = {}

    meta = get_repo("meta")
    # Always sync meta, in case it needs to inform us
    # of newly added repositories
    if not os.path.exists(meta.location):
        sync([meta])
    else:
        to_sync["meta"] = meta

    for name in args.repository or local_repos:
        repo = cast(Optional[BaseRepo], local_repos.get(name) or remote_repos.get(name))
        if repo is None:
            raise RuntimeError(f"Unknown repository {name}")
        to_sync[name] = repo

    sync(to_sync.values())


def add_sync_parser(subparsers, parents):
    parser = subparsers.add_parser("sync", help=l10n("sync-help"), parents=parents)
    parser.add_argument(
        "repository",
        help=l10n("sync-repositories-help"),
        nargs="*",
    )
    parser.set_defaults(func=sync_args)
