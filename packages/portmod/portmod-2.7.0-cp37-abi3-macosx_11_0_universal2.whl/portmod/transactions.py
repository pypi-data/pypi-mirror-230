# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import sys
from logging import error
from typing import (
    AbstractSet,
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    cast,
)

from portmod.io import Transaction
from portmodlib.atom import Atom, FQAtom, QualifiedAtom, atom_sat
from portmodlib.colour import blue, bright, green, lgreen, red, yellow
from portmodlib.l10n import l10n
from portmodlib.usestr import use_reduce

from .config.sets import is_selected
from .config.use import get_use
from .download import fetchable, find_download, get_download_size
from .loader import (
    SandboxedError,
    _sandbox_execute_pybuild,
    load_installed_pkg,
    load_pkg_fq,
)
from .parsers.flags import collapse_flags
from .perms import Permissions
from .pybuild import InstalledPybuild, Pybuild
from .query import get_usestring
from .tsort import CycleException, WeightedEdge, tsort
from .util import UseDep, select_package


def can_update_live(pkg: InstalledPybuild):
    proc = _sandbox_execute_pybuild(
        pkg.FILE,
        "can-update-live",
        Permissions(network=True),
        installed=True,
        # Special True constant (see portmodlib/_wrapper.py)
    )
    returncode = proc.wait_returncode()
    if returncode == 142:
        return True
    if returncode == 0:
        return False
    proc.wait()


class PackageDoesNotExist(Exception):
    """Indicates that no mod matching this atom could be loaded"""

    def __init__(self, atom: Optional[Atom] = None, *, msg=None):
        super().__init__(msg or l10n("package-does-not-exist", atom=green(atom)))


class Delete(Transaction):
    """Delete Transaction"""

    REPR = "d"
    COLOUR = red
    pkg: InstalledPybuild

    def __init__(self, pkg: InstalledPybuild):
        super().__init__(pkg, set())


class New(Transaction):
    """New Package Transaction"""

    REPR = "N"
    COLOUR = lgreen


class Change(Transaction):
    """Update Package Transaction"""

    COLOUR = blue

    def __init__(self, pkg: Pybuild, old: InstalledPybuild, flags: Iterable[str]):
        super().__init__(pkg, flags)
        self.old = old


class Update(Change):
    """Downgrade Package Transaction"""

    REPR = "U"


class Downgrade(Change):
    """Downgrade Package Transaction"""

    REPR = "D"


class Reinstall(Transaction):
    """Reinstall Package Transaction"""

    REPR = "R"
    COLOUR = yellow


class Transactions:
    pkgs: List[Transaction]
    config: List[Any]
    new_selected: Set[Pybuild]

    def __init__(self):
        self.pkgs = []
        self.config = []
        self.new_selected = set()

    def copy(self) -> "Transactions":
        new = Transactions()
        new.pkgs = self.pkgs.copy()
        new.config = self.config.copy()
        new.new_selected = self.new_selected.copy()
        return new

    def append(self, trans: Transaction):
        self.pkgs.append(trans)

    def add_new_selected(self, pkg: Pybuild):
        self.new_selected.add(pkg)

    def extend(self, trans: "Transactions"):
        self.pkgs.extend(trans.pkgs)
        self.config += trans.config
        self.new_selected |= trans.new_selected


def print_transactions(
    pkgs: Sequence[Transaction],
    new_selected: AbstractSet[Pybuild],
    verbose: bool = False,
    out=sys.stdout,
    summarize: bool = True,
):
    for trans in pkgs:
        pkg = trans.pkg
        installed_mod = load_installed_pkg(Atom(trans.pkg.CPN))
        if installed_mod is None:
            installed_use = None
        else:
            installed_use = installed_mod.INSTALLED_USE

        v = verbose or isinstance(trans, New)

        if isinstance(trans, Delete):
            usestring = ""
        else:
            usestring = get_usestring(pkg, installed_use, trans.flags, v)

        trans_colour = trans.__class__.COLOUR
        oldver = ""
        if isinstance(trans, Change):
            oldver = blue(" [" + trans.old.PVR + "]")

        modstring: str
        if verbose:
            modstring = pkg.ATOM
        else:
            modstring = pkg.ATOM.CPF

        if is_selected(pkg.ATOM) or pkg in new_selected:
            modstring = bright(green(modstring))
        else:
            modstring = green(modstring)

        fetch_status = " "
        fetchable_files = set(fetchable(trans.pkg, trans.flags))
        fetch_restricted = [
            source
            for source in trans.pkg.get_source_manifests(trans.flags)
            if source not in fetchable_files
        ]
        if fetch_restricted:
            if all(find_download(source) for source in fetch_restricted):
                fetch_status = "f"
            else:
                fetch_status = "F"

        print(
            f"[{red(fetch_status)}{bright(trans_colour(trans.REPR))}]"
            f" {modstring}{oldver} {usestring}",
            file=out,
        )

    if summarize:
        download_size = get_download_size(
            {trans.pkg: trans.flags for trans in pkgs if not isinstance(trans, Delete)}
        )
        print(
            l10n(
                "transaction-summary",
                packages=len(pkgs),
                updates=len([trans for trans in pkgs if isinstance(trans, Change)]),
                new=len([trans for trans in pkgs if isinstance(trans, New)]),
                reinstalls=len(
                    [trans for trans in pkgs if isinstance(trans, Reinstall)]
                ),
                removals=len([trans for trans in pkgs if isinstance(trans, Delete)]),
                download=download_size,
            ),
            file=out,
        )


def get_all_deps(depstring: str) -> List[Atom]:
    dependencies = use_reduce(depstring, token_class=Atom, matchall=True, flat=True)

    # Note that any || operators will still be included. strip those out
    return list(
        [dep for dep in dependencies if dep != "||" and not dep.startswith("!")]
    )


def sort_transactions(transactions: Transactions):
    """
    Create graph and do a topological sort to ensure that mods are installed/removed
    in the correct order given their dependencies
    """

    def get_dep_graph(rdepend=True):
        graph: Dict[Atom, Set[Tuple[Atom, Optional[int]]]] = {}
        priorities = {}

        for trans in transactions.pkgs:
            graph[trans.pkg.ATOM] = set()
            # Always remove packages last
            # FIXME: This is a poor workaround to the fact that the removal order
            # doesn't ensure that the package being replaced has RDEPEND satisfied
            # something which is necessary for pkg_prerm (note that it may not be
            # possible if the old and new versions have dependencies which cannot
            # be installed simultaneously)
            if isinstance(trans, Delete):
                priorities[trans.pkg.ATOM] = "z"
            else:
                if trans.pkg._PYBUILD_VER == 1:
                    priorities[trans.pkg.ATOM] = trans.pkg.TIER  # type: ignore
                else:
                    priorities[trans.pkg.ATOM] = "a"

        def add_depends(mod, key: str, delete: bool, weight: Optional[int]):
            depends = {}
            depstring = getattr(mod, key)
            for dep in get_all_deps(depstring):
                for trans in transactions.pkgs:
                    if atom_sat(trans.pkg.ATOM, dep):
                        depends[trans.pkg.ATOM] = trans.pkg

            if delete:
                # When removing packages, remove them before their dependencies
                graph[mod.ATOM] |= {WeightedEdge(dep, weight) for dep in depends.keys()}
            else:
                # When adding or updating packages, packages, add or update their dependencies
                # before them
                for dep in depends:
                    graph[dep].add(WeightedEdge(mod.ATOM, weight))
                    if key == "DEPEND":
                        # Also ensure runtime dependencies are available for build dependencies
                        # Whether or not we enforce runtime dependencies for all packages
                        add_depends(depends[dep], "RDEPEND", False, weight=weight)

        for trans in transactions.pkgs:
            add_depends(trans.pkg, "DEPEND", isinstance(trans, Delete), weight=None)
            if rdepend:
                add_depends(trans.pkg, "RDEPEND", isinstance(trans, Delete), weight=1)
        return graph, priorities

    # Attempt to sort using both runtime and build dependencies.
    # Runtime dependencies may not be satisfied if there is a cycle,
    # but build dependencies always will.
    graph, priorities = get_dep_graph()
    try:
        mergeorder = tsort(graph, priorities)
    except CycleException as exception:
        raise CycleException(
            l10n("cycle-encountered-when-sorting-transactions"), exception.cycle
        )

    new_trans = transactions.copy()
    new_trans.pkgs = []
    for atom in mergeorder:
        for trans in transactions.pkgs:
            if trans.pkg.ATOM == atom:
                new_trans.pkgs.append(trans)
                break

    return new_trans


def generate_transactions(
    enabled: Iterable[FQAtom],
    disabled: Iterable[FQAtom],
    newselected: AbstractSet[QualifiedAtom],
    usedeps: Iterable[UseDep],
    enabled_flags: Dict[FQAtom, Set[str]],
    *,
    emptytree: bool = False,
    update: bool = False,
) -> Transactions:
    """
    Generates a list of transactions to update the system such that
    all packages in enabled are installed and all packages in disabled are not

    Packages will not be rebuilt unless a change has occurred, or they are included
    in the new_selected parameter set and update is not specified.

    args:
        enabled: Packages that should be enabled, if not already
        disabled: Packages that should be disabled, if not already
        new_selected: Packages that were selected by the user for this operation
                      These should be re-installed, even if no change has been
                      made, unless update is also passed
        usedeps: Use changes that should accompany the transactions
        update: If true, will update live packages, and won't re-install packages which haven't changed

    returns:
        Onject representing the transactions
    """

    transactions = Transactions()

    # Note: while this technically requires knowing about the use flags in advance,
    # despite being needed to determine the use flags enabled, any flags which are related
    # to a relevant alias would have been included in flagupdates as they are handled by
    # the dependency calculator.
    def is_installed(atom: Atom) -> bool:
        for fqatom in enabled:
            if atom_sat(fqatom, atom) and atom.USE <= enabled_flags[fqatom]:
                return True
        return False

    for atom in enabled:
        pkg = load_pkg_fq(atom)

        flags = set(
            filter(
                lambda x: not x.startswith("-"),
                collapse_flags(
                    get_use(pkg, is_installed=is_installed)[0], enabled_flags[atom]
                ),
            )
        )

        if "local" in pkg.PROPERTIES:
            continue

        (to_install, dep) = select_package([pkg])

        if dep is not None:
            if isinstance(dep, (list, set)):
                transactions.config.extend(dep)
            else:
                transactions.config.append(dep)

        installed = load_installed_pkg(Atom(atom.CPN))

        if not (to_install or installed):
            raise PackageDoesNotExist(atom)

        if (
            to_install is not None
            and to_install.ATOM.CPN in newselected
            or (installed and installed.ATOM.CPN in newselected)
        ):
            transactions.add_new_selected(cast(Pybuild, to_install or installed))

        if emptytree:
            transactions.append(
                Reinstall(cast(Pybuild, to_install or installed), flags)
            )
            continue

        # TODO: There might be advantages to preferring installed over to_install
        # such as avoiding re-downloading files just because the sources changed in a trivial
        # manner
        def safe_can_update_live(pkg: InstalledPybuild):
            try:
                can_update_live(pkg)
            except SandboxedError as e:
                error(e)
                return False

        if installed is not None:
            if installed.version > (to_install or installed).version:
                # to_install cannot be None if it has a smaller version
                transactions.append(Downgrade(to_install, installed, flags))
            elif ((to_install or installed).version > installed.version) or (
                update
                and "live"
                in use_reduce(installed.PROPERTIES, installed.INSTALLED_USE, flat=True)
                and can_update_live(installed)
            ):
                transactions.append(Update(to_install or installed, installed, flags))
            elif installed.INSTALLED_USE != flags:
                transactions.append(Reinstall(to_install or installed, flags))
            elif not update and installed.ATOM.CPN in newselected:
                transactions.append(Reinstall(to_install or installed, flags))
            elif to_install and not atom.R.endswith("::installed"):
                # If the repo's version is enabled, this means the dep generator
                # wants the package re-installed using the repo's version for some reason
                transactions.append(Reinstall(to_install, flags))
        elif to_install is not None:
            new_mod = to_install
            transactions.append(New(new_mod, flags))

    for atom in disabled:
        to_remove = load_installed_pkg(Atom(atom))
        if to_remove is not None:
            transactions.append(Delete(to_remove))

    for dep in usedeps:
        for trans in transactions.pkgs:
            if atom_sat(trans.pkg.ATOM, dep.atom):
                transactions.config.append(dep)

    return transactions
