Usage
=====

The service exposes a small JSON API and a dashboard page. The dashboard calls the same API.

Container lifecycle
-------------------

A *slot* is a number from 1 to ``JHD_MAX_DEPLOY`` (50 by default). Slot ``n`` maps to the
container name ``jupyterhub<n>`` (zero-padded) and the host port ``JHD_HOST_PORT_BASE + n``
(``8101`` to ``8150`` by default).

- **Create.** The service copies the template container, starts it, and adds a proxy device that
  publishes the container port on the host. It uses the lowest free slot.
- **Start and stop.** A stopped hub keeps its slot and its port.
- **Archive.** A stopped hub is renamed to ``jh-archive-<tag>``. The tag must be unique.
- **Deploy an archive.** The archive is renamed into the lowest free slot, given a proxy device,
  and started.

HTTP API
--------

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Method and path
     - Purpose
   * - ``GET /max-deploy``
     - The number of deployment slots.
   * - ``GET /config``
     - The public settings, without the LXD endpoint.
   * - ``GET /list``
     - The live hubs, in slot order.
   * - ``GET /list-archived``
     - The stopped archives.
   * - ``GET /check-archive-tag/<tag>``
     - Whether an archive tag is already in use.
   * - ``POST /start``
     - Create a hub. Body: ``{"description": "..."}``.
   * - ``POST /start/<name>``
     - Start a stopped hub.
   * - ``POST /stop/<name>``
     - Stop a running hub.
   * - ``POST /archive/<name>``
     - Archive a stopped hub. Body: ``{"tag": "..."}``.
   * - ``POST /deploy-archived/<name>``
     - Deploy an archive into a free slot.
   * - ``GET /``
     - The dashboard page.

Errors
------

An error is a JSON object ``{"error": "..."}`` with the matching status code: ``400`` for a
rejected input, ``404`` for a missing container, ``409`` for a state conflict (a full set of
slots, a hub that is already running, a tag that is taken), and ``502`` for a backend failure.

Example
-------

.. code-block:: bash

   curl -s -X POST -H 'Content-Type: application/json' \
     -d '{"description": "spring cohort"}' http://127.0.0.1:5000/start
