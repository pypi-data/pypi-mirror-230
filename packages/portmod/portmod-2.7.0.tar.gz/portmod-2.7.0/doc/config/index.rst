User Configuration
------------------

These files are found in the ``CONFIG_DIR`` (as displayed by ``portmod <prefix> info``).
This is typically one of the following locations, depending on your platform.

.. list-table::
   :widths: 15 85

   * - Linux
     - ``~/.config/portmod/<prefix>``
   * - Windows
     - ``C:\Documents and Settings\<User>\Application Data\Local Settings\portmod\portmod\<prefix>``
       or
       ``C:\Documents and Settings\<User>\Application Data\portmod\portmod\<prefix>``

.. _config_table:

.. list-table::
   :widths: 30 70
   :header-rows: 0

   * - :ref:`package.accept_license`
     - .. summary:: package.accept_license.rst
   * - :ref:`package.accept_keywords`
     - .. summary:: package.accept_keywords.rst
   * - :ref:`package.mask`
     - .. summary:: package.mask.rst
   * - :ref:`package.use`
     - .. summary:: package.use.rst
   * - :ref:`portmod.conf`
     - .. summary:: portmod.conf.rst
   * - profile
     - The profile symlink points to the first directory of your :ref:`Profile <concepts-profiles>`.
   * - :ref:`profile.user`
     - .. summary:: profile.user.rst
   * - :ref:`repos.cfg`
     - .. summary:: repos.cfg.rst
   * - :ref:`sets <user-sets>`
     - .. summary:: sets.rst

.. toctree::
   :hidden:

   package.accept_license
   package.accept_keywords
   package.mask
   package.use
   portmod.conf
   profile.user
   repos.cfg
   sets
