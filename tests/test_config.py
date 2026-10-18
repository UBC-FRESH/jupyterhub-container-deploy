"""Tests for the environment-driven application settings."""

from __future__ import annotations

import pytest

from web_service.config import Settings


@pytest.fixture(autouse=True)
def clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove every ``JHD_`` and ``FLASK_ENV`` variable before each test."""
    for name in list(_all_names()):
        monkeypatch.delenv(name, raising=False)


def _all_names() -> tuple[str, ...]:
    """Return the environment names that the settings read."""
    return (
        "JHD_ENV",
        "JHD_MAX_DEPLOY",
        "JHD_HOST_PORT_BASE",
        "JHD_CONTAINER_PORT",
        "JHD_TEMPLATE_CONTAINER",
        "JHD_CONTAINER_PREFIX",
        "JHD_ARCHIVE_PREFIX",
        "JHD_APPLICATION_ROOT",
        "JHD_LXD_ENDPOINT",
        "FLASK_ENV",
    )


def test_defaults_match_the_lab_host() -> None:
    """The defaults allow fifty deployments on ports 8101 to 8150."""
    settings = Settings.from_env()
    assert settings.max_deploy == 50
    assert settings.host_port_base == 8100
    assert settings.container_port == 8000
    assert settings.template_container == "jh-template"
    assert settings.container_prefix == "jupyterhub"
    assert settings.archive_prefix == "jh-archive"
    assert settings.debug is False


def test_max_deploy_is_configurable(monkeypatch: pytest.MonkeyPatch) -> None:
    """``JHD_MAX_DEPLOY`` overrides the slot count."""
    monkeypatch.setenv("JHD_MAX_DEPLOY", "50")
    assert Settings.from_env().max_deploy == 50


def test_non_integer_value_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    """A non-integer setting raises ``ValueError`` at startup."""
    monkeypatch.setenv("JHD_MAX_DEPLOY", "many")
    with pytest.raises(ValueError, match="must be an integer"):
        Settings.from_env()


def test_out_of_range_value_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    """A setting above its maximum raises ``ValueError``."""
    monkeypatch.setenv("JHD_MAX_DEPLOY", "100")
    with pytest.raises(ValueError, match="between 1 and 99"):
        Settings.from_env()


def test_zero_value_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    """A setting below its minimum raises ``ValueError``."""
    monkeypatch.setenv("JHD_CONTAINER_PORT", "0")
    with pytest.raises(ValueError, match="between 1 and 65535"):
        Settings.from_env()


def test_port_range_overflow_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    """A base port plus the slot count must stay inside the port range."""
    monkeypatch.setenv("JHD_HOST_PORT_BASE", "65500")
    monkeypatch.setenv("JHD_MAX_DEPLOY", "50")
    with pytest.raises(ValueError, match="exceeds port 65535"):
        Settings.from_env()


def test_development_environment_enables_debug(monkeypatch: pytest.MonkeyPatch) -> None:
    """``JHD_ENV=development`` turns on debug mode."""
    monkeypatch.setenv("JHD_ENV", "development")
    assert Settings.from_env().debug is True


def test_flask_env_is_a_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """``FLASK_ENV`` selects the environment when ``JHD_ENV`` is unset."""
    monkeypatch.setenv("FLASK_ENV", "dev")
    assert Settings.from_env().debug is True


def test_public_dict_hides_the_lxd_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    """The public settings omit the LXD endpoint and keep the rest."""
    monkeypatch.setenv("JHD_LXD_ENDPOINT", "/var/snap/lxd/common/lxd/unix.socket")
    public = Settings.from_env().public_dict()
    assert "lxd_endpoint" not in public
    assert public["max_deploy"] == 50
