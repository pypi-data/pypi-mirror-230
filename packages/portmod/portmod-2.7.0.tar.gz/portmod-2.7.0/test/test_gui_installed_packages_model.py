from tempfile import mkdtemp
from test.env import select_profile, setup_env
from test.merge import merge

import pytest
from pytest import fail, fixture

from portmod.globals import env
from portmod.loader import load_installed_pkg
from portmod.prefix import add_prefix
from portmodlib.atom import Atom

try:
    import PySide6  # noqa: F401

    from portmod._gui.config import Config
    from portmod._gui.Manage.InstalledPackagesModel import InstalledPackagesProxyModel
    from portmod._gui.packages import get_installed_packages, get_local_flags
except ModuleNotFoundError as error:
    if error.name == "PySide6":
        pytest.skip("GUI tests when PySide6 is not installed", allow_module_level=True)
    raise error


@fixture(scope="module")
def single_model() -> InstalledPackagesProxyModel:
    setup_env("test")
    merge(["test/test"], nodeps=True)

    return InstalledPackagesProxyModel(get_installed_packages())


@fixture(scope="module")
def model() -> InstalledPackagesProxyModel:
    setup_env("test")
    merge(["test/test4"], nodeps=True)
    merge(["test/test"], nodeps=True)

    return InstalledPackagesProxyModel(get_installed_packages())


@fixture(scope="module")
def test4_model() -> InstalledPackagesProxyModel:
    setup_env("test")
    merge(["test/test4"], nodeps=True)

    return InstalledPackagesProxyModel(get_installed_packages())


def test_init(model):
    assert set(model.realModel._data) == set(get_installed_packages())
    assert set(model.realModel._data) == {
        load_installed_pkg(Atom("test/test")),
        load_installed_pkg(Atom("test/test4")),
    }


def test_get_atom(model):
    assert {model.getAtom(0), model.getAtom(1)} == {"test/test", "test/test4"}


def test_change_to_current_prefix(model):
    temp2 = mkdtemp("portmod.test2")
    add_prefix("test2", "test", temp2, "test", ["test"])
    select_profile("test")

    merge(["test/test7"], nodeps=True)

    # Adding a new prefix sets the current prefix to that one, so set it back.
    env.set_prefix("test")

    assert set(model.realModel._data) == {
        load_installed_pkg(Atom("test/test")),
        load_installed_pkg(Atom("test/test4")),
    }

    gui_config = Config()
    gui_config.set_prefix("test2")

    model.changeToCurrentPrefix()

    assert model.realModel._data == [
        load_installed_pkg(Atom("test/test7")),
    ]


# Note: Order matters.
# Due to side effects of setting up the models like installing packages,
# tests using a certain model need to be run in sequence


def test_get_name(single_model):
    assert single_model.get_name(0) == "Test"


def test_get_author(single_model):
    assert (
        single_model.get_author(0)
        == "someone <someone@example.org>, someone else, justamail@example.org, just a string"
    )


def test_get_version(single_model):
    assert single_model.get_version(0) == "2.0"


def test_get_size(single_model):
    assert single_model.get_size(0) == "0.0 B"


def test_get_license(single_model):
    assert single_model.get_license(0) == "test"


def test_get_description(single_model):
    assert single_model.get_description(0) == "Test Desc: foo-bar"


def test_get_homepage(single_model):
    assert single_model.get_homepage(0) == "https://example.org"


def test_get_local_flags_model(test4_model):
    installed_pybuild = load_installed_pkg(Atom("test/test4"))
    if installed_pybuild:
        flags = get_local_flags(installed_pybuild)
        flags_model = test4_model.get_local_flags_model(0)
        assert flags_model._data == flags
    else:
        fail()
