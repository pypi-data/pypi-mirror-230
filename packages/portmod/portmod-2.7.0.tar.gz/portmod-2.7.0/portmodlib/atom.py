# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import re
from typing import AbstractSet, Any, Dict, Optional, Set, TypeVar

from .functools import deprecated
from .version import Version, _suffix_gt, ver_re

"""
Module for handling package atoms

All atom classes defined in this module should be considered read-only.
Modification of an Atom object may have unexpected side-effects
"""

flag_re = r"[A-Za-z0-9][A-Za-z0-9+_-]*"
useflag_re = re.compile(r"^" + flag_re + r"$")
usedep_re = (
    r"(?P<prefix>[!-]?)(?P<flag>"
    + flag_re
    + r")(?P<default>(\(\+\)|\(\-\))?)(?P<suffix>[?=]?)"
)
_usedep_re = re.compile("^" + usedep_re + "$")

op_re = r"(?P<B>(!!))?(?P<OP>([<>]=?|[<>=~]))?"
cat_re = r"((?P<C>[A-Za-z0-9][A-Za-z0-9\-]*)/)?"
repo_re = r"(::(?P<R>[A-Za-z0-9_][A-Za-z0-9_-]*(::installed)?))?"
_atom_re = re.compile(
    op_re
    + cat_re
    + r"(?P<P>(?P<PN>[A-Za-z0-9+_-]+?)(-(?P<PV>"
    + ver_re
    + r"))?)"
    + repo_re
    + r"(\[(?P<USE>.*)\])?$"
)


class InvalidAtom(Exception):
    "Exception indicating an atom has invalid syntax"


class UnqualifiedAtom(Exception):
    """
    Exception indicating an atom, which was expected to be
    qualified with a category, has no category
    """

    def __init__(self, atom):
        self.atom = atom

    def __str__(self):
        return f"Atom {self.atom} was expected to have a category!"


T = TypeVar("T", bound="Atom")


class Atom(str):
    @property
    def CP(self) -> Optional[str]:
        """
        The category, package name and version, excluding revision

        E.g. ``base/example-suite-1.0``
        """
        if self.CPN is None:
            return None
        if self.version is not None:
            return self.CPN + "-" + self.version.display(revision=True)
        return self.CPN

    CPN: Optional[str]
    """
    The category and package name

    E.g. ``base/example-suite``
    """
    USE: Set[str] = set()
    """
    Use flags set on the atom.

    E.g. ``{minimal}`` in ``base/example-suite[minimal]``
    """

    @property
    def P(self) -> str:
        """
        The package name and version, excluding revision

        E.g. ``example-suite-1.0``
        """
        return (
            self.PN
            + "-"
            + (self.version.display(revision=False) if self.version is not None else "")
        )

    PN: str
    """
    The package name

    E.g. ``example-suite``
    """

    @property
    def PF(self) -> str:
        """
        The package name and version, including revision

        E.g. ``example-suite-1.0-r1``
        """
        return self.PN + (
            "-" + self.version.display() if self.version is not None else ""
        )

    @property
    def PV(self) -> Optional[str]:
        """
        The package version, not including revision

        E.g. ``1.0``
        """
        if self.version is not None:
            return self.version.display(revision=False)
        return None

    @property
    def PR(self) -> Optional[str]:
        """
        The package revision

        E.g. ``r1``
        """
        if self.version is not None:
            return f"r{self.version.revision}"
        return None

    C: Optional[str]
    """
    The package category

    E.g. ``base``
    """
    R: Optional[str]
    """
    The package repository

    E.g. ``openmw`` in base/example-suite-1.0-r1::openmw
    """
    OP: Optional[str]
    """
    An operator.

    See PMS section `8.2.6.1 <https://projects.gentoo.org/pms/7/pms.html#x1-760008.2.6.1>`_,
    noting that Weak blocks are not currently supported by Portmod, and blocks don't show up
    in OP (they instead set the BLOCK field).

    E.g. ``openmw`` in base/example-suite-1.0-r1::openmw
    """
    BLOCK: bool
    """
    If true, this atom is a blocker, referring to a package which must not be installed.

    E.g. ``!!base/example-suite``
    """

    @property
    def PVR(self) -> Optional[str]:
        """
        The version and revision

        E.g. 1.0-r1
        """
        if self.version is not None:
            return self.version.display(revision=True)
        return None

    @property
    def CPF(self) -> str:
        """
        The category, package name and version, including revision

        E.g. ``base/example-suite-1.0-r1``
        """
        if self.CPN is None:
            prefix = self.PN
        else:
            prefix = self.CPN
        if self.version is not None:
            return prefix + "-" + self.version.display(revision=True)
        return prefix

    version: Optional["Version"] = None
    """
    The package's version
    """

    _CACHE: Dict[str, Any] = {}

    def __init__(self, atom: str):
        if atom in self._CACHE:
            self.__dict__ = self._CACHE[atom]
            return

        match = _atom_re.match(atom)
        if not match:
            raise InvalidAtom("Invalid atom %s. Cannot parse" % (atom))

        if match.group("PN") and match.group("C"):
            self.CPN = match.group("C") + "/" + match.group("PN")
        else:
            self.CPN = None

        if match.group("USE"):
            self.USE = set(match.group("USE").split(","))
            for x in self.USE:
                m = _usedep_re.match(x)
                if not m:
                    raise InvalidAtom(
                        "Invalid use dependency {} in atom {}".format(atom, x)
                    )

        if match.group("PV"):
            self.version = Version("", _match=match)

        self.PN = match.group("PN")
        self.C = match.group("C")
        self.R = match.group("R")
        self.OP = match.group("OP")
        self.BLOCK = match.group("B") is not None

        if self.OP is not None and self.version is None:
            raise InvalidAtom(
                "Atom %s has a comparison operator but no version!" % (atom)
            )

        self._CACHE[atom] = self.__dict__

    def evaluate_conditionals(self, use: AbstractSet[str]) -> "Atom":
        """
        Create an atom instance with any USE conditionals evaluated.
        @param use: The set of enabled USE flags
        @return: an atom instance with any USE conditionals evaluated
        """
        tokens = set()

        for x in self.USE:
            m = _usedep_re.match(x)

            if m is not None:
                operator = m.group("prefix") + m.group("suffix")
                flag = m.group("flag")
                default = m.group("default")
                if default is None:
                    default = ""

                if operator == "?":
                    if flag in use:
                        tokens.add(flag + default)
                elif operator == "=":
                    if flag in use:
                        tokens.add(flag + default)
                    else:
                        tokens.add("-" + flag + default)
                elif operator == "!=":
                    if flag in use:
                        tokens.add("-" + flag + default)
                    else:
                        tokens.add(flag + default)
                elif operator == "!?":
                    if flag not in use:
                        tokens.add("-" + flag + default)
                else:
                    tokens.add(x)
            else:
                raise Exception("Internal Error when processing atom conditionals")

        atom = Atom(self)
        atom.USE = tokens
        return atom

    def strip_use(self: T) -> T:
        """Returns the equivalent of this atom with the USE dependencies removed"""
        return self.__class__(re.sub(r"\[.*\]", "", str(self)))

    def use(self, *flags: str):
        """returns atom with use flag dependency"""
        return self.__class__(f'{self}[{",".join(flags)}]')

    def with_category(self, category: str) -> "QualifiedAtom":
        return QualifiedAtom(
            (self.BLOCK and "!!" or "")
            + (self.OP or "")
            + category
            + "/"
            + self.PF
            + (self.R or "")
        )


class QualifiedAtom(Atom):
    """Atoms that include categories"""

    CP: str
    CPN: str
    CPF: str
    C: str

    def __init__(self, atom: str):
        super().__init__(atom)

        if not self.C:
            raise UnqualifiedAtom(atom)


class VAtom(QualifiedAtom):
    """Atoms that include version information"""

    PV: str
    PVR: str
    version: "Version"

    def __init__(self, atom: str):
        super().__init__(atom)
        if not self.version:
            raise InvalidAtom(f"Atom {atom} should include a version")


class FQAtom(VAtom):
    """Atoms that include all possible non-optional fields"""

    R: str

    def __init__(self, atom: str):
        super().__init__(atom)
        if not self.R:
            raise InvalidAtom(f"Atom {atom} should include a repository")


@deprecated(
    version="2.5",
    reason="Internal method which shouldn't be used. Will be removed in Portmod 2.7",
)
def suffix_gt(a_suffix: str, b_suffix: str) -> bool:
    """Returns true iff a_suffix > b_suffix"""
    return _suffix_gt(a_suffix, b_suffix)


@deprecated(
    version="2.5", reason="Use comparison operators with the Version class instead"
)
def version_gt(version1: str, version2: str) -> bool:
    """
    Version comparision function

    args:
        version1: A version string
        version2: Another version string

    returns:
        True if and only if version1 is greater than version2
    """
    return Version(version1) > Version(version2)


def atom_sat(specific: Atom, generic: Atom, *, ignore_name: bool = False) -> bool:
    """
    Determines if a fully qualified atom (can only refer to a single package)
    satisfies a generic atom
    """

    if not ignore_name:
        if specific.PN != generic.PN:
            # Mods must have the same name
            return False

        if generic.C and (generic.C != specific.C):
            # If para defines category, it must match
            return False

    if generic.R and (generic.R != specific.R):
        # If para defines repo, it must match
        return False

    if not generic.OP:
        # Simple atom, either one version or all versions will satisfy

        # Check if version is correct
        if generic.version and (
            not specific.version
            or not specific.version.compare(generic.version, ignore_revision=True)
        ):
            return False

        # Check if revision is correct
        if (
            generic.version
            and generic.version.revision
            and (
                not specific.version
                or specific.version.revision != generic.version.revision
            )
        ):
            return False
    elif generic.version and specific.version:
        equal = specific.version == generic.version
        verequal = specific.version.compare(generic.version, ignore_revision=True)
        lessthan = specific.version < generic.version
        greaterthan = specific.version > generic.version

        if generic.OP == "=":
            return equal
        if generic.OP == "~":
            return verequal
        if generic.OP == "<":
            return lessthan
        if generic.OP == "<=":
            return equal or lessthan
        if generic.OP == ">":
            return greaterthan
        if generic.OP == ">=":
            return equal or greaterthan

    return True
