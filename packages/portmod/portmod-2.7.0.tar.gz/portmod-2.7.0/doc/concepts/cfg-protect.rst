.. _cfg-protect:

Configuration Protection
========================

For certain files in the prefix, and all files outside the prefix, portmod will not blindly overwrite them when installing, and will not allow modules to overwrite them. This helps nicely handle changes to files the user has manually modified.

Instead, these writes will be diverted to a different file, and the changes will be displayed to the user when they run ``portmod <prefix> cfg-update``.

Portmod has a simple builtin tool to accept or reject the changes, and you can get it to launch a custom merge tool by setting the :ref:`MERGE_TOOL` configuration variable in :ref:`portmod.conf`.

.. versionchanged:: 2.6

   Portmod no longer runs cfg-update automatically after merges, to avoid covering up important information which may be displayed after a merge.
