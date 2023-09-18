.. _keywords:

Keywords
========

Keywords indicate the stability of game engines (architectures) for a given package.

Most packages declare one of the following engine-specific keywords in
their KEYWORDS field:

1. Stable: ``arch`` (E.g. ``openmw``) - This version of the mod
   and the pybuild are tested and not known to have any serious issues
   with the given platform.
2. Testing: ``~arch`` (E.g. ``~openmw``) - The version of the
   mod and the pybuild are believed to work and do not have any known
   serious bugs, but more testing should be performed before being
   considered stable.
3. No keyword: If a package has no keyword for a given arch, it means it
   is not known whether the package will work, or that insufficient
   testing has occurred for ~arch.
4. Masked: ``-arch`` (E.g. ``-openmw``) The package version will
   not work on the arch. This likely means it relies on a feature not
   supported by the engine, or contains serious bugs that make it
   unusable.

By default, only stable versions of packages are installed. For unstable
versions you will need to accept the keyword.

You can enable testing packages by default by overriding the default
``ACCEPT_KEYWORDS`` in :ref:`portmod.conf` with the testing keyword appropriate
for your engine.

You can accept keywords for specific packages by adding the mod version
and keyword to :ref:`package.accept_keywords`. E.g:

.. code:: sh

   =base/patch-for-purists-3.2.1 ~openmw
   # To ignore keywords and make the package visible regardless of keywords
   >=base/patch-for-purists-3.1.3 **

Versioned Keywords
------------------

.. versionadded:: 2.6

Keywords can also be versioned. This is an optional feature, and may not be set up for every engine, but it allows packages to be marked as stable/testing/masked on specific versions, in addition to generally.

E.g.

.. code:: python

   # Stable on 0.48 and later
   KEYWORDS = "openmw{>=0.48}"
   # Masked on 0.47.0, but stable on all other versions
   KEYWORDS = "openmw -openmw{==0.47.0}"
   # Stable on 0.47 and related patch versions, but only testing on 0.48 and newer and older versions
   KEYWORDS = "~openmw openmw{0.47*}"

When versioning is set up in the profile, ``ACCEPT_KEYWORDS`` can also be versioned.
Usually it will default to use the ``ARCH_VERSION`` profile variable.

E.g. in ``portmod.conf``

.. code:: python

   ACCEPT_KEYWORDS = "openmw{==0.48.0}"
   # If you want to accept packages testing on your version
   # Note that when using f-strings, literal '{' has to be escaped as '{{',
   # so there end up being three
   ACCEPT_KEYWORDS = f"~openmw{{=={ARCH_VERSION}}}"

See :ref:`arch_ver` in the development guide for further details.
