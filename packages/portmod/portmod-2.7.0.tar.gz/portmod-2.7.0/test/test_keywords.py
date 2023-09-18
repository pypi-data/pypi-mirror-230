# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import pytest

from portmod.repo.keywords import NamedKeyword, Stability
from portmod.repo.keywords import WildcardKeyword as W
from portmod.repo.keywords import _accepts as accepts
from portmod.repo.keywords import _get_stability
from portmodlib.version import Version

from .env import setup_env, tear_down_env

N = NamedKeyword.from_string


@pytest.fixture(scope="module", autouse=True)
def setup():
    """
    Sets up and tears down the test environment
    """
    dictionary = setup_env("test")
    yield dictionary
    tear_down_env()


def test_stable_visibility():
    assert accepts([N("test")], [N("test")])
    assert not accepts([N("test")], [N("test2")])
    assert accepts([N("~test")], [N("test")])
    # See note: https://wiki.gentoo.org/wiki/KEYWORDS
    # ~* does not imply *
    assert not accepts([W.TESTING], [N("test")])
    assert accepts([W.STABLE], [N("test")])


def test_wild_stable_visibility():
    assert not accepts([W.STABLE], [])

    assert accepts([N("test"), W.STABLE], [N("test2")])
    assert accepts([N("~test"), W.STABLE], [N("test2")])
    assert accepts([W.STABLE], [N("test")])
    assert accepts([N("~test"), W.STABLE], [N("test")])


def test_wild_testing_visibility():
    assert not accepts([W.TESTING], [])
    # See note: https://wiki.gentoo.org/wiki/KEYWORDS
    # ~* does not imply *
    assert not accepts([W.TESTING], [N("test")])
    assert accepts([W.TESTING], [N("~test")])
    assert not accepts([N("~test"), W.TESTING], [N("test2")])
    assert accepts([N("~test"), W.TESTING], [N("~test2")])
    assert not accepts([N("test"), W.TESTING], [N("test2")])
    assert accepts([N("test"), W.TESTING], [N("~test2")])


def test_testing_visibility():
    assert not accepts([N("test")], [N("~test")])
    assert accepts([N("~test")], [N("~test")])
    assert accepts([W.TESTING], [N("~test")])
    assert not accepts([W.STABLE], [N("~test")])


def test_wild_visibility():
    assert accepts([W.ALWAYS], [N("test")])
    assert accepts([W.ALWAYS], [N("~test")])
    assert accepts([W.ALWAYS], [])


def test_untested_visibility():
    assert not accepts([N("test")], [])
    assert not accepts([N("~test")], [])
    assert accepts([W.ALWAYS], [])


def test_versions():
    assert accepts([N("test{==1.0}")], [N("test")])
    assert accepts([N("test{==1.0}")], [N("test{>=0.1}")])
    assert accepts([N("test{==1.0}")], [N("test{<2.1,>=1.0}")])

    assert accepts([N("test{>=1.0,<2.0}")], [N("test{<2.1,>=1.0}")])
    assert accepts([N("test{>=1.0,<2.0}")], [N("test{>=1.5}")])
    assert not accepts([N("test{>=1.0,<2.0}")], [N("test{>=2.0}")])


def test_valid_keyword_versions():
    """Tests that keyword versions allow external versions only"""
    N("test{==1.0.0_alpha2_pre1}")

    with pytest.raises(ValueError):
        N("test{==e1-1.0.0_alpha2_pre1}")
    with pytest.raises(ValueError):
        N("test{==1.0.0_alpha2_pre1-r2}")


def test_multiple_versions():
    assert accepts([N("test{==1.0}")], [N("test"), N("-test{<1.0}")])
    assert accepts([N("test{==1.0}")], [N("test{>=1.0}"), N("-test{<1.0}")])
    assert not accepts([N("test{==0.1}")], [N("test{>=1.0}"), N("-test{<1.0}")])


def test_version_overlap():
    """Tests that masked takes priority over stable, and stable takes priority over testing"""
    arch = "test"
    ver = Version("1.0")
    assert (
        _get_stability([N("test{==1.0}")], [N("-test{<1.0}"), N("test")], arch, ver)
        == Stability.STABLE
    )
    ver = Version("0.1")
    assert (
        _get_stability([N("test{==0.1}")], [N("-test{<1.0}"), N("test")], arch, ver)
        == Stability.MASKED
    )

    assert (
        _get_stability([N("test{==0.1}")], [N("~test{<1.0}"), N("test")], arch, ver)
        == Stability.STABLE
    )


def test_version_overlap_wildcards():
    """Tests that named keywords take priority over wildcards"""
    ver = Version("1.0")
    assert (
        _get_stability([N("test{==1.0}")], [W("-*"), N("test")], "test", ver)
        == Stability.STABLE
    )
    ver = Version("0.1")
    assert (
        _get_stability([N("test2{==0.1}")], [W("-*"), N("test")], "test2", ver)
        == Stability.MASKED
    )
    assert (
        _get_stability([N("test{==0.1}")], [W("~*"), N("test")], "test", ver)
        == Stability.STABLE
    )
    assert (
        _get_stability(
            [N("test2{==0.1}")], [W("~*"), N("test"), N("~test")], "test2", ver
        )
        == Stability.TESTING
    )
    assert (
        _get_stability(
            [N("test{==0.1}")], [N("~test"), W("*"), N("test2")], "test", ver
        )
        == Stability.STABLE
    )
    assert (
        _get_stability(
            [N("test{==0.1}"), W("*")], [N("~test"), N("test2")], "test", ver
        )
        == Stability.STABLE
    )


def test_get_stability():
    arch = "test"
    assert _get_stability([N("test")], [N("test")], arch) == Stability.STABLE
    assert _get_stability([N("test")], [N("~test")], arch) == Stability.TESTING
    assert _get_stability([N("test")], [], arch="test") == Stability.UNTESTED
    assert _get_stability([N("test")], [N("-test")], arch) == Stability.MASKED

    assert _get_stability([N("test"), W.STABLE], [N("test2")], arch) == Stability.STABLE
    assert (
        _get_stability([N("test"), W.TESTING], [N("~test2")], arch) == Stability.STABLE
    )
    assert _get_stability([N("test")], [N("test2"), W.MASKED], arch) == Stability.MASKED


def test_get_stability_versioned():
    arch = "test"
    ver = Version("1.0.0")
    assert (
        _get_stability([N("test{==1.0}")], [N("test")], arch, ver) == Stability.STABLE
    )
    assert (
        _get_stability([N("test{==1.0.0}")], [N("test{>=1.0}")], arch, ver)
        == Stability.STABLE
    )
    assert (
        _get_stability([N("test{==0.1.0}")], [N("test{>=1.0}")], arch, Version("0.1.0"))
        == Stability.UNTESTED
    )
    # Masked keywords always take priority
    assert (
        _get_stability(
            [N("test{==0.1.0}")],
            [N("test"), N("-test{==0.1.0}")],
            arch,
            Version("0.1.0"),
        )
        == Stability.MASKED
    )
    # Otherwise, as long as any keyword is stable, the package is stable
    # Even if a testing keyword also matches
    assert (
        _get_stability(
            [N("test{==0.1.0}")], [N("~test"), N("test{<1.0}")], arch, Version("0.1.0")
        )
        == Stability.STABLE
    )


def test_get_stability_versioned_acceptall():
    """Tests that checking the stability of packages when accepting all versions is consistent

    This is used by package validation when checking the stability of dependencies to ensure
    that at least some version has the desired stability.
    """
    arch = "test"
    ver = Version("1.0.0")
    assert _get_stability([N("test")], [N("test{<1.0}")], arch, ver) == Stability.STABLE
    assert (
        _get_stability([N("test")], [N("test{==0.1}")], arch, ver) == Stability.STABLE
    )
    assert (
        _get_stability([N("test")], [N("~test{==0.0.1}")], arch, ver)
        == Stability.TESTING
    )
    assert (
        _get_stability([N("test")], [N("~test{==0.0.1}"), N("-test{0.1*}")], arch, ver)
        == Stability.TESTING
    )
    assert (
        _get_stability([N("test")], [N("~test{==0.0.1}"), N("-test")], arch, ver)
        == Stability.MASKED
    )
