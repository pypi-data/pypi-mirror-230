:orphan:

.. _repositories:

====================
Package Repositories
====================

Repositories have the following basic file structure:

::

   ./profiles/repo_name
   ./CATEGORY_NAME/metadata.yaml
   ./CATEGORY_NAME/PACKAGE_NAME/PACKAGE_NAME-VER.pybuild
   ./CATEGORY_NAME/PACKAGE_NAME/PACKAGE_NAME-OTHER_VER.pybuild
   ./CATEGORY_NAME/PACKAGE_NAME/Manifest
   ./CATEGORY_NAME/PACKAGE_NAME/metadata.yaml

Categories
----------

Any category must be listed in ``profiles/categories`` and contain a
:ref:`metadata.yaml` file.

.. _package-directories:

Package Directories
-------------------

.. toctree::
   :maxdepth: 1

   package-files
   metadata.yaml
   ../manifest

Package directories must be in a subdirectory of a category and their
directory name should be the same as the base name of the package files
(excluding version).

E.g.

.. code:: sh

  category/example-package
  ├── files
  │   └── some-extra-file.txt
  ├── Manifest
  ├── metadata.yaml
  ├── example-package-1.0.pybuild
  └── example-package-1.1.yaml


The :ref:`Manifest` file is optional, but is required to contain a manifest
entry for each source file listed in :py:attr:`SRC_URI <pybuild.Pybuild2.SRC_URI>` (i.e. only optional for
pybuilds without sources).

:ref:`metadata.yaml` is optional.

One or more package files must be included. These files must begin with the :ref:`package name <package-name>`, followed by a hyphen, then the :ref:`package version <version-syntax>`, and end in either the ``.yaml`` or ``.pybuild`` extension. For details on the content of packages, see :ref:`package-files`.

Optionally, extra files can be distributed with the package in the ``files`` directory.
These should be small, plaintext files such as patch files, and can be referred to in
installation scripts via the :py:attr:`FILESDIR <pybuild.Pybuild2.FILESDIR>` attribute.

Profiles Directory
------------------

The files in profiles are optional, except for repo_name.

+------------------+---------------------------------------------------+
| File             | Description                                       |
+==================+===================================================+
| arch.list        | A newlline-separated list of architectures. An    |
|                  | architecture may refer to a game-engine variant   |
|                  | or an operating system, and is used to            |
|                  | distinguish configurations where a package may be |
|                  | stable when used in the context of one, but       |
|                  | unstable in the context of another.               |
+------------------+---------------------------------------------------+
| categories       | A newline-separated list of categories. These     |
|                  | determine which directories in the root of the    |
|                  | repository are considered categories containing   |
|                  | packages. Directories not listed in this file     |
|                  | will not be detected as containing packages.      |
+------------------+---------------------------------------------------+
| lic\             | A yaml file containing a mapping from license     |
| ense_groups.yaml | groups to a whitespace-separated list of license  |
|                  | names. Each group can be referenced within        |
|                  | ACCEPT_LICENSE by prefixing it with an ``@``, and |
|                  | they also reference each other using the same     |
|                  | method.                                           |
+------------------+---------------------------------------------------+
| package.mask     | A :ref:`package.mask`                             |
|                  | file which applies regardless of profile          |
+------------------+---------------------------------------------------+
| profiles.yaml    | A yaml file containing profile declarations. See  |
|                  | :ref:`profiles`.                                  |
+------------------+---------------------------------------------------+
| repo_name        | A file containing a single line with the name of  |
|                  | this repository                                   |
+------------------+---------------------------------------------------+
| use.yaml         | A file describing the global use flags,           |
|                  | containing a mapping of use flag names to         |
|                  | descriptions                                      |
+------------------+---------------------------------------------------+
| use.alias.yaml   | A file describing global use flags which have     |
|                  | their values tied to packages. Contains a mapping |
|                  | of use flag names to package atoms.               |
+------------------+---------------------------------------------------+
| desc             | A directory containing USE_EXPAND descriptor      |
|                  | files. Each file has the same form as             |
|                  | ``use.yaml``.                                     |
+------------------+---------------------------------------------------+


Additionally, there are a number of files related to specific profiles. See :ref:`profiles`.

.. toctree::
   :maxdepth: 3

   profiles

Metadata Directory
------------------

.. toctree::
   :maxdepth: 1

   layout.conf

The metadata directory is optional

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - File
     - Description
   * - groups.yaml
     - Defines maintainer groups
   * - layout.conf
     - See :ref:`layout.conf`
   * - news
     - See `GLEP 42 <https://www.gentoo.org/glep/glep-0042.html>`__, noting
       that news files are in yaml format rather than XML. Specification for
       the files can be found `here <https://gitlab.com/portmod/portmod/-/blob/master/src/news.rs>`__
       (TODO: Rustdoc), and the directory structure follows GLEP 42.
