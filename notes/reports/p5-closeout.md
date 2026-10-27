# Phase close-out report: P5 Operate and maintain

Phase: P5 Operate and maintain
Parent issue: #28
Pull request: #35, `feature/p5-operate` into `main`
Evidence head: `2c0fad7`, the head that the gates and the CI runs below cover
Report commit: the commit that adds this report. Its CI run is posted on the pull request.
Date: 2026-10-18
Status: queued for approval. Not merged.

## Recommendation

Approve these actions. The agent carries them out in this order, and reads back each result.

1. Squash-merge pull request #35, and delete the branch `feature/p5-operate`.
2. Close parent issue #28 with a closeout comment that cites the merge commit.

Settings changes, each with its exact command. Each one runs only after its own approval.

- None.

There is no next phase. P5 is the last planned phase, so on this merge the roadmap is complete and
the service enters maintenance. The recommended maintenance backlog is the filed findings #30 to
#34, reviewed on the quarterly cadence set in `notes/reference/reviews.md`. A future phase can be
opened when the maintainer decides.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| A review cadence is set, and the first review is recorded with its findings and dispositions | `notes/reference/reviews.md`: quarterly cadence, nine findings, each fixed, filed, or accepted | met |

## 2. Workflow compliance

- Parent issue before the branch: #28 was created and its task #29 linked, then the branch was cut
  from `main`.
- Branch from `main`: branched from `f879cc1`.
- Commit messages that start with task IDs: 2 of 2 (`P5 activate`, `P5.1`).
- Gates for each commit: the phase head `2c0fad7` passes the full dashboard and pre-commit.
- Roadmap and changelog in step: `ROADMAP.md` and `CHANGE_LOG.md` were updated with the task.
- Child issues closed with closeout evidence: #29 is closed with a closeout comment.
- Approval gates: no tag, release, settings change, or external account was created.

## 3. Gate evidence

The phase head `2c0fad7` was checked with the full dashboard:

- `python scripts/dashboard.py` — all six gates GREEN.
- `python -m pytest -q` — 235 passed, 99.50 percent branch coverage across `scripts/` and
  `web_service/` (gate 95).
- `python scripts/check_workflow.py` — 0 errors, 0 warnings.
- `pre-commit run --all-files` — all five hooks pass.

## 4. CI evidence

| Run ID | Head commit | Conclusion | Notes |
| --- | --- | --- | --- |
| 39167936823 | `2c0fad7` | success | Three jobs, all success: Quality gates, Green dashboard summary, Pre-commit parity. |

## 5. Deviations

| Deviation | Cause | Remedy |
| --- | --- | --- |
| None | - | - |

## 6. Next phase

None. The roadmap P0 to P5 is complete. The maintenance backlog is the filed findings:

- #30 Set `JHD_AUTH_TOKEN` in the production unit.
- #31 Support a URL prefix or document the nginx requirement.
- #32 Switch the production unit to production settings.
- #33 Reconcile the systemd unit name between the repo and the host.
- #34 Run the acceptance rehearsal on a blank host.

Recommended default: keep the quarterly review cadence, and open a new phase when enough backlog
items justify one.

## 7. Decision

- [ ] Approve as written.
- [ ] Approve with the changes stated here: <changes>.
