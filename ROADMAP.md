# JupyterHub Container Deploy Roadmap

This roadmap is the plan of record and the issue tracker map for the JupyterHub container
deployment service. Keep it in step with the GitHub issues, `CHANGE_LOG.md`, and `notes/`.
`scripts/check_workflow.py` parses the phase headers, status lines, and checkboxes below, so
keep their format.

## Issue Tracker Map

| Phase | Parent issue | Branch | Status |
| --- | --- | --- | --- |
| P0 Bootstrap and hardening | #1 | `feature/p0-bootstrap-scaffold` | complete |
| P1 Capacity and operations | #12 | `feature/p1-capacity-operations` | active |
| P2 API and access control | TBD | `feature/p2-api-access` | planned |
| P3 Deployment and packaging | TBD | `feature/p3-deployment` | planned |
| P4 Verify and release | TBD | `feature/p4-release` | planned |
| P5 Operate and maintain | TBD | `feature/p5-operate` | planned |

## Lifecycle Map

| Stage | Phases |
| --- | --- |
| Scope and design | P0 |
| Build | P0, P1, P2, P3 |
| Verify | P4 |
| Release and deploy | P3, P4 |
| Operate and maintain | P5 |
| Retire | P5 (procedure) |

## Conventions

- A phase is `P<n>`. A task is `P<n>.<m>`. A subtask is a checklist item inside the task's issue body. Three levels at most.
- Status values are `planned`, `active`, `pr-open`, `complete`, and `deferred`.
- A phase becomes `complete` only after its pull request merges to `main` and its parent issue closes.
- A child issue closes after its work, checklist, and verification are complete, with a closeout comment.
- A phase ends with a close-out report in `notes/reports/` and the maintainer's approval.

## Phase 0: Bootstrap and hardening

Parent issue: #1
Branch: `feature/p0-bootstrap-scaffold`
Status: complete

Goal: adopt the UBC-FRESH dev workflow in this repository and bring the existing JupyterHub container deployment service up to its quality bar: typed, tested, documented, and able to manage fifty containers.

- [x] P0.1 Repository governance and public surfaces (#2)
  - [x] Add `LICENSE`, `CONTRIBUTING.md`, and `CODE_OF_CONDUCT.md`.
  - [x] Add `CITATION.cff` with the UBC FRESH Lab authorship.
  - [x] Rewrite `README.md`: purpose, quick start, repository map, and status.
- [x] P0.2 Agent contract and planning surfaces (#3)
  - [x] Add `AGENTS.md` from the UBC-FRESH seed, with this project's rules.
  - [x] Add `ROADMAP.md` with the phases and the issue tracker map.
  - [x] Add `CHANGE_LOG.md` and `notes/` with the ADR index and the first ADRs.
- [x] P0.3 Workflow validator and green dashboard (#4)
  - [x] Add `scripts/check_workflow.py` and `scripts/dashboard.py`.
  - [x] Make `python scripts/check_workflow.py` report 0 errors.
  - [x] Make `python scripts/dashboard.py` green.
- [x] P0.4 Quality gates, pre-commit, and CI (#5)
  - [x] Configure ruff, mypy strict, and the coverage gate in `pyproject.toml`.
  - [x] Add `requirements-dev.txt` and `.pre-commit-config.yaml`.
  - [x] Add the CI and docs workflows and the issue templates.
- [x] P0.5 Sphinx documentation site (#6)
  - [x] Add `docs/conf.py`, `docs/index.rst`, and `docs/llms.txt`.
  - [x] Write the install, usage, configuration, and deployment guides.
  - [x] Write the architecture reference and the session protocol page.
- [x] P0.6 Typed service layer and configuration (50 slots) (#7)
  - [x] Add env-driven `Settings` with `MAX_DEPLOY` defaulting to 50.
  - [x] Add the pure naming helpers and the `LxdBackend` protocol.
  - [x] Add `HubManager` with the slot, start, stop, archive, and deploy rules.
  - [x] Record the capacity and layering decisions as ADRs.
- [x] P0.7 Hardened HTTP API and error handling (#8)
  - [x] Add the blueprint factory and the manager injection.
  - [x] Validate request bodies and reject bad input with 400.
  - [x] Map service errors to 404 and 409, and stop leaking the full config.
  - [x] Fix the named start route that the front end already calls.
- [x] P0.8 Application test suite and coverage (#9)
  - [x] Unit tests for the settings and the naming helpers.
  - [x] Tests for `HubManager` over an in-memory backend.
  - [x] Tests for `PylxdBackend` over a fake `pylxd` module.
  - [x] API tests through the Flask test client.
- [x] P0.9 Phase close-out and review handoff (#10)
  - [x] Open the phase pull request with `Part of #1`.
  - [x] Write `notes/reports/p0-closeout.md` with the gate and CI evidence.
  - [x] Post the progress and closeout comments on the child issues.

Acceptance criteria:

- Every gate in `python scripts/dashboard.py` is green.
- The service manages up to fifty containers, on host ports 8101 to 8150.
- CI is green on the phase pull request.

Phase 0 verification:

- `python scripts/dashboard.py`
- `pre-commit run --all-files`
- `python scripts/check_workflow.py`

## Phase 1: Capacity and operations

Parent issue: #12
Branch: `feature/p1-capacity-operations`
Status: active

Goal: make the fifty-container deployment easy to operate: health checks, a capacity report, and an operational runbook.

- [x] P1.1 Health endpoint and capacity report (#13)
  - [x] Add `HubManager.capacity()`.
  - [x] Add `GET /health` and `GET /capacity`.
  - [x] Add tests for the helper and both routes.
- [ ] P1.2 Operations runbook (#14)
  - [ ] Write `docs/guides/operations.rst`.
  - [ ] Link it from `docs/index.rst` and `docs/llms.txt`.

Acceptance criteria:

- A health endpoint reports the LXD backend and the free slots.
- The runbook covers start, stop, archive, restore, and a full-capacity incident.

## Phase 2: API and access control

Parent issue: TBD
Branch: `feature/p2-api-access`
Status: planned

Goal: secure the service: authentication for the dashboard and the API, and per-user scoping where it is needed.

- [ ] P2.1 Add authentication in front of the dashboard and the API
- [ ] P2.2 Document the access model and its threat boundaries

Acceptance criteria:

- <State the criterion that shows this phase met its goal.>

## Phase 3: Deployment and packaging

Parent issue: TBD
Branch: `feature/p3-deployment`
Status: planned

Goal: make the service reproducible on a fresh host: a pinned environment, the systemd unit, the nginx config, and an install script.

- [ ] P3.1 Add an idempotent install and upgrade script
- [ ] P3.2 Finish the nginx reverse proxy config and document it

Acceptance criteria:

- <State the criterion that shows this phase met its goal.>

## Phase 4: Verify and release

Parent issue: TBD
Branch: `feature/p4-release`
Status: planned

Goal: verify the acceptance criteria end to end and cut the first tagged release.

- [ ] P4.1 Run the acceptance checks on a clean host and record the evidence
- [ ] P4.2 Write the release notes and tag `v0.1.0` (approval required)

Acceptance criteria:

- <State the criterion that shows this phase met its goal.>

## Phase 5: Operate and maintain

Parent issue: TBD
Branch: `feature/p5-operate`
Status: planned

Goal: keep the service current: triage incoming ideas, review on a cadence, and retire cleanly.

- [ ] P5.1 Set a review cadence and record the first review

Acceptance criteria:

- <State the criterion that shows this phase met its goal.>

## Detailed Next Steps Notes

1. Phase 0 is complete. Pull request #11 squash-merged into `main` as `7f26293`; the squash tree
   equals the approved head `aa95946`. #1 is closed. Its tasks were P0.1 to P0.9 on #2 to #10.
   GitHub Pages is enabled, and `main` requires the three CI checks.
2. Phase 1 is active. Its parent is #12, and its tasks are P1.1 and P1.2 on #13 and #14, linked as
   sub-issues. The branch is `feature/p1-capacity-operations`, branched from `7f26293`.
3. The service manages up to 50 containers, on host ports 8101 to 8150, configurable through
   `JHD_MAX_DEPLOY` and `JHD_HOST_PORT_BASE`.
4. The coverage gate is 95 percent branch coverage across `scripts/` and `web_service/`.
