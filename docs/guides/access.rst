Access model
============

The service uses one shared token to protect the dashboard and the API. The decision and its
alternatives are in ``notes/adr/0003-shared-token-authentication.md``.

How to sign in
--------------

- **Dashboard.** Open the service in a browser. An unauthenticated request to ``/`` redirects to
  ``/login``. Enter the token once; the service sets an ``HttpOnly``, ``SameSite=Lax`` cookie and
  the dashboard then loads.
- **API.** Send the token on every request:

  .. code-block:: bash

     curl -s -H "Authorization: Bearer $JHD_AUTH_TOKEN" http://127.0.0.1:5000/list

Sign out by visiting ``/logout``, which clears the cookie.

What is protected
-----------------

Every route is protected by a ``before_request`` check, so a new route is authenticated by
default. The only open routes are:

- ``GET /health``: a liveness probe, so an external monitor needs no token.
- ``GET /login`` and ``GET /logout``: the sign-in and sign-out steps.

Everything else, including ``/list``, ``/capacity``, ``/start``, ``/stop``, ``/archive``, and
``/deploy-archived``, requires the token.

Configuration
-------------

The token is the ``JHD_AUTH_TOKEN`` setting (see :doc:`configuration`). When it is empty,
authentication is disabled; that is intended for local development only. In production, set it to
a long random value and keep it out of tracked files.

Threat boundaries
-----------------

The token protects against a client that can reach the reverse proxy but does not hold the
credential. It does **not** provide:

- **Transport security.** The cookie carries the token, so the service must sit behind TLS. The
  reverse proxy owns TLS termination; the service does not.
- **Per-user identity or an audit trail.** The token is one shared secret. The service cannot say
  which operator made a change.
- **Protection from the host.** Anyone with access to the LXD socket or the host filesystem can
  control the containers directly. The token does not change that.
- **Protection from a leaked token.** A token in a shell history or a log is a full credential.
  Rotate it if it leaks.

Rotating the token
------------------

1. Generate a new value.
2. Update ``JHD_AUTH_TOKEN`` in the service environment.
3. Restart the service deliberately (see :doc:`operations`) and confirm ``GET /health``.
