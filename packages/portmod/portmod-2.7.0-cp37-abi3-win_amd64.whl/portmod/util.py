# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Various utility functions
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable, List, NamedTuple, Optional, Tuple

from portmod.config.license import has_eula, is_license_accepted
from portmod.repo.keywords import (
    Keyword,
    NamedKeyword,
    Stability,
    WildcardKeyword,
    get_stability,
)
from portmodlib.atom import QualifiedAtom, version_gt
from portmodlib.functools import deprecated

from .globals import env
from .pybuild import Pybuild

if TYPE_CHECKING:
    from portmod.query import FlagDesc


class UseDep(NamedTuple):
    atom: QualifiedAtom
    flag: str
    description: Optional[FlagDesc]
    oldvalue: Optional[str]
    comment: Tuple[str, ...]

    def __repr__(self):
        if self.oldvalue:
            return f"UseDep({self.atom}, {self.oldvalue} -> {self.flag})"
        else:
            return f"UseDep({self.atom}, {self.flag})"


def is_keyword_masked(arch: str, keywords: Iterable[str]):
    return "-" + arch in keywords or (
        "-*" in keywords and arch not in keywords and "~" + arch not in keywords
    )


class KeywordDep(NamedTuple):
    """A requirement that a keyword be accepted before the package can be installed"""

    atom: QualifiedAtom
    keyword: Keyword
    masked: bool


class LicenseDep(NamedTuple):
    """A requirement that a license be accepted before the package can be installed"""

    atom: QualifiedAtom
    license: str
    is_eula: bool
    repo: str


def select_package(packages: Iterable[Pybuild]) -> Tuple[Pybuild, Any]:
    """
    Chooses a mod version based on keywords and accepts it if the license is accepted
    """
    if not packages:
        raise Exception("Cannot select mod from empty modlist")

    stable = []
    testing = []
    untested = []
    masked = []

    for package in packages:
        stability = get_stability(package)
        if stability == Stability.STABLE:
            stable.append(package)
        elif stability == Stability.TESTING:
            testing.append(package)
        elif stability == Stability.MASKED:
            masked.append(package)
        elif stability is Stability.UNTESTED:
            untested.append(package)

    is_masked = False
    keyword: Optional[Keyword] = None

    if stable:
        package = max(stable, key=lambda pkg: pkg.version)
    elif testing:
        # No packages were accepted. Choose the best version and add the keyword
        # as a requirement for it to be installed
        package = max(testing, key=lambda pkg: pkg.version)
        keyword = NamedKeyword(env.prefix().ARCH, Stability.TESTING, None)
    elif untested:
        package = max(untested, key=lambda pkg: pkg.version)
        keyword = WildcardKeyword.ALWAYS
    elif masked:
        package = max(masked, key=lambda pkg: pkg.version)
        keyword = WildcardKeyword.ALWAYS
        is_masked = True

    deps: List[Any] = []
    if not is_license_accepted(package, package.get_use()):
        deps.append(
            LicenseDep(package.CPN, package.LICENSE, has_eula(package), package.REPO)
        )
    if keyword is not None:
        deps.append(
            KeywordDep(
                QualifiedAtom("=" + package.ATOM.CPF),
                keyword,
                is_masked,
            )
        )

    return (package, deps or None)


@deprecated(
    version="2.4",
    reason="Use max(versions, None) instead, using the version class from portmodlib.version. "
    "This function will be removed in portmod 2.7",
)
def get_max_version(versions: Iterable[str]) -> Optional[str]:
    """
    Returns the largest version in the given list

    Version should be a valid version according to PMS section 3.2,
    optionally follwed by a revision

    Returns None if the version list is empty
    """
    newest = None
    for version in versions:
        if newest is None or version_gt(version, newest):
            newest = version
    return newest


@deprecated(
    version="2.4",
    reason="Use max(packages, None, key=lambda x: x.version) instead. "
    "This function will be removed in portmod 2.7",
)
def get_newest(packages: Iterable[Pybuild]) -> Pybuild:
    """Returns the newest mod in the given list based on version"""
    return max(packages, key=lambda pkg: pkg.version)


@deprecated(
    version="2.4",
    reason="Use sorted(packages, key=lambda x: x.version) instead. "
    "This function will be removed in portmod 2.7",
)
def sort_by_version(packages: Iterable[Pybuild]) -> List[Pybuild]:
    """
    Sorts the given packages in order of version
    """
    return sorted(packages, key=lambda pkg: pkg.version)
