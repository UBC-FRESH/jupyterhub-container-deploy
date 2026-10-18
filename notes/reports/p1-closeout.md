# Phase close-out report: P1 Capacity and operations

Phase: P1 Capacity and operations
Parent issue: #12
Pull request: #15, `feature/p1-capacity-operations` into `main`
Evidence head: `3caafb4`, the head that the gates and the CI runs below cover
Report commit: the commit that adds this report. Its CI run is posted on the pull request.
Date: 2026-10-18
Status: queued for approval. Not merged.

## Recommendation

Approve these actions. The agent carries them out in this order, and reads back each result.

1. Squash-merge pull request #15, and delete the branch `feature/p1-capacity-operations`.
2. Close parent issue #12 with a closeout comment that cites the merge commit.
3. Launch Phase 2 (API and access control): create `feature/p2-api-access`, set the phase
   statuses in `ROADMAP.md`, create its child issues as sub-issues of a new parent, and start its
   first task.

Settings changes, each with its exact command. Each one runs only after its own approval.

- None. Pages and branch protection were set at the Phase 0 close-out.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| A health endpoint reports the LXD backend and the free slots | `GET /health` in `web_service/routes.py`; `HubManager.health()`; `tests/test_routes.py`, `tests/test_lxd_utils.py` | met |
| The runbook covers start, stop, archive, restore, and a full-capacity incident | `docs/guides/operations.rst`; linked from the docs index and `llms.txt` | met |

## 2. Workflow compliance

- Parent issue before the branch: #12 was created and its tasks #13 and #14 linked, then the branch
  was cut from `main`.
- Branch from `main`: branched from `7f26293`.
- Commit messages that start with task IDs: 3 of 3 (`P1 activate`, `P1.1`, `P1.2`).
- Gates for each commit: the phase head `3caafb4` passes the full dashboard; the P1.1 commit
  `071a835` also passed the full dashboard and pre-commit.
- Roadmap and changelog in step: `ROADMAP.md` and `CHANGE_LOG.md` were updated with each task.
- Child issues closed with closeout evidence: #13 and #14 are closed with closeout comments.
- Approval gates: no tag, release, settings change, or external account was created.

## 3. Gate evidence

The phase head `3caafb4` was checked with the full dashboard:

- `python scripts/dashboard.py` — all six gates GREEN.
- `python -m pytest -q` — 219 passed, 99.74 percent branch coverage across `scripts/` and
  `web_service/` (gate 95).
- `python scripts/check_workflow.py` — 0 errors, 0 warnings.
- `pre-commit run --all-files` — all five hooks pass.

The P1.1 commit `071a835` was checked the same way before it was pushed.

## 4. CI evidence

| Run ID | Head commit | Conclusion | Notes |
| --- | --- | --- | --- |
| 39163695576 | `3caafb4` | success | Three jobs, all success: Quality gates, Green dashboard summary, Pre-commit parity. |

## 5. Deviations

| Deviation | Cause | Remedy |
| --- | --- | --- |
| None | - | - |

## 6. Next phase

Phase 2, API and access control. Goal: secure the service. Tasks:

- P2.1 Add authentication in front of the dashboard and the API.
- P2.2 Document the access model and its threat boundaries.

Acceptance criteria:

- Unauthenticated requests to the dashboard and the API are rejected.
- The access model page names what is protected and what is not.

Recommended default: a shared token or HTTP basic auth in front of the service, since the lab
host is not on the public internet; record the choice as an ADR before the code.

## 7. Decision

- [ ] Approve as written.
- [ ] Approve with the changes stated here: <changes>.
