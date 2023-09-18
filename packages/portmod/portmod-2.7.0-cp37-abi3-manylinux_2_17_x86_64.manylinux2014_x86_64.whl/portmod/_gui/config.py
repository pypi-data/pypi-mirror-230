import sys
from typing import List

from PySide6 import QtCore

from portmod import prefix
from portmod.config import get_config, set_config_value
from portmod.globals import env


class Config(QtCore.QObject):
    """
    Manages prefixes. Handles intializing them, switching them, getting
    the current one, and checking if one is selected.
    """

    def __init__(self) -> None:
        super(Config, self).__init__()
        self.check_config()

    def check_config(self) -> None:
        """
        Checks to make sure everything is setup before launching the GUI.

        First, it checks to make sure there is at least one prefix, and prompts
        the user to create one if there isn't.

        Second, it set's the current prefix in the GUI to whatever the value of
        'GUI_SELECTED_PREFIX' is in the Portmod configuration file. If that value is
        unset, it sets it to the first prefix it finds in the list of prefixes.
        """
        # Checks if there are any prefixes
        if prefix.get_prefixes().keys():
            current_prefix = get_config().get("GUI_SELECTED_PREFIX")
            if current_prefix in prefix.get_prefixes().keys():
                self.set_prefix(current_prefix)
            # If GUI_SELECTED_PREFIX is unset, set it to the first prefix in get_prefixes()
            else:
                self.set_prefix(list(prefix.get_prefixes().keys())[0])
        else:
            # TODO: If there isn't at least one prefix, make the user create one
            print("NO PREFIXES DETECTED")
            sys.exit(-1)

    @QtCore.Slot(result=str)  # type: ignore
    def get_current_prefix(self) -> str:
        """
        Retrieves the name of the prefix from 'GUI_SELECTED_PREFIX' in the Portmod
        configuration file.
        """
        # This will never be None, as check_config() makes sure it is set.
        current_prefix: str = get_config()["GUI_SELECTED_PREFIX"]
        return current_prefix

    @QtCore.Slot(result=list)  # type: ignore
    def get_prefixes(self) -> List[str]:
        """
        Returns a list of each prefix name.
        """
        return list(prefix.get_prefixes().keys())

    @QtCore.Slot(str)
    def set_prefix(self, name: str) -> None:
        """
        Sets the internal prefix, and also sets the value of 'GUI_SELECTED_PREFIX'
        within the Portmod configuration file.
        """
        env.set_prefix(name)
        set_config_value("GUI_SELECTED_PREFIX", name, env.GLOBAL_PORTMOD_CONFIG)

    # TODO: Update based on changes in init consolidation (!568)
    # Also, create a setup wizard.

    # def add_prefix_repo(self, repo_name: str, pfx_name: str):
    #     enabled_repos = get_config()["REPOS"]
    #
    #     if repo_name and repo_name not in enabled_repos:
    #         enabled_repos.add(repo_name)
    #
    #     set_config_value("REPOS", " ".join(sorted(enabled_repos)))
    #     # Re-set prefix so that env.prefix().REPOS is updated
    #     env.set_prefix(pfx_name)
    #
    # def init_prefix(self, name, arch, profile, repos) -> None:
    #     prefix.add_prefix(name, arch)
    #     env.set_prefix(name)
    #     set_config_value("GUI_SELECTED_PREFIX", name, env.GLOBAL_PORTMOD_CONFIG)
    #     for repo in repos:
    #         self.add_prefix_repo(repo.name, name)
    #     set_profile(get_repo(arch).location + "/profiles/" + profile)
