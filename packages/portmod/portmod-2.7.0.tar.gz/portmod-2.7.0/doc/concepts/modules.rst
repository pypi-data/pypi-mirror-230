.. _concepts-modules:

Modules
=======

Modules can be used to run global updates after package installation has been completed.
This is often used to update configuration files to inform game engines of the locations
of the mods which have been installed,

Module updates can be triggered manually with the ``portmod <prefix> module-update`` subcommand.

.. versionchanged:: 2.6

   Module updates are no longer run as part of the ``cfg-update`` subcommand

For implementing modules, see the :ref:`modules` chapter in the Developer Guide.
