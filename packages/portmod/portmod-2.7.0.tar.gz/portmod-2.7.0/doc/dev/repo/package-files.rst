.. _package-files:

Package Files
=============

Package files can be created as either python-like pybuild files,
or yaml files.

See the API for more details about available fields and functions.

Note that this guide is deliberately very simple. Many game engines require custom
installation options to register mods, so portmod package repositories generally
provide custom superclasses for use in packages to ensure that any required configuration
is updated. See the guides on `The Wiki <https://gitlab.com/portmod/portmod/-/wikis/Home>`_.

Pybuild Packages
----------------

Pybuild files have a syntax which is equivalent to python 3.7, not including restricted
syntax listed on the :ref:`sandbox` page.

They should generally follow a structure similar to the following example:

``example-suite-0.17.pybuild``

.. code:: python

  import os
  import shutil
  from pybuild import Pybuild2
  from pybuild.info import PV


  class Package(Pybuild2):
      NAME = "Example Suite"
      DESC = "A demo showing the capabilities of the OpenMW engine"
      HOMEPAGE = "https://github.com/OpenMW/example-suite"
      LICENSE = "CC-BY-3.0 CC-BY-SA-3.0 CC-BY-4.0"
      RDEPEND = "!!base/morrowind"
      KEYWORDS = "~openmw"
      SRC_URI = f"""
          https://github.com/OpenMW/example-suite/releases/download/{PV}/ExampleSuiteVersion{PV}.7z
      """
      S = f"ExampleSuiteVersion{PV}/openmw-template"
      # Actually included in the default DOCS, but note that the working directory must be correct
      # for them to recognized since subdirectories won't be searched.
      DOCS = ["AUTHORS.md", "CHANGELOG.md", "README.md"]

      def src_install(self):
          os.makedirs(os.path.join(self.D, "pkg", "base"))
          shutil.move("data", os.path.join(self.D, "pkg", "base", "example-suite"))


Yaml Packages
-------------

.. versionadded:: 2.7

Yaml packages cannot contain scripts, but can inherit
from :ref:`common` with custom scripts.

It is not currently possible to install anything other than documentation
in yaml-based package files without inheriting from a custom class.

Values in the :py:mod:`pybuild.info` module can be accessed using ``$``-based
substitutions, as implemented by `python Template strings <https://docs.python.org/3/library/string.html#template-strings>`_)

``example-suite-0.17.yaml``

.. code:: yaml

   NAME: Example Suite
   DESC: A demo showing the capabilities of the OpenMW engine
   HOMEPAGE: https://github.com/OpenMW/example-suite
   LICENSE: CC-BY-3.0 CC-BY-SA-3.0 CC-BY-4.0
   RDEPEND: "!!base/morrowind"
   KEYWORDS: ~openmw
   SRC_URI:
      https://github.com/OpenMW/example-suite/releases/download/${PV}/ExampleSuiteVersion${PV}.7z
   S: ExampleSuiteVersion${PV}/openmw-template
   DOCS: [AUTHORS.md, CHANGELOG.md, README.md]
