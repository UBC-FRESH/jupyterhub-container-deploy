"""Tests for the HTTP API, driven through the Flask test client."""

from __future__ import annotations

from flask import Flask
from flask.testing import FlaskClient

from tests.fakes import FailingBackend, FakeBackend
from web_service import create_app
from web_service.config import Settings
from web_service.lxd_utils import Hub, HubManager


def build_app(backend: FakeBackend, settings: Settings | None = None) -> Flask:
    """Build an application over a fake backend.

    Parameters
    ----------
    backend : FakeBackend
        The in-memory backend.
    settings : Settings or None, optional
        Settings to use. ``None`` builds the defaults.

    Returns
    -------
    Flask
        The configured application.
    """
    resolved = settings if settings is not None else Settings()
    manager = HubManager(
        backend,
        max_deploy=resolved.max_deploy,
        host_port_base=resolved.host_port_base,
        container_port=resolved.container_port,
        template_container=resolved.template_container,
        container_prefix=resolved.container_prefix,
        archive_prefix=resolved.archive_prefix,
    )
    return create_app(resolved, manager)


def seed_backend() -> FakeBackend:
    """Build a backend with two live hubs and one archive.

    Returns
    -------
    FakeBackend
        The seeded backend.
    """
    return FakeBackend(
        [
            Hub("jupyterhub01", "Running", "one"),
            Hub("jupyterhub03", "Stopped", "three"),
            Hub("jh-archive-old", "Stopped", "old"),
        ]
    )


def client_for(backend: FakeBackend) -> FlaskClient:
    """Return a test client for an application over a backend.

    Parameters
    ----------
    backend : FakeBackend
        The backend to serve.

    Returns
    -------
    FlaskClient
        The test client.
    """
    return build_app(backend).test_client()


def test_max_deploy_reports_the_slot_count() -> None:
    """The endpoint returns the configured number of slots."""
    response = client_for(seed_backend()).get("/max-deploy")
    assert response.status_code == 200
    assert response.get_json() == 50


def test_config_hides_the_endpoint() -> None:
    """The public config never exposes the LXD endpoint."""
    payload = client_for(seed_backend()).get("/config").get_json()
    assert "lxd_endpoint" not in payload
    assert payload["max_deploy"] == 50


def test_health_reports_ok_when_the_backend_answers() -> None:
    """A reachable backend yields a 200 with the slot counts."""
    response = client_for(seed_backend()).get("/health")
    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "ok"
    assert body["backend"] == "reachable"
    assert body["total_slots"] == 50


def test_health_reports_503_when_the_backend_fails() -> None:
    """An unreachable backend yields a 503 and an unhealthy status."""
    response = client_for(FailingBackend()).get("/health")
    assert response.status_code == 503
    assert response.get_json()["status"] == "unhealthy"


def test_capacity_reports_the_slot_usage() -> None:
    """The capacity route reports the used, free, and total slots."""
    response = client_for(seed_backend()).get("/capacity")
    assert response.status_code == 200
    assert response.get_json() == {"used": 2, "free": 48, "total": 50}


def test_list_returns_live_hubs() -> None:
    """The live list holds the two running or stopped hubs, in slot order."""
    names = [hub["name"] for hub in client_for(seed_backend()).get("/list").get_json()]
    assert names == ["jupyterhub01", "jupyterhub03"]


def test_list_archived_returns_the_archive() -> None:
    """The archive list holds the stopped archive container."""
    names = [hub["name"] for hub in client_for(seed_backend()).get("/list-archived").get_json()]
    assert names == ["jh-archive-old"]


def test_check_archive_tag_reports_existence() -> None:
    """A taken tag reports true and a free tag reports false."""
    client = client_for(seed_backend())
    assert client.get("/check-archive-tag/old").get_json() == {"exists": True}
    assert client.get("/check-archive-tag/new").get_json() == {"exists": False}


def test_start_creates_a_hub_in_the_lowest_slot() -> None:
    """Creating a hub returns its path and records the port."""
    backend = seed_backend()
    response = client_for(backend).post("/start", json={"description": "new"})
    assert response.status_code == 200
    assert response.get_json() == "/jupyterhub02"
    assert backend.created[0]["host_port"] == 8102


def test_start_requires_a_json_object() -> None:
    """A missing body is a 400."""
    response = client_for(seed_backend()).post("/start")
    assert response.status_code == 400
    assert "JSON object" in response.get_json()["error"]


def test_start_requires_a_description() -> None:
    """A body without a description is a 400."""
    response = client_for(seed_backend()).post("/start", json={"other": 1})
    assert response.status_code == 400
    assert "description is required" in response.get_json()["error"]


def test_start_named_hub_starts_a_stopped_hub() -> None:
    """The named start route starts a stopped hub."""
    backend = seed_backend()
    response = client_for(backend).post("/start/jupyterhub03")
    assert response.status_code == 200
    assert backend.started == ["jupyterhub03"]


def test_start_named_hub_conflicts_when_running() -> None:
    """Starting a running hub is a 409."""
    response = client_for(seed_backend()).post("/start/jupyterhub01")
    assert response.status_code == 409


def test_stop_stops_a_running_hub() -> None:
    """The stop route stops a running hub."""
    backend = seed_backend()
    response = client_for(backend).post("/stop/jupyterhub01")
    assert response.status_code == 200
    assert backend.stopped == ["jupyterhub01"]


def test_stop_unknown_hub_is_a_404() -> None:
    """A missing container is a 404 with a JSON error."""
    response = client_for(seed_backend()).post("/stop/jupyterhub99")
    assert response.status_code == 404
    assert "not found" in response.get_json()["error"]


def test_archive_renames_a_stopped_hub() -> None:
    """Archiving a stopped hub returns the new name."""
    backend = seed_backend()
    response = client_for(backend).post("/archive/jupyterhub03", json={"tag": "spring"})
    assert response.status_code == 200
    assert backend.renamed == [("jupyterhub03", "jh-archive-spring")]


def test_archive_requires_a_tag() -> None:
    """A body without a tag is a 400."""
    response = client_for(seed_backend()).post("/archive/jupyterhub03", json={})
    assert response.status_code == 400
    assert "tag is required" in response.get_json()["error"]


def test_archive_rejects_a_bad_tag() -> None:
    """An invalid tag is a 400."""
    response = client_for(seed_backend()).post("/archive/jupyterhub03", json={"tag": "bad tag"})
    assert response.status_code == 400


def test_deploy_archived_starts_the_new_hub() -> None:
    """Deploying an archive renames it into a slot and starts it."""
    backend = seed_backend()
    response = client_for(backend).post("/deploy-archived/jh-archive-old")
    assert response.status_code == 200
    assert backend.started == ["jupyterhub02"]


def test_index_renders_the_dashboard() -> None:
    """The root route serves the dashboard page."""
    response = client_for(seed_backend()).get("/")
    assert response.status_code == 200
    assert b"JupyterHub Deployment Dashboard" in response.data
