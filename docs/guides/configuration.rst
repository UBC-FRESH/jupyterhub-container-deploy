Configuration
=============

The service reads its settings from the environment at startup. Every numeric setting has a
default that matches the lab host, and an invalid value fails fast at startup rather than at the
first request.

Settings
--------

.. list-table::
   :header-rows: 1
   :widths: 34 16 50

   * - Variable
     - Default
     - Purpose
   * - ``JHD_MAX_DEPLOY``
     - ``50``
     - Number of deployment slots, from 1 to 99.
   * - ``JHD_HOST_PORT_BASE``
     - ``8100``
     - First published host port. Slot ``n`` is ``base + n``.
   * - ``JHD_CONTAINER_PORT``
     - ``8000``
     - Port that JupyterHub listens on inside a container.
   * - ``JHD_TEMPLATE_CONTAINER``
     - ``jh-template``
     - Source container that new hubs are copied from.
   * - ``JHD_CONTAINER_PREFIX``
     - ``jupyterhub``
     - Prefix of a live hub container name.
   * - ``JHD_ARCHIVE_PREFIX``
     - ``jh-archive``
     - Prefix of an archived hub container name.
   * - ``JHD_APPLICATION_ROOT``
     - ``/jupyterhub-container-deploy``
     - URL prefix that a reverse proxy mounts the service under.
   * - ``JHD_LXD_ENDPOINT``
     - (empty)
     - LXD socket endpoint. Empty selects the ``pylxd`` default.
   * - ``JHD_AUTH_TOKEN``
     - (empty)
     - Shared token for the dashboard and the API. Empty disables authentication, for local
       development only; set it in production.
   * - ``JHD_ENV``
     - (empty)
     - ``development`` or ``dev`` enables debug mode. ``FLASK_ENV`` is a fallback.

Validation rules
----------------

- ``JHD_MAX_DEPLOY`` must be between 1 and 99.
- ``JHD_HOST_PORT_BASE`` must be between 1 and 65535, and ``base + max_deploy`` must not exceed
  65535.
- ``JHD_CONTAINER_PORT`` must be between 1 and 65535.

Example
-------

.. code-block:: bash

   export JHD_MAX_DEPLOY=50
   export JHD_HOST_PORT_BASE=8100
   python run.py
