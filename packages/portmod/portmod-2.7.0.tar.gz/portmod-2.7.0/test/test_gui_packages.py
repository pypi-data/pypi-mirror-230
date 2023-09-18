from test.env import setup_env
from test.merge import merge

import pytest
from pytest import fail

from portmod.loader import load_installed_pkg
from portmodlib.atom import Atom

try:
    import PySide6  # noqa: F401

    from portmod._gui.packages import get_installed_packages, get_local_flags
except ModuleNotFoundError as error:
    if error.name == "PySide6":
        pytest.skip("GUI tests when PySide6 is not installed", allow_module_level=True)
    raise error


def test_get_installed_packages():
    setup_env("test")
    merge(["test/test0"], nodeps=True)
    merge(["test/test2"], nodeps=True)
    merge(["test/test3"], nodeps=True)

    packages = {
        load_installed_pkg(Atom("test/test0")),
        load_installed_pkg(Atom("test/test2")),
        load_installed_pkg(Atom("test/test3")),
    }

    assert set(get_installed_packages()) == packages


def test_get_local_flags():
    setup_env("test")
    merge(["test/test4"], nodeps=True)

    installed_pybuild = load_installed_pkg(Atom("test/test4"))
    if installed_pybuild:
        assert get_local_flags(installed_pybuild) == {"baf": (False, "test flag")}
    else:
        fail()
