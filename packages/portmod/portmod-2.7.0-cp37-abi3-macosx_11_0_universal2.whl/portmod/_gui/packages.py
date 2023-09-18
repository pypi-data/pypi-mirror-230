from typing import Dict, List, Tuple

from portmod.loader import load_all_installed
from portmod.pybuild import InstalledPybuild
from portmod.query import get_flags, query
from portmod.repo import LocalRepo
from portmod.repo.metadata import get_profiles
from portmodlib.portmod import PackageIndexData


class LocalFlag:
    def __init__(self, name: str, description: str, status: bool) -> None:
        self.name = name
        self.description = description
        self.status = status


def get_installed_packages() -> List[InstalledPybuild]:
    return list(load_all_installed())


def get_local_flags(pybuild: InstalledPybuild) -> Dict[str, Tuple[bool, str]]:
    """
    Returns a dictionary where the keys are USE flags, and the values are
    a tuple containing the flags status (whether it's enabled or not),
    and its description.
    """

    flags = get_flags(pybuild)[0]

    restructured_flags = {}
    for flag in flags:
        restructured_flags[flag] = (
            flag in pybuild.get_use(),  # Flag status
            flags[flag],  # Description
        )

    return restructured_flags


def search_packages(search_term: str) -> List[PackageIndexData]:
    return query(search_term, 0)


def list_profiles(arch: str, repos: List[LocalRepo]) -> List[str]:
    return [
        name for values in get_profiles(arch, repos).values() for _, name, _ in values
    ]
