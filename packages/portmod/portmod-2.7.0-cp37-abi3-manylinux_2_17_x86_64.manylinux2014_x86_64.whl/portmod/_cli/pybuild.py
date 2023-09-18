# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
CLI for interacting with individual pybuild files
"""

import os
import py_compile
import sys
from logging import error, info, warning

from portmod.download import download_source
from portmod.globals import env
from portmod.loader import load_file
from portmod.parsers.manifest import FileType, Manifest, ManifestEntry
from portmod.pybuild import Pybuild, manifest_path
from portmod.repo import get_repo_root
from portmod.repo.metadata import (
    is_pybuild_version_banned,
    is_pybuild_version_deprecated,
)
from portmod.repos import LocalRepo
from portmod.source import HashAlg
from portmodlib._loader import _iterate_pybuilds
from portmodlib.l10n import l10n
from portmodlib.portmod import parse_yaml_mapping

from .merge import CLIFetchProgress


def create_manifest(pkg: Pybuild):
    """
    Automatically downloads mod DIST files (if not already in cache)
    and creates a manifest file
    """
    manifest = Manifest(manifest_path(pkg.FILE))

    existing_sources = set()

    # Collect the names of existing files
    for file in _iterate_pybuilds(os.path.abspath(os.path.dirname(pkg.FILE))):
        if file == pkg.FILE:
            continue
        thismod = load_file(file)
        existing_sources |= {
            source.name for source in thismod.get_sources(matchall=True)
        }

    # Remove files not referenced by any of the package files
    # This will also remove files, if any, referenced by the package file being added to the manifest
    for name in {name for name in manifest.entries if name not in existing_sources}:
        del manifest.entries[name]

    # Add sources from the package file to manifest
    for source in load_file(pkg.FILE).get_sources(matchall=True):
        filename = download_source(
            pkg,
            source,
            get_progress=lambda filename, start, end: CLIFetchProgress(
                filename, start=start, end=end
            ),
        )
        if filename is None:
            error("Unable to get shasum for unavailable file " + source.name)
            continue

        manifest.add_entry(
            ManifestEntry.from_path(
                FileType.DIST, filename, source.name, [HashAlg.BLAKE3, HashAlg.MD5]
            )
        )

    # Write changes to manifest
    manifest.write()


def pybuild_validate(file_name):
    _, ext = os.path.splitext(file_name)
    if ext == ".pybuild":
        # Verify that pybuild is valid python
        py_compile.compile(file_name, doraise=True)
    elif ext == ".yaml":
        with open(file_name) as file:
            parse_yaml_mapping(file.read(), file_name)

    # Verify fields of pybuild
    pkg = load_file(file_name)
    if is_pybuild_version_banned(get_repo_root(file_name), pkg._PYBUILD_VER):
        raise TypeError(f"{file_name} uses Pybuild{pkg._PYBUILD_VER}, which is banned")
    if is_pybuild_version_deprecated(get_repo_root(file_name), pkg._PYBUILD_VER):
        warning(f"{file_name} uses Pybuild{pkg._PYBUILD_VER}, which is deprecated")
    pkg.validate()


def pybuild_manifest(file_name):
    if not os.path.exists(file_name):
        raise FileNotFoundError(l10n("file-does-not-exist", file=file_name))

    repo_root = get_repo_root(file_name)

    if repo_root is None:
        raise FileNotFoundError(l10n("repository-does-not-exist"))

    # Register repo in case it's not already in repos.cfg
    REAL_ROOT = os.path.realpath(repo_root)
    if not any([REAL_ROOT == os.path.realpath(repo.location) for repo in env.REPOS]):
        sys.path.append(os.path.join(repo_root))
        env.REPOS.append(LocalRepo(os.path.basename(repo_root), repo_root))

    if not env.STRICT:
        raise Exception("Must be in strict mode when generating the manifest!")

    mod = load_file(file_name)

    create_manifest(mod)
    info(l10n("created-manifest", atom=mod.ATOM))
