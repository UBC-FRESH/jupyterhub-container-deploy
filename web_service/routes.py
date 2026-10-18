"""HTTP API for the JupyterHub container deployment service.

The blueprint holds no state. Every handler reads the settings and the
:class:`~web_service.lxd_utils.HubManager` from the Flask application, so the same
blueprint serves a real LXD backend in production and an in-memory backend in tests. A
:class:`~web_service.lxd_utils.HubError` raised by the manager is turned into a JSON error
response with the status code that the error carries.
"""

from __future__ import annotations

from typing import cast

from flask import Blueprint, Flask, Response, current_app, jsonify, render_template, request

from .config import Settings
from .lxd_utils import Hub, HubError, HubManager, InvalidInputError


def _manager() -> HubManager:
    """Return the hub manager bound to the current application.

    Returns
    -------
    HubManager
        The manager stored in ``app.extensions``.
    """
    return cast("HubManager", current_app.extensions["hub_manager"])


def _settings() -> Settings:
    """Return the settings bound to the current application.

    Returns
    -------
    Settings
        The settings stored in the application config.
    """
    return cast("Settings", current_app.config["SETTINGS"])


def _json_body() -> dict[str, object]:
    """Return the request body as a JSON object.

    Returns
    -------
    dict of str to object
        The parsed body.

    Raises
    ------
    InvalidInputError
        When the body is missing or is not a JSON object.
    """
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise InvalidInputError("a JSON object body is required")
    return data


def _hub_payload(hub: Hub) -> dict[str, str]:
    """Convert a hub record into its JSON payload.

    Parameters
    ----------
    hub : Hub
        The record to convert.

    Returns
    -------
    dict of str to str
        The name, status, and description.
    """
    return {"name": hub.name, "status": hub.status, "description": hub.description}


def create_blueprint() -> Blueprint:
    """Build the application blueprint.

    Returns
    -------
    Blueprint
        A blueprint with every route registered.
    """
    blueprint = Blueprint("main_routes", __name__)

    @blueprint.get("/max-deploy")
    def max_deploy() -> Response:
        """Return the number of deployment slots."""
        return jsonify(_settings().max_deploy)

    @blueprint.get("/config")
    def config() -> Response:
        """Return the public settings as JSON."""
        return jsonify(_settings().public_dict())

    @blueprint.get("/list")
    def list_hubs() -> Response:
        """Return the live hubs."""
        return jsonify([_hub_payload(hub) for hub in _manager().list_hubs()])

    @blueprint.get("/list-archived")
    def list_archived_hubs() -> Response:
        """Return the archived hubs."""
        return jsonify([_hub_payload(hub) for hub in _manager().list_archived()])

    @blueprint.get("/health")
    def health() -> tuple[Response, int]:
        """Report whether the service and its LXD backend are healthy."""
        status = _manager().health()
        body = {
            "status": "ok" if status.healthy else "unhealthy",
            "backend": "reachable" if status.healthy else "unreachable",
            "free_slots": status.free_slots,
            "total_slots": status.total_slots,
        }
        return jsonify(body), 200 if status.healthy else 503

    @blueprint.get("/capacity")
    def capacity() -> Response:
        """Report the deployment-slot usage."""
        usage = _manager().capacity()
        return jsonify({"used": usage.used, "free": usage.free, "total": usage.total})

    @blueprint.get("/check-archive-tag/<tag>")
    def check_archive_tag(tag: str) -> Response:
        """Report whether an archive tag is already in use."""
        return jsonify({"exists": _manager().archive_tag_exists(tag)})

    @blueprint.post("/start")
    def start_new_hub() -> tuple[Response, int]:
        """Create and start a new hub from a description."""
        body = _json_body()
        description = body.get("description")
        if not isinstance(description, str):
            raise InvalidInputError("description is required")
        name = _manager().create_hub(description)
        return jsonify(f"/{name}"), 200

    @blueprint.post("/start/<hub_name>")
    def start_hub(hub_name: str) -> tuple[Response, int]:
        """Start a stopped hub."""
        _manager().start_hub(hub_name)
        return jsonify(f"{hub_name} has been started."), 200

    @blueprint.post("/stop/<hub_name>")
    def stop_hub(hub_name: str) -> tuple[Response, int]:
        """Stop a running hub."""
        _manager().stop_hub(hub_name)
        return jsonify(f"{hub_name} has been stopped."), 200

    @blueprint.post("/deploy-archived/<hub_name>")
    def deploy_archived_hub(hub_name: str) -> tuple[Response, int]:
        """Deploy an archived hub into the lowest free slot."""
        new_name = _manager().deploy_archived(hub_name)
        return jsonify(f"{new_name} has been deployed."), 200

    @blueprint.post("/archive/<hub_name>")
    def archive_hub(hub_name: str) -> tuple[Response, int]:
        """Archive a stopped hub under a tag."""
        body = _json_body()
        tag = body.get("tag")
        if not isinstance(tag, str):
            raise InvalidInputError("tag is required")
        target = _manager().archive_hub(hub_name, tag)
        return jsonify(f"{hub_name} has been archived as {target}."), 200

    @blueprint.get("/")
    def index() -> str:
        """Render the dashboard page."""
        return render_template("index.html")

    return blueprint


def register_error_handlers(app: Flask) -> None:
    """Register the JSON error handler for :class:`HubError`.

    Parameters
    ----------
    app : Flask
        Application to register the handler on.
    """

    @app.errorhandler(HubError)
    def _handle_hub_error(error: HubError) -> tuple[Response, int]:
        return jsonify({"error": str(error)}), error.http_status
