Operations runbook
==================

Routine tasks and incident steps for the JupyterHub container deployment service. The
endpoints are described in :doc:`usage`; the settings are in :doc:`configuration`.

Routine tasks
-------------

Create a hub, which lands in the lowest free slot:

.. code-block:: bash

   curl -s -X POST -H 'Content-Type: application/json' \
     -d '{"description": "spring cohort"}' http://127.0.0.1:5000/start

Stop a running hub:

.. code-block:: bash

   curl -s -X POST http://127.0.0.1:5000/stop/jupyterhub07

Start a stopped hub:

.. code-block:: bash

   curl -s -X POST http://127.0.0.1:5000/start/jupyterhub07

Archive a stopped hub under a unique tag:

.. code-block:: bash

   curl -s -X POST -H 'Content-Type: application/json' \
     -d '{"tag": "spring-2026"}' http://127.0.0.1:5000/archive/jupyterhub07

Restore an archive into the lowest free slot:

.. code-block:: bash

   curl -s -X POST http://127.0.0.1:5000/deploy-archived/jh-archive-spring-2026

Check a tag before you use it:

.. code-block:: bash

   curl -s http://127.0.0.1:5000/check-archive-tag/spring-2026

Monitoring
----------

Health, which reports whether the LXD backend answers:

.. code-block:: bash

   curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:5000/health

A ``200`` means the backend answered; a ``503`` means it did not. Capacity, which reports the
slot usage:

.. code-block:: bash

   curl -s http://127.0.0.1:5000/capacity

Full-capacity incident
----------------------

Symptom: a create or restore fails with ``409`` and ``all 50 deployment slots are in use``.

1. Confirm the usage with ``GET /capacity``.
2. List the live hubs with ``GET /list`` and identify the idle ones.
3. Stop and archive an idle hub, which frees its slot:

   .. code-block:: bash

      curl -s -X POST http://127.0.0.1:5000/stop/jupyterhubNN
      curl -s -X POST -H 'Content-Type: application/json' \
        -d '{"tag": "idle-2026-10"}' http://127.0.0.1:5000/archive/jupyterhubNN

4. Retry the create or restore.

If the demand is sustained, raise ``JHD_MAX_DEPLOY`` (up to 99) and restart the service. Confirm
that ``JHD_HOST_PORT_BASE + JHD_MAX_DEPLOY`` stays at or below 65535.

Restart discipline
------------------

The dashboard runs as a service on the lab host. Do not restart ``jupyterhub-container-deploy``
while a request could be in flight. After a settings change, restart deliberately and check
``GET /health``:

.. code-block:: bash

   sudo systemctl restart jupyterhub-container-deploy
   curl -s http://127.0.0.1:5000/health
