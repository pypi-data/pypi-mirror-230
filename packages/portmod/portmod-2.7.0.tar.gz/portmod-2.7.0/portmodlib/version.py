# Copyright 2019-2023 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Match, Optional, Tuple

ext_ver_re = (
    r"(?P<NUMERIC>(\d+)(\.\d+)*)"
    r"(?P<LETTER>[a-z])?"
    # Note: The p suffix is disabled for external versions
    r"(?P<SUFFIX>((_(pre|beta|alpha|rc)\d*)*))"
)
ver_re = (
    r"(e(?P<EPOCH>\d+)-)?"
    r"(?P<NUMERIC>(\d+)(\.\d+)*)"
    r"(?P<LETTER>[a-z])?"
    r"(?P<SUFFIX>((_(pre|p|beta|alpha|rc)\d*)*))"
    r"(-r(?P<REV>\d+))?"
)
_ver_re = re.compile("^" + ver_re + "$")
_ext_ver_re = re.compile("^" + ext_ver_re + "$")


@dataclass
class Version:
    """
    A package version

    This class should be treated as immutable
    """

    numeric: List[str]
    suffixes: List[str]
    epoch: Optional[int] = None
    letter: str = ""
    revision: Optional[int] = None

    def __init__(
        self,
        version: str,
        *,
        _match: Optional[Match[str]] = None,
        external: bool = False,
    ):
        """
        args:
            version: A string representation of the version to be parsed
            external: If true, epochs and revisions  will be disabled, for use with upstream versions.
        """
        if not _match:
            if external:
                match = _ext_ver_re.match(version)
            else:
                match = _ver_re.match(version)
            if match is None:
                raise ValueError(f"Version {version} could not be parsed")
        else:
            match = _match

        if not external and match.group("EPOCH"):
            self.epoch = int(match.group("EPOCH"))
        self.numeric = list(str(match.group("NUMERIC")).split("."))
        self.letter = match.group("LETTER") or ""
        suffixes = match.group("SUFFIX")
        if suffixes:
            self.suffixes = suffixes.lstrip("_").split("_")
        else:
            self.suffixes = []
        if not external and match.group("REV"):
            self.revision = int(match.group("REV"))

    def __str__(self) -> str:
        return self.display()

    def display(self, *, revision: bool = True, epoch: bool = True) -> str:
        return (
            (f"e{self.epoch}-" if self.epoch is not None and epoch else "")
            + ".".join(self.numeric)
            + (self.letter or "")
            + ("_" + "_".join(self.suffixes) if self.suffixes else "")
            + (f"-r{self.revision}" if self.revision is not None and revision else "")
        )

    def _normalize_numeric(self) -> List[str]:
        return list(map(lambda x: x.rstrip("0"), self.numeric))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Version):
            return self.compare(other)
        return False

    def compare(self, other: "Version", *, ignore_revision=False) -> bool:
        # Note: versions with different numbers of numeric components are not equivalent
        # according to the PMS, even if the extra components are trailing 0s.
        return (
            self.epoch == other.epoch
            and self._normalize_numeric() == other._normalize_numeric()
            and self.letter == other.letter
            and self.suffixes == other.suffixes
            and (self.revision == other.revision or ignore_revision)
        )

    def __ge__(self, other: "Version") -> bool:
        return self > other or self == other

    def __gt__(self, other: "Version") -> bool:
        return self.greater(other)

    def greater(self, other: "Version", ignore_extra_components=False) -> bool:
        # Compare epochs
        if (self.epoch or 0) > (other.epoch or 0):
            return True
        if (self.epoch or 0) < (other.epoch or 0):
            return False

        if int(self.numeric[0]) > int(other.numeric[0]):
            return True
        if int(self.numeric[0]) < int(other.numeric[0]):
            return False

        # Compare numeric components
        for index, val in enumerate(self.numeric[1:], start=1):
            if index >= len(other.numeric):
                if ignore_extra_components:
                    return False
                else:
                    return True
            if val.startswith("0") or other.numeric[index].startswith("0"):
                # If either starts with a leading 0, strip trailing zeroes and
                # compare lexicographically.
                # I.e. 01 should always come before 10
                my_stripped = val.rstrip("0")
                other_stripped = other.numeric[index].rstrip("0")
                if my_stripped > other_stripped:
                    return True
                if my_stripped < other_stripped:
                    return False
            else:
                if int(val) > int(other.numeric[index]):
                    return True
                if int(val) < int(other.numeric[index]):
                    return False
        if len(other.numeric) > len(self.numeric):
            return False

        if ignore_extra_components:
            # Any further
            return False

        # Compare letter components
        if self.letter > other.letter:
            return True
        if self.letter < other.letter:
            return False

        # Compare suffixes
        for a_s, b_s in zip(self.suffixes, other.suffixes):
            asm = re.match(r"(?P<S>[a-z]+)(?P<N>\d+)?", a_s)
            bsm = re.match(r"(?P<S>[a-z]+)(?P<N>\d+)?", b_s)
            assert asm
            assert bsm
            a_suffix = asm.group("S")
            b_suffix = bsm.group("S")
            a_suffix_num = int(asm.group("N") or "0")
            b_suffix_num = int(bsm.group("N") or "0")
            if a_suffix == b_suffix:
                if b_suffix_num > a_suffix_num:
                    return False
                if a_suffix_num > b_suffix_num:
                    return True
            elif _suffix_gt(a_suffix, b_suffix):
                return True
            else:
                return False
        # More suffixes implies an earlier version,
        # except when the suffix is _p
        if len(self.suffixes) > len(other.suffixes):
            if self.suffixes[len(other.suffixes)].startswith("p"):
                return True
            return False
        if len(self.suffixes) < len(other.suffixes):
            if other.suffixes[len(self.suffixes)].startswith("p"):
                return False
            return True

        # Compare revisions
        if (self.revision or 0) > (other.revision or 0):
            return True
        if (self.revision or 0) < (other.revision or 0):
            return False

        # Equal
        return False


# Fixme: ^= or ~= for partial version matching? (e.g. cargo)
# Or implicit if an operator isn't provided, and wildcards?
# E.g. 2.5 is equivalent to 2.5.*,
# E.g. 2 is equivalent to 2.*, etc.
_range_op_re = r"^(!=|<=|>=|==|<|>)?"


class Operator(Enum):
    Eq = "=="
    Neq = "!="
    Lt = "<"
    Gt = ">"
    Leq = "<="
    Geq = ">="


@dataclass
class VersionRange:
    """
    A comma-separated range of versions which apply simultaneously.

    A version is considered in the range if it matches every component.

    E.g.
    "3.0" is in ">=1.0,!=2.0", but "2.0" and "0.1" are not.

    This class should be treated as immutable
    """

    versions: List[Tuple[Optional[Operator], Version]]

    def __init__(self, inputstr: str, external: bool = False):
        def parse_elem(string: str):
            result = re.split(_range_op_re, string, maxsplit=1)
            if len(result) < 3:
                raise ValueError(f"Version {string} does not begin with an operator!")
            _, op, version = result
            if not op and version.endswith("*"):
                return None, Version(version[:-1], external=external)
            elif not op:
                raise ValueError(
                    f"Version {string} must either begin with an operator, or end with a wildcard"
                )
            else:
                return Operator(op), Version(version, external=external)

        self.versions = [parse_elem(elem) for elem in inputstr.split(",")]

    def __contains__(self, other: Any):
        if isinstance(other, Version):
            for op, version in self.versions:
                if op:
                    if (
                        (op == Operator.Eq and other != version)
                        or (op == Operator.Neq and other == version)
                        or (op == Operator.Lt and other >= version)
                        or (op == Operator.Gt and other <= version)
                        or (op == Operator.Leq and other > version)
                        or (op == Operator.Geq and other < version)
                    ):
                        return False
                else:
                    # Wildcard
                    # e.g. 1*
                    print(
                        other,
                        version,
                        other < version,
                        version.greater(other, ignore_extra_components=True),
                    )
                    if other < version:
                        return False
                    if other.greater(version, ignore_extra_components=True):
                        return False
            return True
        raise NotImplementedError()

    def _get_bounds(self):
        upper_bound = lower_bound = None
        upper_inclusive = lower_inclusive = None

        for op, version in self.versions:
            if op is None:
                raise NotImplementedError()
            if op == Operator.Lt and (upper_bound is None or version > upper_bound):
                upper_bound = version
                upper_inclusive = False
            elif op == Operator.Leq and (upper_bound is None or version >= upper_bound):
                upper_bound = version
                upper_inclusive = True
            if op == Operator.Gt and (lower_bound is None or version < lower_bound):
                lower_bound = version
                lower_inclusive = False
            elif op == Operator.Geq and (lower_bound is None or version <= lower_bound):
                lower_bound = version
                lower_inclusive = True

        if upper_bound and lower_bound:
            # E.g. >2.0,<1.0
            if upper_bound < lower_bound:
                raise ValueError("Upper bound is lower than lower bound!")

            # Equal, but one of the inequalities isn't inclusive
            # E.g. >1.0,<1.0 or >=1.0,<1.0
            if (
                not upper_inclusive or not lower_inclusive
            ) and upper_bound == lower_bound:
                raise ValueError("Upper bound is lower than lower bound!")
        return upper_bound, upper_inclusive, lower_bound, lower_inclusive

    def __and__(self, other: Any):
        if not isinstance(other, VersionRange):
            raise NotImplementedError()

        for op, version in self.versions:
            # If there is an ==, it must be in the other range
            if op == Operator.Eq and version not in other:
                return False
            # If there is a !=, it must not be in the other range
            elif op == Operator.Neq and version in other:
                return False

        # Because range components combine with AND, there are two possibilities
        # 1. Only one inequality, allowing all versions greater or less than a certain version
        # 2. Two inequalities (or more than two where some are redundant), allowing a range between two versions
        try:
            (
                upper_bound,
                upper_inclusive,
                lower_bound,
                lower_inclusive,
            ) = self._get_bounds()
            (
                other_upper_bound,
                other_upper_inclusive,
                other_lower_bound,
                other_lower_inclusive,
            ) = other._get_bounds()
        except ValueError:
            # Contradiction in the bounds, one of the ranges is empty
            return False

        # Cases 1 and 2:
        # E.g. <1.0 and >2.0
        if upper_bound and other_lower_bound and upper_bound < other_lower_bound:
            return False
        # E.g. <1.0 and >1.0
        if (
            upper_bound
            and other_lower_bound
            and (not upper_inclusive or not other_lower_inclusive)
            and upper_bound <= other_lower_bound
        ):
            return False
        # E.g. >2.0 and <1.0
        if lower_bound and other_upper_bound and lower_bound > other_upper_bound:
            return False
        # E.g. >1.0 and <1.0
        if (
            lower_bound
            and other_upper_bound
            and (not lower_inclusive or not other_upper_inclusive)
            and lower_bound >= other_upper_bound
        ):
            return False

        return True

    def __str__(self):
        return ",".join(
            (f"{operator.value}{version}" if operator else f"{version}.*")
            for operator, version in self.versions
        )


def _suffix_gt(a_suffix: str, b_suffix: str) -> bool:
    """Returns true iff a_suffix > b_suffix"""
    suffixes = ["alpha", "beta", "pre", "rc", "p"]
    return suffixes.index(a_suffix) > suffixes.index(b_suffix)
