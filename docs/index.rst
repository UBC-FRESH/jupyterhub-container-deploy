JupyterHub Container Deploy
===========================

A Flask service that manages JupyterHub LXD containers on the FRESH lab host. It creates,
starts, stops, archives, and restores hubs, and publishes each one on a host port. It manages
up to fifty containers at a time, on host ports 8101 to 8150.

This site is the RTFM surface for the project. Agents read the relevant page before they act,
and cite it in their reports. Start with the repository's ``AGENTS.md`` and ``ROADMAP.md``.

.. toctree::
   :maxdepth: 2
   :caption: Guides

   guides/install
   guides/usage
   guides/configuration
   guides/deployment
   guides/operations
   guides/access

.. toctree::
   :maxdepth: 2
   :caption: Reference

   reference/architecture

.. toctree::
   :maxdepth: 2
   :caption: Agents

   agents/session-protocol

.. toctree::
   :maxdepth: 2
   :caption: API

   api/index

Machine readers can start from ``llms.txt`` at the root of the published site.
