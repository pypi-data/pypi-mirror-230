.. _concepts-profiles:

Profiles
========

Profiles are default game configurations for portmod.

They are used to set default values for various settings. Certain user-relevant settings can be viewed with the ``portmod <prefix> info`` subcommand.

They also specify the mandatory packages in the ``system`` set (see :ref:`sets`), and can provide other metadata such as default :ref:`use-flags` and masked packages (in the same manner as :ref:`package.mask`).
