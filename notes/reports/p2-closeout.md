# Phase close-out report: P2 API and access control

Phase: P2 API and access control
Parent issue: #16
Pull request: #19, `feature/p2-api-access` into `main`
Evidence head: `f7e7b9c`, the head that the gates and the CI runs below cover
Report commit: the commit that adds this report. Its CI run is posted on the pull request.
Date: 2026-10-18
Status: queued for approval. Not merged.

## Recommendation

Approve these actions. The agent carries them out in this order, and reads back each result.

1. Squash-merge pull request #19, and delete the branch `feature/p2-api-access`.
2. Close parent issue #16 with a closeout comment that cites the merge commit.
3. Launch Phase 3 (deployment and packaging): create `feature/p3-deployment`, set the phase
   statuses in `ROADMAP.md`, create its child issues as sub-issues of a new parent, and start its
   first task.

Settings changes, each with its exact command. Each one runs only after its own approval.

- None. The production host must set `JHD_AUTH_TOKEN` in the service environment and restart, but
  that is a host action outside this repository and is not run by the agent.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| Unauthenticated requests to the dashboard and the API are rejected with 401 | `web_service/auth.py`; `tests/test_auth.py` | met |
| The health probe stays reachable without a credential | `OPEN_PATHS` includes `/health`; `test_health_probe_is_open` | met |
| The access model page names what is protected and what is not | `docs/guides/access.rst`; linked from the docs index and `llms.txt` | met |

## 2. Workflow compliance

- Parent issue before the branch: #16 was created and its tasks #17 and #18 linked, then the branch
  was cut from `main`.
- Branch from `main`: branched from `c9407ca`.
- Commit messages that start with task IDs: 3 of 3 (`P2 activate`, `P2.1`, `P2.2`).
- Gates for each commit: the phase head `f7e7b9c` passes the full dashboard; the P2.1 commit
  `eb9b0e8` also passed the full dashboard and pre-commit.
- Roadmap and changelog in step: `ROADMAP.md` and `CHANGE_LOG.md` were updated with each task.
- Child issues closed with closeout evidence: #17 and #18 are closed with closeout comments.
- Approval gates: no tag, release, settings change, or external account was created.

## 3. Gate evidence

The phase head `f7e7b9c` was checked with the full dashboard:

- `python scripts/dashboard.py` — all six gates GREEN.
- `python -m pytest -q` — 230 passed, 99.50 percent branch coverage across `scripts/` and
  `web_service/` (gate 95).
- `python scripts/check_workflow.py` — 0 errors, 0 warnings.
- `pre-commit run --all-files` — all five hooks pass.

## 4. CI evidence

| Run ID | Head commit | Conclusion | Notes |
| --- | --- | --- | --- |
| 39164249244 | `f7e7b9c` | success | Three jobs, all success: Quality gates, Green dashboard summary, Pre-commit parity. |

## 5. Deviations

| Deviation | Cause | Remedy |
| --- | --- | --- |
| None | - | - |

## 6. Next phase

Phase 3, deployment and packaging. Goal: make the service reproducible on a fresh host. Tasks:

- P3.1 Add an idempotent install and upgrade script.
- P3.2 Finish the nginx reverse proxy config and document it.

Acceptance criteria:

- A fresh host can be provisioned with one documented command, and a re-run changes nothing.
- The nginx config proxies the service under a prefix and passes the headers that `ProxyFix`
  reads.

Recommended default: the install script copies the unit, creates the virtual environment, installs
the pinned requirements, and enables the service; a `--dry-run` mode prints the plan without
changing the host.

## 7. Decision

- [ ] Approve as written.
- [ ] Approve with the changes stated here: <changes>.
