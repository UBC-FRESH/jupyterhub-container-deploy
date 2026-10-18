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
- Completed P1.2 (#14). Wrote `docs/guides/operations.rst`: the routine create, stop, start,
  archive, and restore tasks; the health and capacity checks; the full-capacity incident; and the
  restart discipline. Linked it from the docs index and `docs/llms.txt`. All Phase 1 tasks are
  complete; the phase is ready for its close-out.
- Queued Phase 1 for approval. Pull request #15 held `feature/p1-capacity-operations` at
  `3caafb4`, with the close-out report in `notes/reports/p1-closeout.md` (report commit `f1a2e94`).
  CI run 39163695576 was green in all three jobs on `3caafb4`, and run 39163780752 on the report
  commit. Nothing had merged.
- The maintainer approved the report. Squash-merged PR #15 into `main` as `c9407ca`, with a squash
  tree equal to the approved report head `f1a2e94`; deleted the branch; and closed parent #12 with
  a closeout comment that cites `c9407ca`.
- Launched Phase 2 (API and access control) from `main` at `c9407ca`, on `feature/p2-api-access`.
  Created the parent #16 and the tasks P2.1 (#17) and P2.2 (#18), linked as sub-issues. The
  roadmap records P1 as `complete` and P2 as `active`. P2.1 starts in a later move.
- Started P2.1 (#17). Added shared-token authentication. `JHD_AUTH_TOKEN` protects every route
  except the open list (`/health`, `/login`, `/logout`). API clients use
  `Authorization: Bearer <token>`; the dashboard signs in once at `/login`, which sets an
  `HttpOnly`, `SameSite=Lax` cookie, and `/logout` clears it. An empty token disables
  authentication for local development. The comparison uses `secrets.compare_digest`. The decision
  is ADR 0003. The dashboard is green with 230 tests and 99.50 percent branch coverage.
- Completed P2.2 (#18). Wrote `docs/guides/access.rst`: how to sign in, the protected and open
  routes, the `JHD_AUTH_TOKEN` setting, and the threat boundaries (no TLS, no per-user identity,
  no host protection, and the leaked-token case). Linked it from the docs index and
  `docs/llms.txt`. All Phase 2 tasks are complete; the phase is ready for its close-out.
- Queued Phase 2 for approval. Pull request #19 held `feature/p2-api-access` at `f7e7b9c`, with the
  close-out report in `notes/reports/p2-closeout.md` (report commit `02d97b3`). CI run 39164249244
  was green in all three jobs on `f7e7b9c`, and run 39164335897 on the report commit.
- The maintainer approved the report. Squash-merged PR #19 into `main` as `955b5ff`, with a squash
  tree equal to the approved report head `02d97b3`; deleted the branch; and closed parent #16 with
  a closeout comment that cites `955b5ff`.
- Launched Phase 3 (deployment and packaging) from `main` at `955b5ff`, on `feature/p3-deployment`.
  Created the parent #20 and the tasks P3.1 (#21) and P3.2 (#22), linked as sub-issues. The roadmap
  records P2 as `complete` and P3 as `active`. P3.1 starts in a later move.
- Started P3.1 (#21). Added `scripts/install.sh`: an idempotent install and upgrade with
  `--dry-run` (default) and `--apply`. It creates the virtual environment, installs the pinned
  requirements, installs the unit only when it changed, and enables the service only when it is
  not enabled, so an upgrade never restarts a running service. Five tests run the script with fake
  `python3` and `systemctl` commands and cover the dry-run plan, the apply, and the idempotent
  re-run. Linked from the deployment guide. The dashboard is green.
