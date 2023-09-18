from tempfile import mkdtemp

import pytest

from portmod.config import get_config
from portmod.prefix import add_prefix

from .env import setup_env

try:
    import PySide6  # noqa: F401

    from portmod._gui.config import Config
except ModuleNotFoundError as error:
    if error.name == "PySide6":
        pytest.skip("GUI tests when PySide6 is not installed", allow_module_level=True)
    raise error


def test_get_current_prefix():
    setup_env("test")

    # If GUI_SELECTED_PREFIX is unset, __init__ will set it to
    # the first prefix it finds.
    gui_config = Config()

    assert gui_config.get_current_prefix() == "test"


def test_get_prefixes():
    # Setup 3 test prefixes
    setup_env("test")
    temp2 = mkdtemp("portmod.test2")
    add_prefix("test2", "test", temp2, "test", ["test"])
    temp3 = mkdtemp("portmod.test3")
    add_prefix("test3", "test", temp3, "test", ["test"])

    gui_config = Config()

    prefixes = gui_config.get_prefixes()

    assert prefixes == ["test", "test2", "test3"]


class TestCheckConfig:
    def test_gui_selected_prefix_not_set(self):
        # Setup 3 test prefixes
        setup_env("test")
        temp2 = mkdtemp("portmod.test2")
        add_prefix("test2", "test", temp2, "test", ["test"])
        temp3 = mkdtemp("portmod.test3")
        add_prefix("test3", "test", temp3, "test", ["test"])

        # GUI_SELECTED_PREFIX should be None before portmod._gui.config.check_config() runs.
        assert not get_config().get("GUI_SELECTED_PREFIX")

        # Initializing Config object runs check_config().
        Config()

        # GUI_SELECTED_PREFIX should now be "test3", as it should be the first prefix in the
        # list of prefixes.
        assert get_config().get("GUI_SELECTED_PREFIX") == "test"

    def test_gui_selected_prefix_set(self):
        # Setup 3 test prefixes
        setup_env("test")
        temp2 = mkdtemp("portmod.test2")
        add_prefix("test2", "test", temp2, "test", ["test"])
        temp3 = mkdtemp("portmod.test3")
        add_prefix("test3", "test", temp3, "test", ["test"])

        gui_config = Config()

        assert get_config().get("GUI_SELECTED_PREFIX") == "test"

        gui_config.set_prefix("test2")

        assert get_config().get("GUI_SELECTED_PREFIX") == "test2"
