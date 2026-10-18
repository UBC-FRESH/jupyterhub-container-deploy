"""Application settings for the JupyterHub container deployment service.

Every setting is read from the environment so that the same checkout runs on a laptop and
on the lab server. Each value has a default that matches the FRESH lab host, where the
service manages up to fifty JupyterHub containers. Invalid values fail fast at startup
instead of at the first request.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, fields

DEFAULT_MAX_DEPLOY: int = 50
DEFAULT_HOST_PORT_BASE: int = 8100
DEFAULT_CONTAINER_PORT: int = 8000
DEFAULT_TEMPLATE_CONTAINER: str = "jh-template"
DEFAULT_CONTAINER_PREFIX: str = "jupyterhub"
DEFAULT_ARCHIVE_PREFIX: str = "jh-archive"
DEFAULT_APPLICATION_ROOT: str = "/jupyterhub-container-deploy"
ENV_PREFIX: str = "JHD_"


def _read_int(name: str, default: int, *, minimum: int, maximum: int) -> int:
    """Read an integer setting from the environment and range-check it.

    Parameters
    ----------
    name : str
        Environment variable name, without the ``JHD_`` prefix.
    default : int
        Value returned when the variable is unset or empty.
    minimum : int
        Smallest accepted value, inclusive.
    maximum : int
        Largest accepted value, inclusive.

    Returns
    -------
    int
        The parsed and validated value.

    Raises
    ------
    ValueError
        When the value is not an integer, or falls outside ``[minimum, maximum]``.
    """
    raw = os.environ.get(ENV_PREFIX + name, "")
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{ENV_PREFIX}{name} must be an integer, got {raw!r}") from exc
    if not minimum <= value <= maximum:
        raise ValueError(f"{ENV_PREFIX}{name} must be between {minimum} and {maximum}, got {value}")
    return value


def _read_str(name: str, default: str) -> str:
    """Read a string setting from the environment.

    Parameters
    ----------
    name : str
        Environment variable name, without the ``JHD_`` prefix.
    default : str
        Value returned when the variable is unset or empty.

    Returns
    -------
    str
        The configured value, or the default.
    """
    return os.environ.get(ENV_PREFIX + name, "") or default


@dataclass(frozen=True)
class Settings:
    """Immutable configuration for one running instance of the service.

    Attributes
    ----------
    application_root : str
        URL prefix that a reverse proxy mounts the service under.
    max_deploy : int
        Number of deployment slots, from ``1`` to this value. The lab host runs up to
        fifty, so the default is ``50``.
    host_port_base : int
        First host port. Slot ``n`` is published on ``host_port_base + n``.
    container_port : int
        Port that the JupyterHub process listens on inside each container.
    template_container : str
        Name of the LXD container that new hubs are copied from.
    container_prefix : str
        Prefix of a live hub container name, such as ``jupyterhub``.
    archive_prefix : str
        Prefix of an archived hub container name, such as ``jh-archive``.
    debug : bool
        Whether Flask runs in debug mode.
    lxd_endpoint : str
        LXD socket endpoint. Empty selects the pylxd default.
    auth_token : str
        Shared token that protects the dashboard and the API. Empty disables authentication,
        which is intended for local development only.
    """

    application_root: str = DEFAULT_APPLICATION_ROOT
    max_deploy: int = DEFAULT_MAX_DEPLOY
    host_port_base: int = DEFAULT_HOST_PORT_BASE
    container_port: int = DEFAULT_CONTAINER_PORT
    template_container: str = DEFAULT_TEMPLATE_CONTAINER
    container_prefix: str = DEFAULT_CONTAINER_PREFIX
    archive_prefix: str = DEFAULT_ARCHIVE_PREFIX
    debug: bool = False
    lxd_endpoint: str = ""
    auth_token: str = ""

    @classmethod
    def from_env(cls, env: str | None = None) -> Settings:
        """Build settings from the process environment.

        Parameters
        ----------
        env : str or None, optional
            Overrides the environment selection. ``"development"`` or ``"dev"`` enables
            debug mode. ``None`` reads ``JHD_ENV``, then ``FLASK_ENV``.

        Returns
        -------
        Settings
            The validated settings.

        Raises
        ------
        ValueError
            When a numeric setting is not an integer or falls outside its range.
        """
        name = env or os.environ.get(ENV_PREFIX + "ENV") or os.environ.get("FLASK_ENV") or ""
        debug = name.lower() in {"development", "dev"}
        max_deploy = _read_int("MAX_DEPLOY", DEFAULT_MAX_DEPLOY, minimum=1, maximum=99)
        host_port_base = _read_int(
            "HOST_PORT_BASE", DEFAULT_HOST_PORT_BASE, minimum=1, maximum=65535
        )
        container_port = _read_int(
            "CONTAINER_PORT", DEFAULT_CONTAINER_PORT, minimum=1, maximum=65535
        )
        if host_port_base + max_deploy > 65535:
            raise ValueError(
                f"JHD_HOST_PORT_BASE ({host_port_base}) plus JHD_MAX_DEPLOY "
                f"({max_deploy}) exceeds port 65535"
            )
        return cls(
            application_root=_read_str("APPLICATION_ROOT", DEFAULT_APPLICATION_ROOT),
            max_deploy=max_deploy,
            host_port_base=host_port_base,
            container_port=container_port,
            template_container=_read_str("TEMPLATE_CONTAINER", DEFAULT_TEMPLATE_CONTAINER),
            container_prefix=_read_str("CONTAINER_PREFIX", DEFAULT_CONTAINER_PREFIX),
            archive_prefix=_read_str("ARCHIVE_PREFIX", DEFAULT_ARCHIVE_PREFIX),
            debug=debug,
            lxd_endpoint=_read_str("LXD_ENDPOINT", ""),
            auth_token=_read_str("AUTH_TOKEN", ""),
        )

    def public_dict(self) -> dict[str, object]:
        """Return the settings that are safe to expose over the API.

        Secrets and the LXD endpoint are omitted. The result is JSON-serializable.

        Returns
        -------
        dict of str to object
            Field name to value, for every setting except the secret ones.
        """
        hidden = {"lxd_endpoint", "auth_token"}
        return {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if field.name not in hidden
        }
