# Phase close-out report: P0 Bootstrap and hardening

Phase: P0 Bootstrap and hardening
Parent issue: #1
Pull request: #11, `feature/p0-bootstrap-scaffold` into `main`
Evidence head: `bf5b14a`, the head that the gates and the CI runs below cover
Report commit: the commit that adds this report. Its CI run is posted on the pull request.
Date: 2026-10-18
Status: queued for approval. Not merged.

## Recommendation

Approve these actions. The agent carries them out in this order, and reads back each result.

1. Squash-merge pull request #11, and delete the branch `feature/p0-bootstrap-scaffold`.
2. Close parent issue #1 with a closeout comment that cites the merge commit.
3. Launch Phase 1 (capacity and operations): create `feature/p1-capacity-operations`, set the
   phase statuses in `ROADMAP.md`, create its child issues as sub-issues of a new parent, and
   start its first task.

Settings changes, each with its exact command. Each one runs only after its own approval.

- Enable GitHub Pages from the Actions source, so that the Docs workflow can deploy:
  `gh api -X POST repos/UBC-FRESH/jupyterhub-container-deploy/pages -f build_type=workflow`
- Protect `main` and require the three CI jobs (`Quality gates`, `Green dashboard summary`,
  `Pre-commit parity`). This is a maintainer settings change; the exact `gh api` call is
  prepared at execution time.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| Every gate in `python scripts/dashboard.py` is green | `python scripts/dashboard.py` on `bf5b14a`: lint, format, types, tests, validator, docs all GREEN | met |
| The service manages up to fifty containers, on ports 8101 to 8150 | `web_service/config.py` default `max_deploy=50`, `host_port_base=8100`; `tests/test_config.py`, `tests/test_lxd_utils.py` | met |
| CI is green on the phase pull request | CI run 39162260138 on `bf5b14a`, three jobs, all success; see section 4 | met |

## 2. Workflow compliance

- Parent issue before the branch: #1 was created, then its sub-issues #2 to #10, then the branch
  `feature/p0-bootstrap-scaffold`.
- Branch from `main`: branched from `051d282`.
- Commit messages that start with task IDs: 8 of 8 work commits (P0.1 to P0.8).
- Gates for each commit: the phase head `bf5b14a` passes the full dashboard. See section 3 for the
  stated limit on the intermediate commits.
- Roadmap and changelog in step: `ROADMAP.md` and `CHANGE_LOG.md` landed in P0.2 and were kept in
  step; the changelog records every task of this phase.
- Child issues closed with closeout evidence: #2 to #9 close with closeout comments after this
  report is posted; #10 stays open until the pull request is queued.
- Approval gates: no tag, release, settings change, or external account was created. The Pages and
  branch-protection changes are named above and wait for approval.

## 3. Gate evidence

The phase head `bf5b14a` was checked with the full dashboard:

- `python scripts/dashboard.py` — all six gates GREEN.
- `python -m pytest -q` — 210 passed, 99.82 percent branch coverage across `scripts/` and
  `web_service/` (gate 95).
- `python scripts/check_workflow.py` — 0 errors, 0 warnings.
- `pre-commit run --all-files` — ruff check, ruff format, mypy strict, the validator, and pytest
  all pass.

Stated limit: the scaffold is one interdependent change set. The intermediate commits P0.1 to P0.8
were not each checked with the full dashboard, because the validator's required files span several
of them. The gates were verified on the phase head, which is what the pull request merges.

## 4. CI evidence

| Run ID | Head commit | Conclusion | Notes |
| --- | --- | --- | --- |
| 39162260138 | `bf5b14a` | success | Three jobs, all success: Quality gates, Green dashboard summary, Pre-commit parity. |

## 5. Deviations

| Deviation | Cause | Remedy |
| --- | --- | --- |
| Intermediate commits not independently gate-verified | The scaffold's required files span P0.1 to P0.8, so no single early commit has the full validator surface | Gates verified on the phase head `bf5b14a`; recorded here as a stated limit |
| `gunicorn.conf.py` excluded from ruff | Its name is not a valid Python module name, and gunicorn loads it by that path | Excluded in `pyproject.toml` with a comment; it is one line of config |
| `Any` at the pylxd boundary | `pylxd` ships no type information | Isolated to `PylxdBackend`; `ANN401` ignored for that module with a comment; `Hub` conversion happens at once |

## 6. Next phase

Phase 1, capacity and operations. Goal: make the fifty-container deployment easy to operate.
Tasks:

- P1.1 Add a health endpoint and a capacity report.
- P1.2 Write the operations runbook in `docs/guides/`.

Acceptance criteria:

- A health endpoint reports the LXD backend and the free slots.
- The runbook covers start, stop, archive, restore, and a full-capacity incident.

Recommended default: keep the phase small; defer authentication to Phase 2.

## 7. Decision

- [ ] Approve as written.
- [ ] Approve with the changes stated here: <changes>.
