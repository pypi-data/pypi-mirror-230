.. _profile.user:

profile.user
============

The user profile directory can be used to customize your :ref:`Profile <concepts-profiles>`. This is recommended only for advanced users.

You can place configuration files which are restricted to profiles (see :ref:`profiles` in the developer guide) inside this directory, which is treated as a profile directory. It loads last, so any profile configuration here will override prior settings from your profile.

Note that changing certain profile settings can break your prefix as some settings are not designed to be changed on the fly (such as those which control the filesystem layout).
