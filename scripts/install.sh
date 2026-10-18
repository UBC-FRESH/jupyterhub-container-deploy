#!/usr/bin/env bash
#
# Idempotent install and upgrade for the JupyterHub container deployment service.
#
# The script creates the virtual environment, installs the pinned requirements, installs the
# systemd unit when it changed, and enables the service when it is not enabled. A second run
# changes nothing and reports what was already in place.
#
# Usage:
#   scripts/install.sh --dry-run    print the plan and run no state-changing command (default)
#   scripts/install.sh --apply      carry out the plan
#
# Paths and commands are overridable for testing:
#   JHD_APP_DIR, JHD_UNIT_DEST, JHD_PYTHON, JHD_SYSTEMCTL
#
# The script never restarts a running service, so an upgrade does not interrupt a request.

set -euo pipefail

SERVICE_NAME="jupyterhub-container-deploy"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_DIR="${JHD_APP_DIR:-/opt/${SERVICE_NAME}}"
UNIT_SRC="${REPO_DIR}/scripts/${SERVICE_NAME}.service"
UNIT_DEST="${JHD_UNIT_DEST:-/etc/systemd/system/${SERVICE_NAME}.service}"
VENV="${APP_DIR}/.venv"
PYTHON="${JHD_PYTHON:-python3}"
SYSTEMCTL="${JHD_SYSTEMCTL:-systemctl}"
MODE="dry-run"

usage() {
    sed -n '2,18p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

run() {
    printf '+ %s\n' "$*"
    if [ "${MODE}" = "apply" ]; then
        "$@"
    fi
}

while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run) MODE="dry-run" ;;
        --apply) MODE="apply" ;;
        -h | --help)
            usage
            exit 0
            ;;
        *)
            printf 'error: unknown argument: %s\n' "$1" >&2
            exit 2
            ;;
    esac
    shift
done

if [ "${MODE}" = "apply" ] && ! command -v "${PYTHON}" >/dev/null 2>&1; then
    printf 'error: %s is not on the path\n' "${PYTHON}" >&2
    exit 2
fi

printf 'Install plan for %s (%s)\n' "${SERVICE_NAME}" "${MODE}"
printf '  app dir: %s\n' "${APP_DIR}"
printf '  unit:    %s\n' "${UNIT_DEST}"

if [ -d "${VENV}" ]; then
    printf '  venv:    already present at %s\n' "${VENV}"
else
    run "${PYTHON}" -m venv "${APP_DIR}/.venv"
fi

run "${VENV}/bin/python" -m pip install --upgrade pip
run "${VENV}/bin/python" -m pip install -r "${REPO_DIR}/requirements.txt"

unit_changed=0
if [ -f "${UNIT_DEST}" ] && cmp -s "${UNIT_SRC}" "${UNIT_DEST}"; then
    printf '  unit:    already up to date\n'
else
    run install -m 0644 "${UNIT_SRC}" "${UNIT_DEST}"
    unit_changed=1
fi

if [ "${unit_changed}" = "1" ]; then
    run "${SYSTEMCTL}" daemon-reload
fi

if "${SYSTEMCTL}" is-enabled --quiet "${SERVICE_NAME}" 2>/dev/null; then
    printf '  service: already enabled\n'
else
    run "${SYSTEMCTL}" enable --now "${SERVICE_NAME}"
fi

printf 'Done (%s).\n' "${MODE}"
