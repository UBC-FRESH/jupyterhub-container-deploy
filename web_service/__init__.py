"""Application factory for the JupyterHub container deployment service.

:func:`create_app` builds a Flask application with its settings, its hub manager, and its
routes. The manager is injected, so tests pass an in-memory backend and production passes
the LXD backend. Nothing connects to LXD until the first request, so importing the package
never needs a running daemon.
"""

from __future__ import annotations

from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from .auth import install_auth
from .config import Settings
from .lxd_utils import HubManager, PylxdBackend
from .routes import create_blueprint, register_error_handlers

__all__ = ["build_manager", "create_app"]


def build_manager(settings: Settings) -> HubManager:
    """Build the production hub manager from settings.

    Parameters
    ----------
    settings : Settings
        Application settings.

    Returns
    -------
    HubManager
        A manager backed by LXD.
    """
    return HubManager(
        PylxdBackend(settings.lxd_endpoint),
        max_deploy=settings.max_deploy,
        host_port_base=settings.host_port_base,
        container_port=settings.container_port,
        template_container=settings.template_container,
        container_prefix=settings.container_prefix,
        archive_prefix=settings.archive_prefix,
    )


def create_app(
    settings: Settings | None = None,
    manager: HubManager | None = None,
) -> Flask:
    """Create and configure the Flask application.

    Parameters
    ----------
    settings : Settings or None, optional
        Settings to use. ``None`` reads them from the environment.
    manager : HubManager or None, optional
        Hub manager to use. ``None`` builds one on LXD.

    Returns
    -------
    Flask
        The configured application.
    """
    resolved = settings if settings is not None else Settings.from_env()
    app = Flask(__name__)
    # Wrapping wsgi_app is the documented way to trust one reverse proxy; mypy types it as a method.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)  # type: ignore[method-assign]
    app.config["SETTINGS"] = resolved
    app.extensions["hub_manager"] = manager if manager is not None else build_manager(resolved)
    CORS(app)
    app.register_blueprint(create_blueprint())
    register_error_handlers(app)
    install_auth(app, resolved.auth_token)
    return app
