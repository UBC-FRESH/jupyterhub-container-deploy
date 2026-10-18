Architecture
============

The application is a small Flask service with three layers. The rules sit in the middle layer, and
the container runtime sits behind a protocol, so the rules are tested without a live LXD daemon.

Layers
------

.. list-table::
   :header-rows: 1
   :widths: 26 74

   * - Module
     - Responsibility
   * - ``web_service/config.py``
     - ``Settings``: an immutable, environment-driven record, with range checks.
   * - ``web_service/lxd_utils.py``
     - Pure naming helpers, the ``Hub`` record, the ``LxdBackend`` protocol, ``PylxdBackend``,
       and ``HubManager``, which holds the business rules.
   * - ``web_service/routes.py``
     - The HTTP blueprint. It reads the manager and settings from the Flask app, validates
       request bodies, and maps errors to status codes.
   * - ``web_service/__init__.py``
     - The application factory. It injects the manager, so tests pass an in-memory backend.

Naming scheme
-------------

- A live hub is ``<container_prefix><NN>``, zero-padded, such as ``jupyterhub07``.
- Its host port is ``host_port_base + NN``, such as ``8107``.
- An archive is ``<archive_prefix>-<tag>``, such as ``jh-archive-spring``.

The slot is parsed with a full-match regular expression, so a name that does not carry a slot is
ignored rather than misread.

Error model
-----------

``HubError`` is the base class. Each subclass carries an ``http_status``:

- ``InvalidInputError`` (400): a value the service cannot accept.
- ``NotFoundError`` (404): a missing container.
- ``ConflictError`` (409): a state conflict, such as a running hub that cannot be started again.
- ``SlotUnavailableError`` (409): every slot is in use.
- ``BackendError`` (502): an unclassified LXD failure.

The application registers one error handler for ``HubError``, so a route raises the error and the
handler shapes the JSON response.

Testing
-------

The suite has the layers that the workflow's testing policy names: unit tests for the pure
helpers, tests for ``HubManager`` over an in-memory ``FakeBackend``, tests for ``PylxdBackend``
over a fake ``pylxd`` module, and API tests through the Flask test client. No test needs a daemon.
