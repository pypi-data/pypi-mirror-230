# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
import shutil
from logging import error, info, warning
from typing import Iterable, List, cast

from packaging import version

from portmod.globals import env, get_version
from portmod.news import update_news
from portmod.query import update_index
from portmod.repo import BaseRepo, LocalRepo, RemoteRepo, get_repo, has_repo
from portmod.repo.metadata import get_master_names
from portmod.repos import add_repo, get_local_repos, get_remote_repos
from portmodlib.l10n import l10n


def sync(repos: Iterable[BaseRepo]):
    old_prefix = env.set_prefix(None)
    # Slow imports
    import git

    local_repos = get_local_repos()
    remote_repos = get_remote_repos()

    to_sync: List[LocalRepo] = []

    for repo in repos:
        if repo.name not in local_repos:
            assert isinstance(repo, RemoteRepo), (
                "If the repository cannot be found locally, "
                "then this must be a RemoteRepo"
            )
            should_be_repo = add_repo(repo)
            assert should_be_repo
            repo = should_be_repo
        else:
            repo = local_repos[repo.name]

        to_sync.append(repo)

    for repo in to_sync:
        if repo.auto_sync and repo.sync_type == "git" and repo.sync_uri:
            if os.path.exists(repo.location):
                info(l10n("syncing-repo", repo=repo.name))
                gitrepo = git.Repo.init(repo.location)
                current = gitrepo.head.commit

                # Remote location has changed. Update gitrepo to match
                if gitrepo.remotes.origin.url != repo.sync_uri:
                    gitrepo.remotes.origin.set_url(repo.sync_uri)

                gitrepo.remotes.origin.pull(rebase=True)

                for diff in current.diff("HEAD"):
                    if diff.renamed_file:
                        print(
                            "{} {} -> {}".format(
                                diff.change_type, diff.a_path, diff.b_path
                            )
                        )
                    if diff.deleted_file:
                        print("{} {}".format(diff.change_type, diff.a_path))
                        if diff.a_path.endswith(".pybuild"):
                            # Remove from pybuild cache
                            parts = diff.a_path.split("/")
                            category = parts[0]
                            file = parts[-1].lstrip(".pybuild")
                            path = os.path.join(
                                env.PYBUILD_CACHE_DIR, repo.name, category, file
                            )
                            if os.path.exists(path):
                                os.remove(path)
                    else:
                        print("{} {}".format(diff.change_type, diff.b_path))

                tags = []
                for tag in gitrepo.tags:
                    # Valid tags must have the tag commit be the merge base
                    # A merge base further back indicates a branch point
                    if tag.name.startswith("portmod_v"):
                        base = gitrepo.merge_base(gitrepo.head.commit, tag.commit)
                        if base and base[0] == tag.commit:
                            tags.append(tag)

                this_version = version.parse(get_version())
                newest = max(
                    [version.parse(tag.name.lstrip("portmod_v")) for tag in tags]
                    + [this_version]
                )
                if newest != this_version and not env.TESTING:
                    warning(l10n("update-message"))
                    warning(l10n("current-version", version=this_version))
                    warning(l10n("new-version", version=newest))
                info(l10n("done-syncing-repo", repo=repo.name))
            else:
                git.Repo.clone_from(repo.sync_uri, repo.location)
                info(l10n("initialized-repository", repo=repo.name))
        elif repo.auto_sync:
            error(
                l10n(
                    "invalid-sync-type",
                    type=repo.sync_type,
                    repo=repo.name,
                    supported="git",
                )
            )

        remote_repos = get_remote_repos()
        for master in get_master_names(repo.location):
            if has_repo(master):
                master_repo = get_repo(master)
            else:
                # As the repository did not previously exist, add_repo will not
                # return None
                master_repo = cast(LocalRepo, add_repo(remote_repos[master]))
            if master_repo not in to_sync:
                to_sync.append(master_repo)

    if os.path.exists(env.PYBUILD_CACHE_DIR):
        local = get_local_repos()
        for repo_name in os.listdir(env.PYBUILD_CACHE_DIR):
            path = os.path.join(env.PYBUILD_CACHE_DIR, repo_name)
            if repo_name not in local:
                print(l10n("cache-cleanup", repo=repo_name))
                shutil.rmtree(path)

    update_news()

    for repo in to_sync:
        update_index(repo)

    env.set_prefix(old_prefix)
