# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Tests file master detection
"""

import os

import pytest

from portmod.globals import env
from portmodlib.masters import get_masters

from .env import setup_env, tear_down_env
from .merge import merge


@pytest.fixture(scope="module", autouse=True)
def setup_repo():
    """sets up and tears down test environment"""
    yield setup_env("test")
    tear_down_env()


def test_masters_esp():
    """Tests that we detect esp masters properly"""

    merge(["=test/quill-of-feyfolken-2.0.2"])
    path = os.path.join(
        env.prefix().ROOT, "pkg", "test", "quill-of-feyfolken", "Quill of Feyfolken.esp"
    )
    masters = get_masters(path)
    assert len(masters) == 1
    assert "Morrowind.esm" in masters
