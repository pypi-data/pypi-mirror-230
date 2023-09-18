# Copyright 2022 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Abstract interface for IO

This currently only targets the merge function in the portmod/merge.py file via the
MergeIO abstract class, and install_pkg via InstallIO (install_pkg gets called by
merge, but shouldn't be invoked by itself).

To use, call merge(..., io=my_merge_io), passing an object from a class which
implements MergeIO as my_merge_io.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import AbstractSet, Callable, Iterable, Optional, Sequence, Set

from portmod.loader import SandboxedProcess
from portmod.pybuild import Pybuild
from portmod.util import KeywordDep, LicenseDep
from portmodlib.atom import Atom, FQAtom

from .util import UseDep


class Transaction:
    """Transaction class"""

    REPR: str
    COLOUR: Callable[[str], str]
    pkg: Pybuild
    flags: Set[str]

    def __init__(self, pkg: Pybuild, flags: Iterable[str]):
        self.pkg = pkg
        self.flags = set(flags)

    def __str__(self):
        return f"{self.__class__.__name__}({self.pkg})"

    def __repr__(self):
        return str(self)


class Task:
    """A function which the interface is expected to call"""

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.done: bool = False

    def run(self):
        """Runs the task"""
        if not self.done:
            self.func(*self.args, **self.kwargs)
            self.done = True
        else:
            raise Exception("Tasks cannot be run twice!")


@dataclass(frozen=True)
class Message:
    """A message produced by a package"""

    class Type(Enum):
        """The type of the package's message"""

        INFO = "info"
        WARNING = "warning"

    typ: Type
    text: str


class MergeMode(Enum):
    """
    Merge modes. Value corresponds to the localised text
    """

    INSTALL = "to-install"
    REMOVE = "to-remove"


class PhaseFunction(Enum):
    SRC_UNPACK = "src_unpack"
    SRC_PREPARE = "src_prepare"
    SRC_INSTALL = "src_install"
    PKG_POSTINST = "pkg_postinst"
    PKG_PRERM = "pkg_prerm"


class Progress(ABC):
    """
    Abstract class for receiving information which can be displayed in progressbars
    """

    def __init__(self, steps: int):
        self.steps = steps

    @abstractmethod
    def update(self, *, value: Optional[int] = None):
        ...

    @abstractmethod
    def done(self):
        ...


class PackageIO(ABC):
    """
    Abstract class for implementing input/output handling for :py:func:`portmod.package:install_pkg`
    and :py:func:`portmod.package.remove_pkg`
    """

    def __init__(self, package: FQAtom, pipe_output: bool):
        """
        args:
            package: The package atom, fully qualified
            pipe_output: Whether or not stdout and stderr should be piped. If true, no
                         stderr or stdout will be produced, and the implementor will be
                         required to read and handle this using Popen.communicate
        """
        self.package = package
        self.pipe_output = pipe_output

    @abstractmethod
    def phase_function(self, function: PhaseFunction, process: SandboxedProcess):
        """
        A phase function has begun execution

        The process can be monitored to determine when execution has ended,
        and its communicate function can be used to read output (if pipe_output was set)

        Note that the subprocess will run in the background, and the install process will
        wait on it after this function has finished executing.
        The purpose of this function is to allow a UI to monitor and use the phase function's
        output in real time.
        """


class RemoveIO(PackageIO):
    @abstractmethod
    def remove_files(self, count: int) -> Progress:
        """Should return something which can handle displaying file installation progress"""

    @abstractmethod
    def begin_removal(self):
        """Package removal has begun"""

    @abstractmethod
    def finished_removal(self):
        """Package removal has finished successfully"""


class InstallIO(RemoveIO):
    """
    Interface for installing packages.

    The old package, if present, will be removed as part of installation via the RemoveIO interface
    """

    @abstractmethod
    def check_conflicts(self, count: int) -> Progress:
        """Should return something which can handle displaying file conflict progress"""

    @abstractmethod
    def install_files(self, count: int) -> Progress:
        """Should return something which can handle displaying file installation progress"""

    @abstractmethod
    def begin_install(self):
        """Package installation has begun"""

    @abstractmethod
    def finished_install(self):
        """Package installation has finished successfully"""

    @abstractmethod
    def get_fetch_progress(
        self, filename: str, start: int, end: Optional[int]
    ) -> Progress:
        """Returns a progress for displaying remote file fetching progress"""

    @abstractmethod
    def can_overwrite(self, path: str) -> bool:
        """
        Should return true if the specified path can be overwritten

        Is only called on files which already exist on the filesystem and are not owned by another package
        """


class MergeIO(ABC):
    """
    Abstract class for implementing input/output handling for :py:func:`portmod.merge:configure`
    """

    @abstractmethod
    def display_transactions(
        self,
        mode: MergeMode,
        transactions: Sequence[Transaction],
        new_selected: AbstractSet[Pybuild],
    ):
        """
        Transaction list to display to the user

        args:
            transactions: List of transactions to perform, in order.
            new_selected: Packages which were selected for installation
                          these, along with previously selected packages
                          (use :py:func:`portmod.config.sets:is_selected`) should be
                          visually distinguished from packages which are installed
                          just as dependencies
        """

    @abstractmethod
    def use_changes(self, use_flags: Sequence[UseDep], apply_callback: Task):
        """
        Display necessary flag changes to the user and prompt them to accept
        the changes

        args:
            use_flags: he use flag changes which are required
            apply_callback: Task, which when executed will apply the changes
        """

    @abstractmethod
    def keyword_changes(self, keywords: Sequence[KeywordDep], apply_callback: Task):
        """
        Display necessary keyword changes to the user and prompt them to accept
        the changes

        args:
            keywords: The keyword changes which are required
            apply_callback: Task, which when executed will apply the changes
        """

    @abstractmethod
    def license_changes(self, licenses: Sequence[LicenseDep], apply_callback: Task):
        """
        Display licenses which need to be accepted and prompt the user to accept them

        args:
            licenses: The licenses which must be accepted
            apply_callback: Task, which when executed will apply the changes
        """

    @abstractmethod
    def pkg_nofetch(self, package: FQAtom, instructions: str):
        """
        Display fetch information for the package

        args:
            package: The package which contains files which could not be fetched
            instructions: The instructions produced by the package describing how
                         to manually fetch the files
        """

    @abstractmethod
    def pkg_pretend(self, package: FQAtom, message: str):
        """
        Display pkg_pretend messages for the package

        args:
            package: The package which produced the message
            message: The output from pkg_pretend
        """

    @abstractmethod
    def space_warning(self, package: FQAtom, message: str):
        """
        Display message about insufficient space

        args:
            package: The package which contains files which could not be fetched
            message: Message to display
        """

    @abstractmethod
    def rebuild_warning(self, packages: Sequence[Atom], message: str):
        """
        Display message about packages which need to be rebuilt

        args:
            packages: The package which need to be rebuilt
            message: Message to display
        """

    @abstractmethod
    def merge_ready(self, start_callback: Task):
        """
        Called when all checks have passed and we are ready to merge

        args:
            start_callback: Task to indicate that the user wants to begin merge
        """

    @abstractmethod
    def pkg_messages(self, package: FQAtom, messages: Sequence[Message]):
        """
        Display custom messages for the package

        atgs:
            package: The package which produced the custom messages
            messages: Messages to display
        """

    @abstractmethod
    def get_install_io(self, package: FQAtom) -> InstallIO:
        """
        Produce an InstallIO object for use when installing a package

        This will be called once for each package to be installed
        """

    @abstractmethod
    def get_remove_io(self, package: FQAtom) -> RemoveIO:
        """
        Produce an RemoveIO object for use when removing a package

        This will be called once for each package to be removed
        """

    @abstractmethod
    def finished(self, message: str):
        """
        Called when the merge operation has finished. The message should be displayed to the user
        """
