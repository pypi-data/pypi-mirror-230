.. _arch_ver:

Architecture Versioning
=======================

The file ``.get_arch_version.py``, if installed into a prefix, can be used to detect the version of an architecture. The file should, when run in a python interpreter, print the version to stdout (in portmod's external version format, i.e. without revisions or epochs. See :ref:`external-versions`). If the script produces a non-zero exit code, any output will be ignored.

It is recommended that this be written as efficiently as possible, as it is run at the beginning of almost every single portmod command since it's necessary to set up the profile.

The script has full read access in the :ref:`sandbox`, but no write access outside of a temporary directory which will be specified through the ``TMP`` or ``TMPDIR`` environment variables (such as can be accessed by the python :py:mod:`tempfile` module; see :ref:`sandbox-tmp` for details). It also has no network access.

The output of the script, assuming it parses as a valid version, gets set in the sandbox as the ``ARCH_VERSION`` variable (see :ref:`defaults.conf`). Otherwise, ``ARCH_VERSION`` is ``None``.

E.g. ``.get_arch_version.py``

.. code:: python

    """Finds openmw version on linux"""

    version_file_path = "/usr/share/openmw/resources/version"
    with open(version_file_path, encoding="utf-8") as file:
        print(file.read().strip(), end="")

.. note::
   stderr will not be redirected, and it is recommended that any commands which produce stderr
   should be redirected or suppressed.
   Successful version detection should write nothing to stderr.

   However, stderr can be used in the case of failure to indicate to the user things such as
   environment variables which can be set to aid version detection
   (e.g. the path of the game data directory).


Usage
-----

Keywords in :py:attr:`pybuild.Pybuild2.KEYWORDS` can optionally be followed by a :ref:`version-specifier` surrounded by ``{}``, making it possible to indicate that a package is stable, testing or masked on a specific version or range of versions.

Note that multiple levels of support are available.

At minimum, by installing the version detection script so that ``ARCH_VERSION`` gets set while using non-version-specific ``ACCEPT_KEYWORDS`` you immediately will get support for masking packages when they are broken on a particular version. That is, packages with version-specific masks (e.g. ``-openmw{<0.48}``) will get masked, while without ``ARCH_VERSION`` only generic masks such as ``-openmw`` that apply to all versions will have an effect.

By using a version-specific ``ACCEPT_KEYWORDS`` (e.g. ``ACCEPT_KEYWORDS = "openmw{==0.47.0}"``) then version-specific stable and testing keywords will also be respected, and when your ``ARCH_VERSION`` falls into the range of versions specified, the package will have the stability provided by the keyword.

If the ``.get_arch_version.py`` file is being installed by a package, users will not have ``ARCH_VERSION`` set when portmod first runs. To handle this, it is generally recommended that ``ACCEPT_KEYWORDS`` be set in the following manner (to accept stable by default, minor modifications would be necessary for testing by default):

.. code:: python

   if ARCH_VERSION is None:
       ACCEPT_KEYWORDS = ARCH
   else:
       ACCEPT_KEYWORDS = f"{ARCH}{{=={ARCH_VERSION}}}"

This also means that packages in the :ref:`@system set <sets>` (notably including the package that installs the version detection script) should not use version-specific keywords, as they will be ignored on the first run.
