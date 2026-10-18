"""Tests for the shared-token authentication."""

from __future__ import annotations

from flask import Flask
from flask.testing import FlaskClient

from tests.fakes import FakeBackend
from web_service import create_app
from web_service.config import Settings
from web_service.lxd_utils import Hub, HubManager

TOKEN = "s3cret-token"


def build_app(token: str) -> Flask:
    """Build an application with a given auth token.

    Parameters
    ----------
    token : str
        Shared token. Empty disables authentication.

    Returns
    -------
    Flask
        The configured application.
    """
    settings = Settings(auth_token=token)
    backend = FakeBackend([Hub("jupyterhub01", "Running", "one")])
    manager = HubManager(
        backend,
        max_deploy=settings.max_deploy,
        host_port_base=settings.host_port_base,
        container_port=settings.container_port,
        template_container=settings.template_container,
        container_prefix=settings.container_prefix,
        archive_prefix=settings.archive_prefix,
    )
    return create_app(settings, manager)


def client_for(token: str) -> FlaskClient:
    """Return a test client for an application with a token.

    Parameters
    ----------
    token : str
        Shared token.

    Returns
    -------
    FlaskClient
        The test client.
    """
    return build_app(token).test_client()


def test_authentication_is_disabled_without_a_token() -> None:
    """An empty token leaves the API open."""
    assert client_for("").get("/list").status_code == 200


def test_protected_route_requires_a_token() -> None:
    """A request without a credential is rejected with 401."""
    response = client_for(TOKEN).get("/list")
    assert response.status_code == 401
    assert response.get_json()["error"] == "authentication required"


def test_health_probe_is_open() -> None:
    """The health probe answers without a credential."""
    assert client_for(TOKEN).get("/health").status_code == 200


def test_dashboard_redirects_to_login() -> None:
    """A browser request to the root is redirected to the login form."""
    response = client_for(TOKEN).get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_login_form_renders() -> None:
    """The login page is reachable without a credential."""
    response = client_for(TOKEN).get("/login")
    assert response.status_code == 200
    assert b"Access token" in response.data


def test_bearer_token_grants_access() -> None:
    """A correct bearer token is accepted."""
    response = client_for(TOKEN).get("/list", headers={"Authorization": f"Bearer {TOKEN}"})
    assert response.status_code == 200


def test_wrong_bearer_token_is_rejected() -> None:
    """A wrong bearer token is rejected with 401."""
    response = client_for(TOKEN).get("/list", headers={"Authorization": "Bearer nope"})
    assert response.status_code == 401


def test_login_with_the_form_token_sets_a_cookie() -> None:
    """A correct form token sets the cookie and the cookie grants access."""
    client = client_for(TOKEN)
    response = client.post("/login", data={"token": TOKEN})
    assert response.status_code == 302
    assert client.get("/list").status_code == 200


def test_login_with_a_json_token_sets_a_cookie() -> None:
    """A correct JSON token is accepted too."""
    client = client_for(TOKEN)
    assert client.post("/login", json={"token": TOKEN}).status_code == 302


def test_login_with_a_wrong_token_is_rejected() -> None:
    """A wrong token is rejected with 401."""
    response = client_for(TOKEN).post("/login", data={"token": "nope"})
    assert response.status_code == 401


def test_logout_clears_access() -> None:
    """Logout removes the cookie, so the next request is rejected."""
    client = client_for(TOKEN)
    client.post("/login", data={"token": TOKEN})
    client.get("/logout")
    assert client.get("/list").status_code == 401
