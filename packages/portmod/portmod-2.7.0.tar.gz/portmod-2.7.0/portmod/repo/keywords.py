# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, List, Optional

from portmod.config.mask import get_unmasked
from portmod.globals import env
from portmod.parsers.flags import add_flag, get_flags, remove_flag
from portmodlib.atom import QualifiedAtom, atom_sat
from portmodlib.version import Version, VersionRange

from ..config import get_config
from ..pybuild import Pybuild


# Note: in KEYWORDS, the absence of a keyword indicates untested
# The UNTESTED variant is never associated with a NamedKeyword
class Stability(Enum):
    MASKED = "masked"
    TESTING = "testing"
    STABLE = "stable"
    UNTESTED = "untested"

    def __str__(self):
        return self.value

    def __le__(self, other: Any):
        return self < other or self == other

    def __lt__(self, other: Any):
        if not isinstance(other, Stability):
            raise NotImplementedError()

        order = [
            Stability.MASKED,
            Stability.UNTESTED,
            Stability.TESTING,
            Stability.STABLE,
        ]
        return order.index(self) < order.index(other)


# TODO: Phase out '.'
_kw_name_re = re.compile(r"^([A-Za-z0-9][A-Za-z0-9_.-]*)")


class Keyword:
    """Keyword indicating the stability/visibility of a package on various architectures"""

    def accepts(self, _other: "Keyword") -> bool:
        """
        Returns true if and only if this keyword accepts the other keyword
        This is not necessarily true in reverse (~arch accepts arch, but not vice-versa)
        """
        raise NotImplementedError("This must be implemented for keyword subclasses")

    def masks(self, _arch: str, _arch_ver: Optional[Version] = None) -> bool:
        """
        Returns true if and only if this keyword masks the other keyword
        """
        raise NotImplementedError("This must be implemented for keyword subclasses")


def parse_keyword(inputstr: str) -> Keyword:
    """
    Converts the string representation of a Keyword

    The Keyword class itself is just an abstract class. This function, or the
    WildcardKeyword and NamedKeyword classes, shuold be used to instantiate keywords.
    """
    try:
        return WildcardKeyword(inputstr)
    except ValueError:
        return NamedKeyword.from_string(inputstr)


class WildcardKeyword(Keyword, Enum):
    """Wildcards used to control package visiblily on multiple architectures"""

    ALWAYS = "**"
    """Package is always visible"""
    TESTING = "~*"
    """Package is visible if testing on any architecture"""
    STABLE = "*"
    """Package is visible if stable on any architecture"""
    MASKED = "-*"
    """Package is masked on all architectures not otherwise listed"""

    def __str__(self):
        return self.value

    def masks(self, _arch: str, _arch_ver: Optional[Version] = None) -> bool:
        if self == WildcardKeyword.MASKED:
            return True
        return False

    def accepts(self, other: Keyword) -> bool:
        if WildcardKeyword.MASKED in (self, other):
            return False
        if WildcardKeyword.ALWAYS in (self, other):
            return True
        if isinstance(other, WildcardKeyword):
            if self == WildcardKeyword.STABLE:
                return other == WildcardKeyword.STABLE
            if self == WildcardKeyword.TESTING:
                return other == WildcardKeyword.TESTING
        elif isinstance(other, NamedKeyword):
            if self == WildcardKeyword.STABLE:
                return other.stability in (Stability.STABLE, Stability.TESTING)
            if self == WildcardKeyword.TESTING:
                return other.stability == Stability.TESTING

        raise NotImplementedError()


@dataclass
class NamedKeyword(Keyword):
    """
    Keyword referring to a specific architecture

    (and optionally specific versions of that architecture)
    """

    name: str
    stability: Stability
    versions: Optional[VersionRange]

    @classmethod
    def from_string(cls, inputstr: str) -> "NamedKeyword":
        """
        Constructs a keyword from the string representation

        The string representation should consist of the keyword name,
        optionally preceeded by a ~ or - to indicate testing/masked keywords
        and optionally followed by a comma-separated list of versions enclosed in braces

        E.g. ~openmw{==0.48}
        """
        if inputstr[0] == "~":
            stability = Stability.TESTING
            inputstr = inputstr[1:]
        elif inputstr[0] == "-":
            stability = Stability.MASKED
            inputstr = inputstr[1:]
        else:
            stability = Stability.STABLE

        result = re.split(_kw_name_re, inputstr, maxsplit=1)
        if len(result) < 3:
            raise ValueError(f"Invalid Keyword '{inputstr}'!")

        _, name, versions = result

        if versions:
            if (
                not versions.startswith("{") or not versions.endswith("}")
            ) and versions[0].isnumeric():
                raise ValueError(
                    f"Missing braces around keyword versions in keyword {inputstr}"
                )
            if not versions.startswith("{"):
                raise ValueError(
                    f"Trailing characters {versions} of keyword {inputstr} "
                    "cannot be part of a valid keyword name"
                )
            versions = VersionRange(versions.strip("{}"), external=True)
        else:
            versions = None
        return cls(name, stability, versions)

    def __str__(self):
        result = self.name
        if self.stability == Stability.TESTING:
            result = "~" + result
        elif self.stability == Stability.MASKED:
            result = "-" + result
        if self.versions:
            result += "{" + str(self.versions) + "}"
        return result

    def masks(self, arch: str, arch_ver: Optional[Version] = None) -> bool:
        if self.stability != Stability.MASKED:
            return False

        if arch != self.name:
            return False

        # If the mask does not specify a version, it always applies
        if self.versions is None:
            return True
        # If the mask specifies a version, but no version is provided, assume it doesn't apply
        # This is a situation which should usually not occur,
        # as packages should only provide a version if versioning is set up
        elif arch_ver is None:
            return False

        # Otherwise, the mask applies only if the version is within the masked range
        return arch_ver in self.versions

    def accepts(self, other: Keyword) -> bool:
        if isinstance(other, NamedKeyword):
            if other.name != self.name:
                return False

            # If one is masked, do not accept
            if (
                other.stability == Stability.MASKED
                and self.stability != Stability.MASKED
            ):
                return False
            if (
                self.stability == Stability.MASKED
                and other.stability != Stability.MASKED
            ):
                return False

            # Stable does not accept testing, but testing accepts stable
            if (
                other.stability == Stability.TESTING
                and self.stability == Stability.STABLE
            ):
                return False

            # If one or the other does not specify a version, there is overlap
            if other.versions is None or self.versions is None:
                return True

            # Otherwise, there is only overlap if the versions overlap
            return bool(self.versions & other.versions)

        elif isinstance(other, WildcardKeyword):
            return other.accepts(self)

        raise NotImplementedError()


def _user_package_accept_keywords_path() -> str:
    return os.path.join(env.prefix().CONFIG_DIR, "package.accept_keywords")


def add_keyword(
    atom: QualifiedAtom, keyword: Keyword, *, protect_file: Optional[str] = None
):
    """Adds keyword for the given atom. Does not modify any existing keywords."""
    keyword_file = protect_file or _user_package_accept_keywords_path()

    add_flag(keyword_file, atom, str(keyword))


def remove_keyword(atom: QualifiedAtom, keyword: Keyword):
    keyword_file = os.path.join(env.prefix().CONFIG_DIR, "package.accept_keywords")
    remove_flag(keyword_file, atom, str(keyword))


def get_global_keywords() -> List[Keyword]:
    return [parse_keyword(token) for token in get_config()["ACCEPT_KEYWORDS"]]


def get_keywords(atom: QualifiedAtom) -> List[Keyword]:
    """Returns the keywords for a particular package"""
    keyword_file = os.path.join(env.prefix().CONFIG_DIR, "package.accept_keywords")
    return [
        parse_keyword(token) for token in get_flags(keyword_file, atom)
    ] + get_global_keywords()


def _accepts(accept_keywords: Iterable[Keyword], keywords: Iterable[Keyword]):
    # FIXME: This description is rediculous.
    """
    Returns true if and only if at least one keyword in accept_keywords
    accepts at least one of the keywords in keywords

    You must not pass a consumable iterator to this method, as it will iterate
    over them multiple times.
    """
    for accept_keyword in accept_keywords:
        if isinstance(accept_keyword, WildcardKeyword):
            if accept_keyword == WildcardKeyword.STABLE:
                # Accepts stable on all architectures. Valid if keywords contains
                # a stable keyword for any keyword
                if any(
                    keyword.stability == Stability.STABLE
                    for keyword in keywords
                    if isinstance(keyword, NamedKeyword)
                ):
                    return True
            elif accept_keyword == WildcardKeyword.TESTING:
                # Accepts testing on all architectures. Valid if keywords contains
                # either testing or stable for any keyword
                if any(
                    isinstance(keyword, NamedKeyword)
                    and keyword.stability == Stability.TESTING
                    for keyword in keywords
                ):
                    return True
            elif accept_keyword == WildcardKeyword.ALWAYS:
                # Accepts any configuration
                return True
        elif isinstance(accept_keyword, NamedKeyword):
            if any(accept_keyword.accepts(keyword) for keyword in keywords):
                return True

    return WildcardKeyword.ALWAYS in keywords


def get_stability(package: Pybuild) -> Stability:
    """Returns the stability for the user's current configuration of the given package"""
    accepts_keywords = get_keywords(package.ATOM)
    keywords = list(map(parse_keyword, package.KEYWORDS))

    is_unmasked = False
    for atom in get_unmasked().get(package.CPN, []):
        if atom_sat(atom, package.ATOM):
            is_unmasked = True
    arch_ver = get_config().get("ARCH_VERSION")
    return _get_stability(
        accepts_keywords,
        keywords,
        get_config()["ARCH"],
        Version(arch_ver) if arch_ver else None,
        is_unmasked,
    )


def _get_stability(
    accepts_keywords: List[Keyword],
    keywords: List[Keyword],
    arch: str,
    arch_ver: Optional[Version] = None,
    is_unmasked: bool = False,
) -> Stability:
    # Maked named keywords take priority. To override, you need to use package.unmask
    if not is_unmasked:
        if any(
            keyword.masks(arch, arch_ver)
            for keyword in keywords
            if isinstance(keyword, NamedKeyword)
        ):
            return Stability.MASKED

    # Note: if a testing keyword is in accepts_keywords,
    # we treat packages with matching testing keywords as stable
    if _accepts(accepts_keywords, keywords):
        return Stability.STABLE

    for keyword in accepts_keywords:
        # Stable keyword implies testing keyword
        if isinstance(keyword, NamedKeyword):
            if keyword.stability == Stability.STABLE:
                testing_keyword = NamedKeyword(
                    keyword.name, Stability.TESTING, keyword.versions
                )
                if any(testing_keyword.accepts(keyword) for keyword in keywords):
                    return Stability.TESTING

    if not is_unmasked:
        if any(
            keyword.masks(arch, arch_ver)
            for keyword in keywords
            if isinstance(keyword, WildcardKeyword)
        ):
            return Stability.MASKED

    # Untested
    return Stability.UNTESTED
