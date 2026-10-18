# Phase close-out report: P3 Deployment and packaging

Phase: P3 Deployment and packaging
Parent issue: #20
Pull request: #23, `feature/p3-deployment` into `main`
Evidence head: `cb019e7`, the head that the gates and the CI runs below cover
Report commit: the commit that adds this report. Its CI run is posted on the pull request.
Date: 2026-10-18
Status: queued for approval. Not merged.

## Recommendation

Approve these actions. The agent carries them out in this order, and reads back each result.

1. Squash-merge pull request #23, and delete the branch `feature/p3-deployment`.
2. Close parent issue #20 with a closeout comment that cites the merge commit.
3. Launch Phase 4 (verify and release): create `feature/p4-release`, set the phase statuses in
   `ROADMAP.md`, create its child issues as sub-issues of a new parent, and start its first task.

Settings changes, each with its exact command. Each one runs only after its own approval.

- None in this repository. Phase 4 may propose a tag and a GitHub release; each is named with its
  command at that close-out and waits for its own approval.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| A fresh host can be provisioned with one documented command, and a re-run changes nothing | `scripts/install.sh`; `tests/test_install_script.py`; deployment guide | met |
| The nginx config proxies the service under a prefix and passes the headers that `ProxyFix` reads | `nginx/nginx.conf` serves at the site root on a dedicated hostname and forwards the host, client, and scheme headers; deployment guide | met with a stated limit |

Limit: the report's acceptance wording said "under a prefix". Serving at the site root is the
correct choice, because the application does not rewrite its URLs for a path prefix, so a prefix
would break the login redirect and the dashboard's relative URLs. The config and the guide record
the reason.

## 2. Workflow compliance

- Parent issue before the branch: #20 was created and its tasks #21 and #22 linked, then the branch
  was cut from `main`.
- Branch from `main`: branched from `955b5ff`.
- Commit messages that start with task IDs: 3 of 3 (`P3 activate`, `P3.1`, `P3.2`).
- Gates for each commit: the phase head `cb019e7` passes the full dashboard; the P3.1 commit
  `068f766` also passed the full dashboard and pre-commit.
- Roadmap and changelog in step: `ROADMAP.md` and `CHANGE_LOG.md` were updated with each task.
- Child issues closed with closeout evidence: #21 and #22 are closed with closeout comments.
- Approval gates: no tag, release, settings change, or external account was created.

## 3. Gate evidence

The phase head `cb019e7` was checked with the full dashboard:

- `python scripts/dashboard.py` — all six gates GREEN.
- `python -m pytest -q` — 235 passed, 99.50 percent branch coverage across `scripts/` and
  `web_service/` (gate 95).
- `python scripts/check_workflow.py` — 0 errors, 0 warnings.
- `pre-commit run --all-files` — all five hooks pass.

## 4. CI evidence

| Run ID | Head commit | Conclusion | Notes |
| --- | --- | --- | --- |
| 39165052183 | `cb019e7` | success | Three jobs, all success: Quality gates, Green dashboard summary, Pre-commit parity. |

## 5. Deviations

| Deviation | Cause | Remedy |
| --- | --- | --- |
| Acceptance wording "under a prefix" | A path prefix breaks the login redirect and relative URLs, because the app does not rewrite URLs | Serve at the site root on a dedicated hostname; recorded in the config and the guide |

## 6. Next phase

Phase 4, verify and release. Goal: verify the acceptance criteria end to end and cut the first
tagged release. Tasks:

- P4.1 Run the acceptance checks on a clean host and record the evidence.
- P4.2 Write the release notes and tag `v0.1.0` (approval required).

Acceptance criteria:

- The acceptance checks pass on a clean checkout, and the evidence is in the changelog.
- The tag is created on `main` only after approval, and the release notes list the changes and the
  known gaps.

Recommended default: P4.1 is a local rehearsal against a clean checkout; P4.2 is queued with the
exact `git tag` and `gh release create` commands and waits for its own approval.

## 7. Decision

- [ ] Approve as written.
- [ ] Approve with the changes stated here: <changes>.
