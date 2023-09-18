Package Names and Versions
==========================

.. note::
   Valid characters are displayed as a regular expression, so that they
   can be concisely specified while still being exhaustive. Brackets (``[]``)
   are part of the regex and are not considered valid characters in any context.

Category Names
--------------

A category name may contain any of the characters ``[A-Za-z0-9+_.-]``.
It must not begin with a hyphen, a dot or a plus sign.

.. _package-name:

Package Names
-------------

A package name may contain any of the characters ``[A-Za-z0-9+_-]``.
It must not begin with a hyphen or a plus sign, and must not end in a
hyphen followed by anything matching the :ref:`version-syntax`.

.. note::
   A package name does not include the category.
   The term qualified package name is used where a category/package pair is meant.

USE flag names
--------------
A USE flag name may contain any of the characters ``[A-Za-z0-9+_-]``.
It must begin with an alphanumeric character.

Underscores should be considered reserved for USE_EXPAND, as described
in the :ref:`use-expand` section of the USE flag guide.

Repository Names
----------------
A repository name may contain any of the characters ``[A-Za-z0-9_-]``.
It must not begin with a hyphen.
In addition, every repository name must also be a valid package name.

License Names
-------------

A license name may contain any of the characters ``[A-Za-z0-9+_.-]``.
It must not begin with a hyphen, a dot or a plus sign.

Keyword names
-------------

A keyword name may contain any of the characters ``[A-Za-z0-9_.-]``.
It must begin with an alphanumeric character.
In contexts where it makes sense to do so, a keyword name may be prefixed by a tilde or a hyphen.
In :py:attr:`pybuild.Pybuild2.KEYWORDS`, -* is also acceptable as a keyword.


.. versionchanged:: 2.6
   Keywords were not validated in the past, and any value was accepted and used,
   whether or not it conformed to the above specification. Now, invalid keywords will cause errors.

   Additionally, the ``.`` character was added to the above specification, to allow for keywords
   which include version numbers. This is for legacy purposes only, and it is recommended that you
   use the new keyword versioning system also introduced in Portmod 2.6.


.. _version-syntax:

Version Syntax
--------------

A version may optionally begin with an epoch, in the form ``e[0-9]+`` (an ``e``, then one or more digits). This epoch is a packaging-only component used to indicate that a package has changed to a new versioning system which is incompatible with the old versioning system. If the epoch is omitted, the version is considered to be epoch ``e0``. The epoch, when present, is separated from the rest of the version by a hyphen.

A version always must contain a number part, which is in the form ``[0-9]+(\.[0-9]+)*`` (an unsigned integer, followed by zero or more dot-prefixed unsigned integers). E.g. ``1.2.3``

This may optionally be followed by one of ``[a-z]`` (a lowercase letter).

This may be followed by zero or more of the suffixes ``_alpha``, ``_beta``, ``_pre``, ``_rc`` or ``_p`` (in order of priority),
each of which may optionally be followed by an unsigned integer.
Suffix and integer count as separate version components.

This may optionally be followed by the suffix ``-r`` followed immediately by an unsigned integer (the “revision number”, used to indicate changes to the package which require rebuilding, when there are no changes to the upstream project).
If this suffix is not present, it is assumed to be ``-r0``.

E.g. Using all the components: ``e2-1.2.3a_alpha12-r3``.

.. _external-versions:

External Versions
.................
.. versionadded:: 2.6

A variant on the version syntax is used for "external" versions, that is, versions
where packaging concepts like revisions and epochs aren't meaningful. These versions
are identical to regular versions except that they cannot include revisions, epochs
or the `_p` suffix.

E.g. ``1.2.3a_alpha12``.

Version Comparison and Ordering
...............................
Generally speaking, versions are compared component by component, from left to
right, with the left-most components being the most significant when differences
are found between the versions.

This means that epoch differences always outweigh everything else, and revisions
are always the last to have an effect.

Numeric version components are compared as individual integers if they have no
leading zeroes.
If one of the components being compared has a leading zero, lexicographical
comparison is done instead (comparing each digit one by one).

E.g. ``1.1 < 1.2 < 1.10 < 1.11``

However ``1.01 < 1.09 < 1.1`` even in the second comparison, because there is
a leading 0 and ``0 < 1`` (the ``9`` is not compared because the second
version only has one digit in that component).

For the exact version comparison algorithm, see `Section 3.3 of the Package Manager Specification <https://projects.gentoo.org/pms/7/pms.html#x1-260003.3>`_. Note that epochs are not included in that algorithm, but are checked first and the package with the larger epoch is always the greater version.

.. _version-specifier:

Version Specifier
-----------------
.. versionadded:: 2.6

Version specifiers should consist of a list of versions with operators, and separated by commas. The specifier matches versions which match *all* conditions in the specifier.

E.g. ``>=1.0,<3.0`` matches versions between 1.0 and 3.0, including 1.0, but not 3.0.

Available operators are listed below. Note that all operators except globstar should be written before the version they apply to, while globstar folows the version.

- ``>``: Greater than -- matches versions greater than the specified version.
- ``<``: Less than
- ``>=``: Greater than or equal to
- ``<=``: Less than or equal to
- ``==``: Equals -- Matches versions which are exactly equal to the specified version.
- ``!=``: Not Equals -- Matches versions which are not exactly equal to the specified version.
- ``*``: Globstar -- Matches all versions starting with the specified version. Note that the version preceeding the star operator must still be valid. E.g. ``1.0*`` is valid, but ``1.0.*`` is not.

Version specifiers are currently only used in ``KEYWORDS``/``ACCEPT_KEYWORDS`` for versioned architectures.
They cannot be used in ``DEPEND`` or similar package variables, where a different syntax is used.

External Resources
------------------

Ignoring slots and epochs, Portmod's version specifiers are identical to Portage's version specifiers. The following Gentoo resources may be helpful.

- https://wiki.gentoo.org/wiki/Version_specifier
- https://devmanual.gentoo.org/ebuild-writing/file-format/index.html#file-naming-rules.

Portmod's package names and versions generally follow `Section 3 of the Package Manager Specification <https://projects.gentoo.org/pms/7/pms.html#x1-150003>`_, with some exceptions. Excerpts of this section have been copied verbatim and are licensed `CC-BY-SA-3.0 <http://creativecommons.org/licenses/by-sa/3.0/>`_.
