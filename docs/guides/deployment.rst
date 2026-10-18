Deployment
==========

The service runs under ``gunicorn`` behind a reverse proxy, managed by ``systemd``. The unit
template is in ``scripts/jupyterhub-container-deploy.service``.

The unit
--------

The unit runs ``gunicorn`` on ``127.0.0.1:5000`` from the checkout's virtual environment:

.. code-block:: ini

   [Service]
   WorkingDirectory=/opt/jupyterhub-container-deploy
   ExecStart=/opt/jupyterhub-container-deploy/.venv/bin/gunicorn -b 127.0.0.1:5000 run:app
   Restart=always

Install and upgrade script
--------------------------

``scripts/install.sh`` provisions a host in one command and is idempotent. It creates the virtual
environment, installs the pinned requirements, installs the unit when it changed, and enables the
service when it is not enabled. It never restarts a running service, so an upgrade does not
interrupt a request.

Print the plan first, then apply it:

.. code-block:: bash

   scripts/install.sh --dry-run
   sudo scripts/install.sh --apply

A second run reports what was already in place and runs no state-changing command.

The manual equivalent, if you prefer it:

.. code-block:: bash

   sudo cp scripts/jupyterhub-container-deploy.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now jupyterhub-container-deploy

Reverse proxy
-------------

``nginx/nginx.conf`` publishes the service on a dedicated hostname at the site root. Serving at
the root keeps the login redirect and the dashboard's relative URLs correct; a path prefix would
break them, because the application does not rewrite its URLs for a prefix.

The block proxies to ``127.0.0.1:5000`` and forwards the host, client, and scheme headers that the
application's ``ProxyFix`` middleware reads. Set ``server_name`` for the host, then install it:

.. code-block:: bash

   sudo cp nginx/nginx.conf /etc/nginx/sites-available/jupyterhub-container-deploy
   sudo ln -sf /etc/nginx/sites-available/jupyterhub-container-deploy /etc/nginx/sites-enabled/
   sudo nginx -t && sudo systemctl reload nginx

The service sets an ``HttpOnly`` cookie for the dashboard, so add a TLS server block and serve it
over HTTPS in production.

Restart discipline
------------------

The dashboard runs as a service on the lab host. Do not restart it from a task unless the task is
about the service itself, and never while a request could be in flight. Record a settings change
in the changelog and the close-out report before it is applied.
