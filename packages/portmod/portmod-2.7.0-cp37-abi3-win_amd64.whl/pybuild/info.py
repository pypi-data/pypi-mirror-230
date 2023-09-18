# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Importing values from this module fills them with information about the
pybuild file from which they were imported
"""
# Note: This module should be removed from sys.modules prior to importing to ensure that
# the cached version is not used instead.

import os
from pathlib import Path
from typing import Optional

from portmodlib.atom import VAtom

CATEGORY: str = ""
"""
The package's category.

E.g. ``base``
"""
P: str = ""
"""
The package name and version.

E.g.: ``example-suite-1.0``
"""
PF: str = ""
"""
The package name with version and revision.

E.g.: ``example-suite-1.0-r1``
"""
PN: str = ""
"""
The package name without version.

E.g.: ``example-suite``
"""
PV: str = ""
"""
The package's version without revision

E.g. ``1.0``
"""
PR: Optional[str] = None
"""
The package's revision

E.g. ``r1``
"""
PVR: str = ""
"""
The package's version and revision

E.g. ``1.0-r1``
"""


def _get_info(atom):
    return {
        "P": atom.P,
        "PF": atom.PF,
        "PN": atom.PN,
        "PV": atom.PV,
        "PR": atom.PR,
        "PVR": atom.PVR,
    }


def _set_info(filename):
    """Puts module information in the global scope so that it can be imported"""
    global P, PF, PN, PV, PR, PVR, CATEGORY
    if filename is not None:
        CATEGORY = Path(filename).resolve().parent.parent.name
        name, _ = os.path.splitext(os.path.basename(filename))
        atom = VAtom("{}/{}".format(CATEGORY, name))

        globals().update(_get_info(atom))
