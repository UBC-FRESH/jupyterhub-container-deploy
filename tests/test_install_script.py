"""Integration tests for the install and upgrade script.

The tests run ``scripts/install.sh`` with fake ``python3`` and ``systemctl`` commands, so they
exercise the real script without touching the host.
"""

from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

REPO: Path = Path(__file__).resolve().parents[1]
SCRIPT: Path = REPO / "scripts" / "install.sh"

FAKE_PYTHON: str = """#!/usr/bin/env bash
printf 'python %s\\n' "$*" >> "$LOG"
if [ "${1:-}" = "-m" ] && [ "${2:-}" = "venv" ]; then
  mkdir -p "${3}/bin"
  ln -sf "$0" "${3}/bin/python"
fi
exit 0
"""

FAKE_SYSTEMCTL: str = """#!/usr/bin/env bash
printf 'systemctl %s\\n' "$*" >> "$LOG"
if [ "${1:-}" = "is-enabled" ]; then
  if [ -f "$STATE" ]; then exit 0; else exit 1; fi
fi
if [ "${1:-}" = "enable" ]; then
  touch "$STATE"
fi
exit 0
"""


def write_executable(path: Path, text: str) -> None:
    """Write an executable shell script.

    Parameters
    ----------
    path : Path
        File to write.
    text : str
        Script contents.
    """
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)


def make_env(tmp_path: Path) -> dict[str, str]:
    """Build the environment and fake commands for one test.

    Parameters
    ----------
    tmp_path : Path
        Temporary directory for the fake commands and the install target.

    Returns
    -------
    dict of str to str
        The environment for the script.
    """
    bindir = tmp_path / "bin"
    bindir.mkdir()
    write_executable(bindir / "python3", FAKE_PYTHON)
    write_executable(bindir / "systemctl", FAKE_SYSTEMCTL)
    env = dict(os.environ)
    env.update(
        {
            "PATH": f"{bindir}:{env['PATH']}",
            "JHD_APP_DIR": str(tmp_path / "app"),
            "JHD_UNIT_DEST": str(tmp_path / "unit.service"),
            "JHD_PYTHON": str(bindir / "python3"),
            "JHD_SYSTEMCTL": str(bindir / "systemctl"),
            "LOG": str(tmp_path / "log"),
            "STATE": str(tmp_path / "enabled"),
        }
    )
    return env


def run_install(env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    """Run the install script.

    Parameters
    ----------
    env : dict of str to str
        Environment for the script.
    *args : str
        Arguments passed to the script.

    Returns
    -------
    subprocess.CompletedProcess of str
        The finished process.
    """
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def log_lines(env: dict[str, str]) -> str:
    """Return the fake-command log, or an empty string when it was never written.

    Parameters
    ----------
    env : dict of str to str
        Environment that names the log file.

    Returns
    -------
    str
        The log contents.
    """
    path = Path(env["LOG"])
    return path.read_text(encoding="utf-8") if path.exists() else ""


def test_dry_run_prints_the_plan_and_changes_nothing(tmp_path: Path) -> None:
    """The default mode prints the plan and creates no files."""
    env = make_env(tmp_path)
    result = run_install(env, "--dry-run")
    assert result.returncode == 0
    assert "-m venv" in result.stdout
    assert "systemctl enable" in result.stdout
    assert not (tmp_path / "app" / ".venv").exists()
    assert not (tmp_path / "unit.service").exists()


def test_apply_provisions_the_environment(tmp_path: Path) -> None:
    """The apply mode creates the venv, installs the unit, and enables the service."""
    env = make_env(tmp_path)
    result = run_install(env, "--apply")
    assert result.returncode == 0
    assert (tmp_path / "app" / ".venv" / "bin" / "python").exists()
    assert (tmp_path / "unit.service").exists()
    log = log_lines(env)
    assert "systemctl daemon-reload" in log
    assert "systemctl enable --now jupyterhub-container-deploy" in log


def test_apply_is_idempotent(tmp_path: Path) -> None:
    """A second apply runs no state-changing step again and reports the existing state."""
    env = make_env(tmp_path)
    run_install(env, "--apply")
    result = run_install(env, "--apply")
    assert result.returncode == 0
    assert "already present" in result.stdout
    assert "already up to date" in result.stdout
    assert "already enabled" in result.stdout
    log = log_lines(env)
    assert log.count("-m venv") == 1
    assert log.count("daemon-reload") == 1
    assert log.count("enable --now") == 1


def test_unknown_argument_is_rejected(tmp_path: Path) -> None:
    """An unknown argument exits with status 2."""
    result = run_install(make_env(tmp_path), "--bogus")
    assert result.returncode == 2


def test_help_exits_zero(tmp_path: Path) -> None:
    """The help flag prints the usage and exits with status 0."""
    result = run_install(make_env(tmp_path), "--help")
    assert result.returncode == 0
    assert "Usage:" in result.stdout
