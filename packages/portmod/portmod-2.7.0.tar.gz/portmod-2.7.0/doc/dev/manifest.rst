.. _Manifest:

Manifest
========

In the tree, every package has a ``Manifest`` file. The Manifest file contains
various hashes and file size data for every external source that is to
be fetched. This is used primarily to verify the integrity of external files.

Generating the Manifest
-----------------------

To generate the Manifest, use ``inquisitor manifest foo.pybuild``. When
new sources are added or removed, the ``Manifest`` must be regenerated.

Structure
---------

Manifest files are plain text files with the following format:

.. code::

    <type> <filename> <size> <hash-type> <hash> [<hash-type> <hash> ...]

.. list-table:: Members
   :widths: 25 75

   * - ``type``
     - The type of the file. Supported types are ``DIST`` (for remote package sources) and ``LINK`` and ``MISC`` (used internally for ``CONTENTS`` files in the package DB).
   * - ``filename``
     - The name of the file the manifest entry references.
   * - ``size``
     - The size of the file as a decimal number, in bytes
   * - ``hash-type``
     - One of the supported hash types listed below
   * - ``hash``
     - The hash of the file as a hexadecimal number, matching the preceeding hash type.

Supported Hash Types
--------------------

The hashes currently supported by portmod are:

- BLAKE2B
- BLAKE3 (recommended for performance)
- MD5
- SHA256 (SHA-2)
- SHA512 (SHA-2)

External Resources
-------------------

https://wiki.gentoo.org/wiki/Repository_format/package/Manifest
