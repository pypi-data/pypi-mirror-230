# Copyright 2022 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
import sys
from io import StringIO

import pytest

from portmod._cli.main import main
from portmod.cfg_protect import get_redirections, remove_redirection
from portmod.globals import env
from portmodlib.module_util import _add_redirection

from .env import setup_env, tear_down_env
from .merge import merge


@pytest.fixture(scope="module", autouse=True)
def setup():
    """
    Sets up and tears down the test environment
    """
    dictionary = setup_env("test")
    os.makedirs(env.prefix().CONFIG_PROTECT_DIR, exist_ok=True)
    yield dictionary
    tear_down_env()


def test_remove_redirections(setup):
    """
    Tests that removing redirections from the cfg_protect cache works
    """

    def write(file, data):
        with open(file, "w") as file:
            print(data, file=file)

    src1 = os.path.abspath("temp1")
    src2 = os.path.abspath("temp2")
    dst1 = os.path.abspath("temp3")
    dst2 = os.path.abspath("temp4")
    write(src1, "src1")
    write(src2, "src2")
    write(dst1, "dst1")
    write(dst2, "dst2")

    from portmodlib.globals import config_protect_dir

    assert config_protect_dir() == env.prefix().CONFIG_PROTECT_DIR

    _add_redirection(src1, dst1)
    _add_redirection(src2, dst2)
    assert get_redirections() == {dst1: [src1], dst2: [src2]}
    remove_redirection(src1, dst1)
    assert get_redirections() == {dst2: [src2]}
    remove_redirection(src2, dst2)
    assert get_redirections() == {}


def test_cfg_protect(setup):
    """
    Tests that file protected by CFG_PROTECT don't get their changes overwritten
    when the package is re-installed
    """
    merge(["=test/test-1.0-r1"])
    path = os.path.join(env.prefix().ROOT, "etc", "test")

    with open(path, "a", encoding="utf-8") as file:
        print("bar = baz", file=file)
    with open(path, encoding="utf-8") as file:
        contents = file.readlines()

    merge(["=test/test-1.0-r1"])

    with open(path, encoding="utf-8") as file:
        assert contents == file.readlines()

    # Since the file was the same when re-installed,
    # it shouldn't get added to the list of pending config file updates
    assert not list(get_redirections())

    merge(["=test/test-1.0-r1"], delete=True)
    merge
    os.remove(path)


def test_cfg_protect_changed(setup, monkeypatch):
    """
    Tests that files protected by CFG_PROTECT get installed as separate files
    and registered with cfg_protect when an update changes the file
    """
    merge(["=test/test-1.0-r1"])
    path = os.path.join(env.prefix().ROOT, "etc", "test")

    with open(path, "a", encoding="utf-8") as file:
        print("bar = baz", file=file)
    with open(path, encoding="utf-8") as file:
        contents = file.readlines()

    merge(["=test/test-2.0"])

    # File should not have been changed directly
    with open(path, encoding="utf-8") as file:
        assert contents == file.readlines()

    # Since the file was the same when re-installed,
    # it shouldn't get added to the list of pending config file updates
    redirections = list(get_redirections().items())
    assert redirections
    dst, srcs = redirections[0]
    assert dst == path
    assert srcs[0] == path + ".__cfg_protect__"
    with open(srcs[0], encoding="utf-8") as file:
        assert file.read() == "foo = baz\n"

    env.INTERACTIVE = True
    monkeypatch.setattr("sys.stdin", StringIO("y\n"))
    sys.argv = ["portmod", "test", "cfg-update"]
    main()

    with open(path, encoding="utf-8") as file:
        assert file.read() == "foo = baz\n"
    env.INTERACTIVE = False


def is_empty(path: str) -> bool:
    if not os.path.exists(path):
        return True

    with open(path, "r") as file:
        if file.read():
            return False

    return True


def test_cfg_protect_license(setup):
    """
    Tests that cfg_protect protects the package.accept_license file
    if installing in non-interactive mode
    """

    env.TESTING = False
    # Normally cfg_protect on configuration files is not enabled in testing mode
    assert is_empty(
        os.path.join(env.prefix().CONFIG_DIR, "package.accept_license")
    ), "package.accept_license should not exist at the start"

    # Configure will fail since license changes must be accepted
    with pytest.raises(SystemExit):
        merge(["test/test-eula"])

    assert is_empty(
        os.path.join(env.prefix().CONFIG_DIR, "package.accept_license")
    ), "package.accept_license should not contain anything after running the merge"

    assert os.path.exists(
        os.path.join(env.prefix().CONFIG_DIR, "package.accept_license.__cfg_protect__")
    )

    env.TESTING = True


def test_cfg_protect_keywords(setup):
    """
    Tests that cfg_protect protects the package.accept_keywords file
    if installing in non-interactive mode
    """

    env.TESTING = False
    # Normally cfg_protect on configuration files is not enabled in testing mode
    assert is_empty(
        os.path.join(env.prefix().CONFIG_DIR, "package.accept_keywords")
    ), "package.accept_keywords should not exist at the start"

    # Configure will fail since keyword changes must be accepted
    with pytest.raises(SystemExit):
        merge(["=test/test0-2.0_alpha"])

    assert is_empty(
        os.path.join(env.prefix().CONFIG_DIR, "package.accept_keywords")
    ), "package.accept_keywords should not contain anything after running the merge"

    assert os.path.exists(
        os.path.join(env.prefix().CONFIG_DIR, "package.accept_keywords.__cfg_protect__")
    )

    env.TESTING = True


def test_cfg_protect_use(setup):
    """
    Tests that cfg_protect protects the package.use file
    if installing in non-interactive mode
    """

    env.TESTING = False
    # Normally cfg_protect on configuration files is not enabled in testing mode
    assert is_empty(
        os.path.join(env.prefix().CONFIG_DIR, "package.use")
    ), "package.use should not exist at the start"

    # Configure will fail since use changes must be accepted
    with pytest.raises(SystemExit):
        merge(["=test/test-1.0-r2[test1]"])

    assert is_empty(
        os.path.join(env.prefix().CONFIG_DIR, "package.use")
    ), "package.use should not contain anything after running the merge"

    assert os.path.exists(
        os.path.join(env.prefix().CONFIG_DIR, "package.use.__cfg_protect__")
    )

    env.TESTING = True
