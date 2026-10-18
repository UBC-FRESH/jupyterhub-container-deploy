Install
=======

The service runs on the FRESH lab host, next to the LXD daemon it drives. This page covers a
development checkout. Production deployment is in :doc:`deployment`.

Prerequisites
-------------

- Python 3.11 or newer.
- LXD, reachable through the local socket. The service talks to it with ``pylxd``.
- A template container named ``jh-template`` (or another name set through
  ``JHD_TEMPLATE_CONTAINER``). New hubs are copied from it.
- Read access to the LXD socket for the user that runs the service.

Check out and install
---------------------

.. code-block:: bash

   git clone https://github.com/UBC-FRESH/jupyterhub-container-deploy.git
   cd jupyterhub-container-deploy
   python -m venv .venv
   . .venv/bin/activate
   python -m pip install -r requirements.txt

For development, add the tooling:

.. code-block:: bash

   python -m pip install -r requirements-dev.txt
   pre-commit install

Run it
------

.. code-block:: bash

   python run.py

The development server listens on ``127.0.0.1:5000``. Open it in a browser to reach the
dashboard, or call the API directly. See :doc:`usage` for the endpoints.

Check the environment
---------------------

The dashboard runs every quality gate and must be green before any commit:

.. code-block:: bash

   python scripts/dashboard.py

If LXD is not running, the dashboard still passes: the tests never need a live daemon.
