# Change Log

Newest entries last. Each milestone gets a dated entry that matches the roadmap status and the GitHub issue comments.

## 2026-10-18

- Adopted the UBC-FRESH dev workflow in this repository. The parent issue is #1 (P0), and its
  tasks are P0.1 to P0.9 on #2 to #10, linked as sub-issues. The phase branch is
  `feature/p0-bootstrap-scaffold`.
- Added the governance and public surfaces (P0.1, #2): `LICENSE` under UBC FRESH Lab,
  `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `CITATION.cff`, and a rewritten `README.md`.
- Added the agent contract and planning surfaces (P0.2, #3): `AGENTS.md`, `ROADMAP.md`,
  `CHANGE_LOG.md`, and `notes/` with its index and the first ADRs.
- Added the workflow validator and the green dashboard (P0.3, #4) from the UBC-FRESH seed:
  `scripts/check_workflow.py` and `scripts/dashboard.py`.
- Added the quality gates and CI (P0.4, #5): `pyproject.toml` with ruff, mypy strict, and the
  coverage gate; `requirements-dev.txt`; `.pre-commit-config.yaml`; the CI and docs workflows;
  and the phase and task issue templates.
- Added the Sphinx documentation site (P0.5, #6): `docs/conf.py`, `docs/index.rst`,
  `docs/llms.txt`, the install, usage, configuration, and deployment guides, the architecture
  reference, and the session protocol page.
- Replaced the ad-hoc container code with a typed service layer (P0.6, #7). `Settings` reads the
  environment, and the deployment limit is now 50 slots on host ports 8101 to 8150. The pure
  naming helpers, the `LxdBackend` protocol, `PylxdBackend`, and `HubManager` hold the rules.
  The bugs in the old `routes.py` are gone: the duplicate dictionary keys, the unreachable
  branch, the shadowed `config_class`, and the container-number parsing that assumed two digits.
- Hardened the HTTP API (P0.7, #8). The blueprint factory injects the manager, request bodies are
  validated, and `HubError` subclasses map to 400, 404, and 409. The `/config` route no longer
  returns the whole Flask config, and `POST /start/<name>` now matches what the front end calls.
- Added the application test suite (P0.8, #9): settings, naming helpers, `HubManager` over an
  in-memory backend, `PylxdBackend` over a fake `pylxd` module, and the API through the Flask
  test client. The coverage gate is 95 percent branch coverage of `scripts/` and `web_service/`.
- Dashboard result for this entry, from `python scripts/dashboard.py`: all gates green, with the
  framework and application tests passing and branch coverage at or above the gate.
- Queued Phase 0 for approval (P0.9, #10). Pull request #11 held `feature/p0-bootstrap-scaffold`
  at `bf5b14a`, with the close-out report in `notes/reports/p0-closeout.md` (report commit
  `aa95946`). CI run 39162260138 was green in all three jobs on `bf5b14a`, and run 39162323911 on
  the report commit. Nothing had merged.
- The maintainer approved the report and the two settings changes. Executed the close-out in order:
  enabled GitHub Pages with `build_type=workflow`; squash-merged PR #11 into `main` as `7f26293`,
  with a squash tree equal to the approved head `aa95946`; deleted the branch; and protected
  `main`, requiring `Quality gates`, `Green dashboard summary`, and `Pre-commit parity`, with force
  pushes and deletions blocked.
- Closed parent #1 with a closeout comment that cites `7f26293`.
- Launched Phase 1 (capacity and operations) from `main` at `7f26293`, on
  `feature/p1-capacity-operations`. Created the parent #12 and the tasks P1.1 (#13) and P1.2 (#14),
  linked as sub-issues. The roadmap records P0 as `complete` and P1 as `active`. P1.1 starts in a
  later move.
- Started P1.1 (#13). Added `HubManager.capacity()` and `HubManager.health()`, and the
  `GET /health` and `GET /capacity` routes. A transport error at the pylxd boundary is now
  translated to a `BackendError`, so a failed read or write returns a JSON 502 instead of an HTML
  500. New tests cover the helpers, both routes, and the error translation. The dashboard is green
  with 219 tests and 99.74 percent branch coverage.
