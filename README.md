# JupyterHub Container Deploy

A Flask service that manages JupyterHub LXD containers on the FRESH lab host. It creates,
starts, stops, archives, and restores hubs, and publishes each one on a host port. It
manages up to fifty containers at a time, on host ports 8101 to 8150.

The project follows the [UBC-FRESH dev workflow](https://github.com/UBC-FRESH/ubc-fresh-dev-workflow):
work is planned as phases and tasks in `ROADMAP.md`, mirrored in GitHub issues, and recorded in
`CHANGE_LOG.md`. The agent operating contract is in `AGENTS.md`.

## Status

Phase 0 (bootstrap and hardening) is active. `ROADMAP.md` lists the phases, and the GitHub issues
carry the live status.

## What it does

- Creates a hub by copying the `jh-template` container, starting it, and adding a proxy device
  that publishes its port on the host.
- Starts, stops, and lists hubs.
- Archives a stopped hub under a tag, and deploys an archive back into a free slot.
- Serves a small Bootstrap dashboard and a JSON API.

## Quick start

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
python run.py
```

The development server listens on `127.0.0.1:5000`. The full install, configuration, and
deployment steps are in [the install guide](docs/guides/install.rst).

## Development

```bash
python scripts/dashboard.py
```

The dashboard runs every quality gate: lint, format, strict types, tests with the coverage gate,
the workflow validator, and the docs build. It must be green before every commit. See
[CONTRIBUTING.md](CONTRIBUTING.md).

## Repository map

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Operating contract for coding agents |
| `ROADMAP.md` | Plan of record and issue tracker map |
| `CHANGE_LOG.md` | Dated narrative of changes |
| `docs/` | Sphinx documentation site |
| `notes/` | Decisions (ADRs), reference notes, and reports |
| `web_service/` | Flask app: settings, the LXD service layer, and the routes |
| `run.py` | Development and WSGI entry point |
| `scripts/` | Workflow validator and green dashboard |
| `tests/` | pytest suite for the framework and the application |

## Configuration

The service is configured through environment variables. The most important ones are
`JHD_MAX_DEPLOY` (default `50`), `JHD_HOST_PORT_BASE` (default `8100`), and
`JHD_TEMPLATE_CONTAINER` (default `jh-template`). See
[the configuration guide](docs/guides/configuration.rst).

## License

MIT. See [LICENSE](LICENSE).
