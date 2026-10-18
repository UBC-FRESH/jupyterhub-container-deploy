"""Shared-token authentication for the dashboard and the API.

:func:`install_auth` registers a ``before_request`` check, so every route is protected by
default and only the small open list is exempt. API clients present the token as
``Authorization: Bearer <token>``; the dashboard presents it once at ``/login`` and then carries
it in an ``HttpOnly`` cookie. When the token is empty, authentication is disabled for local
development. See ``notes/adr/0003-shared-token-authentication.md``.
"""

from __future__ import annotations

import secrets

from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue

COOKIE_NAME: str = "jhd_token"
OPEN_PATHS: frozenset[str] = frozenset({"/health", "/login", "/logout"})
BEARER_PREFIX: str = "Bearer "


def _presented_token() -> str | None:
    """Return the token presented on the request, if any.

    Returns
    -------
    str or None
        The bearer token from the ``Authorization`` header, or the cookie value.
    """
    header = request.headers.get("Authorization", "")
    if header.startswith(BEARER_PREFIX):
        return header[len(BEARER_PREFIX) :].strip()
    return request.cookies.get(COOKIE_NAME)


def _submitted_token() -> str | None:
    """Return the token submitted to the login route, if any.

    Returns
    -------
    str or None
        The ``token`` form field, or the ``token`` key of a JSON body.
    """
    form_token = request.form.get("token")
    if form_token is not None:
        return form_token
    payload = request.get_json(silent=True)
    if isinstance(payload, dict):
        value = payload.get("token")
        if isinstance(value, str):
            return value
    return None


def install_auth(app: Flask, token: str) -> None:
    """Register the authentication check and the login and logout routes.

    Parameters
    ----------
    app : Flask
        Application to protect.
    token : str
        Shared token. An empty token disables authentication.
    """
    if not token:
        return

    @app.before_request
    def _require_auth() -> ResponseReturnValue | None:
        if request.path in OPEN_PATHS:
            return None
        presented = _presented_token() or ""
        if secrets.compare_digest(presented, token):
            return None
        if request.method == "GET" and request.path == "/":
            return redirect(url_for("login_form"))
        return jsonify({"error": "authentication required"}), 401

    @app.get("/login")
    def login_form() -> str:
        """Render the login form."""
        return render_template("login.html")

    @app.post("/login")
    def login_submit() -> ResponseReturnValue:
        """Validate a submitted token and set the session cookie."""
        submitted = _submitted_token()
        if submitted is None or not secrets.compare_digest(submitted, token):
            return jsonify({"error": "invalid token"}), 401
        response = redirect(url_for("main_routes.index"))
        response.set_cookie(COOKIE_NAME, token, httponly=True, samesite="Lax")
        return response

    @app.get("/logout")
    def logout() -> ResponseReturnValue:
        """Clear the session cookie."""
        response = redirect(url_for("login_form"))
        response.delete_cookie(COOKIE_NAME)
        return response
