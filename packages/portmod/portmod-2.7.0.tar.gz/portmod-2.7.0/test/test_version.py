# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Tests the version comparison system
"""

import pytest

from portmodlib.version import Version, VersionRange


def test_simple_version():
    """Tests extremely simple version comparison"""
    v_b = "2.0"
    v_a = "1.0"
    assert max([v_a, v_b]) == v_b
    gt("2.0.0", "2.0")


def gt(ver1, ver2):
    """Tests that ver1 is considered greater than ver2"""
    ver1 = Version(ver1)
    ver2 = Version(ver2)
    assert ver1 > ver2
    assert not ver2 > ver1
    assert max([ver1, ver2]) == ver1
    assert max([ver2, ver1]) == ver1


def test_suffix():
    """Tests that suffixed versions come before full versions"""
    assert max(
        map(Version, ["2.0_alpha", "2.0_beta", "2.0_pre", "2.0_rc", "2.0"])
    ) == Version("2.0")
    gt("2.0", "2.0_alpha1")
    gt("2.0.0_alpha1", "2.0")


def test_suffix_p():
    """Tests that p suffixed versions come after full versions"""
    gt("2.0_p1", "2.0")
    gt("2.0_alpha_p1", "2.0_alpha")


def test_suffix_endings():
    """Tests that p suffixed versions with integer endings order correctly"""
    gt("2.0_p2", "2.0_p1")
    gt("2.0_alpha2", "2.0_alpha1")
    gt("2.0_beta1", "2.0_alpha2")
    gt("2.0_alpha1", "2.0_alpha")
    gt("2.0_alpha1_beta2", "2.0_alpha")
    gt("2.0_alpha", "2.0_alpha_beta2")


def test_letter():
    """
    Tests that letter versions come after non-letter versions, increase in order
    and take precedence over suffixes, but not numeric components
    """
    gt("2.0a", "2.0")
    gt("2.0b", "2.0a")
    gt("2.0b_alpha", "2.0a")
    gt("2.1a", "2.0b")


def test_revision():
    """
    Tests that revisions have the lowest precedence and increase in order
    """
    gt("2.0-r1", "2.0")
    gt("2.0-r2", "2.0-r1")
    gt("2.0a-r1", "2.0-r2")
    gt("2.0_beta-r1", "2.0_alpha-r2")


def test_different_version_lengths():
    """
    Tests that having more version components is considered a greater version if the numbers are otherwise equal
    """
    gt("2.0.1", "2.0")
    gt("2.1", "2.0.1")
    gt("2.0.1_alpha", "2.0_p1-r1")


def test_different_epochs():
    """
    Tests that packages with a larger epoch are considered a greater version
    """
    gt("e1-2.0", "2.0")
    gt("e1-0.1", "2.0")
    gt("e2-0.1", "e1-2.0.0")
    gt("e1-2.1", "e1-2")


def test_leading_zeroes():
    """
    Tests that versions with leading zeroes are compared lexicographically
    """
    gt("2.1", "2.01")
    gt("2.10", "2.9")
    gt("2.1", "2.09")
    gt("2", "1.09")
    gt("2.09", "2")


def test_invalid():
    """
    Tests that invalid versions do not parse
    """
    with pytest.raises(ValueError):
        Version("1.")

    with pytest.raises(ValueError):
        Version("1.0-2")

    with pytest.raises(ValueError):
        Version("1.a")


def test_external():
    """Tests that epochs and revisions are considered invalid in external versions"""
    Version("1.0.0_alpha2_pre1_alpha", external=True)

    Version("1.0.0_beta2_pre1", external=True)
    Version("e1-1.0.0_beta2_pre1-r1")
    with pytest.raises(ValueError):
        Version("1.0.0_beta2_pre1-r1", external=True)
    with pytest.raises(ValueError):
        Version("e1-1.0.0_beta2_pre1", external=True)
    with pytest.raises(ValueError):
        Version("1.0.0_beta2_p1", external=True)


def test_range():
    assert Version("1.0") in VersionRange("==1.0")
    assert Version("1.0") in VersionRange(">=1.0")
    assert Version("1.0") in VersionRange("<=1.0")
    assert Version("1.0") not in VersionRange("!=1.0")

    assert Version("1.0") not in VersionRange(">1.0")
    assert Version("1.0") not in VersionRange("<1.0")
    assert Version("1.1") in VersionRange(">1.0")
    assert Version("0.1") in VersionRange("<1.0")


def test_range_multiple():
    assert Version("1.0") in VersionRange(">=1.0,<2.0")
    assert Version("1.1") in VersionRange(">=1.0,<2.0")
    assert Version("2.0") not in VersionRange(">=1.0,<2.0")
    assert Version("1.0") not in VersionRange(">1.0,<2.0")
    assert Version("1.0") not in VersionRange("<1.0,>2.0")
    # Ranges containing nothing are valid, but all versions should not be in the range
    assert Version("0") not in VersionRange("<1.0,>2.0")
    assert Version("3") not in VersionRange("<1.0,>2.0")


def test_range_intersection():
    assert VersionRange(">=1.0,<2.0") & VersionRange("==1.0")
    assert VersionRange(">=1.0,<2.0") & VersionRange(">1.0")
    assert VersionRange(">=1.0,<2.0") & VersionRange("<2.0")
    assert VersionRange(">=1.0,<2.0") & VersionRange("<=1.0")
    assert not VersionRange(">=1.0,<2.0") & VersionRange("<1.0")

    assert VersionRange(">=1.0,>1.0") & VersionRange("==1.0")
    assert VersionRange(">1.0,>=1.0") & VersionRange("==1.0")

    assert not VersionRange(">2.0,<1.0") & VersionRange("==1.0")
    assert not VersionRange(">=2.0,<=1.0") & VersionRange("==1.0")

    assert not VersionRange(">1.0,<1.0") & VersionRange("==1.0")
    assert not VersionRange(">=1.0,<1.0") & VersionRange("==1.0")
    assert not VersionRange(">1.0,<=1.0") & VersionRange("==1.0")
    assert VersionRange(">=1.0,<=1.0") & VersionRange("==1.0")
    assert not VersionRange(">1.0,<=1.0") & VersionRange("==1.0")
    assert not VersionRange(">=1.0,<1.0") & VersionRange("==1.0")


def test_range_wildcard():
    assert Version("1.0") in VersionRange("1*")
    assert Version("1.1") in VersionRange("1*")
    assert Version("2.0") not in VersionRange("1*")

    assert Version("1.0") not in VersionRange("1.2*")
    assert Version("1.1") not in VersionRange("1.2*")
    assert Version("1.2") in VersionRange("1.2*")
    assert Version("1.2.0") in VersionRange("1.2*")
    assert Version("1.2.1") in VersionRange("1.2*")
    # Pre-release versions are also in the range (See PMS)
    assert Version("1.2.0_alpha1") in VersionRange("1.2*")
    assert Version("1.2.0_beta1") in VersionRange("1.2*")
    assert Version("1.2.0_rc1") in VersionRange("1.2*")
    assert Version("1.2.0_pre1") in VersionRange("1.2*")

    assert Version("1.2.0_p1") in VersionRange("1.2*")
    assert Version("1.2.0_p1") in VersionRange("1.2.0_p*")
    assert Version("1.2.0") not in VersionRange("1.2.0_p*")

    assert Version("1.3a") not in VersionRange("1.2*")
    assert Version("2.0") not in VersionRange("1.2*")


def test_invalid_range_operators():
    VersionRange("1.0*")
    with pytest.raises(ValueError):
        VersionRange("1.0.*")
    with pytest.raises(ValueError):
        VersionRange("*1.0")
