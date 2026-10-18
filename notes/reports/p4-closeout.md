# Phase close-out report: P4 Verify and release

Phase: P4 Verify and release
Parent issue: #24
Pull request: #27, `feature/p4-release` into `main`
Evidence head: `ccd9952`, the head that the gates and the CI runs below cover
Report commit: the commit that adds this report. Its CI run is posted on the pull request.
Date: 2026-10-18
Status: queued for approval. Not merged, not tagged, not released.

## Recommendation

Approve these actions. The agent carries them out in this order, and reads back each result.

1. Squash-merge pull request #27, and delete the branch `feature/p4-release`.
2. Create the annotated tag `v0.1.0` on the squash-merge commit, and push it.
3. Create the GitHub release `v0.1.0` from the release notes.
4. Close parent issue #24 with a closeout comment that cites the merge commit and the tag.
5. Launch Phase 5 (operate and maintain): create `feature/p5-operate`, set the phase statuses in
   `ROADMAP.md`, create its child issues as sub-issues of a new parent, and start its first task.

Settings and external actions, each with its exact command. Each one runs only after its own
approval. The tag is placed on `main` only, on the squash-merge commit of #27, whose hash is
recorded when the merge runs.

```bash
# 2. Tag (replace <merge-commit> with the squash-merge commit of PR #27)
git tag -a v0.1.0 <merge-commit> -m "v0.1.0"
git push origin v0.1.0

# 3. GitHub release
gh release create v0.1.0 --title "v0.1.0" --notes-file notes/releases/v0.1.0.md
```

No repository settings changes are requested.

## 1. Objectives and acceptance

| Criterion | Evidence | Status |
| --- | --- | --- |
| The acceptance checks pass on a clean checkout, and the evidence is recorded | `notes/reference/acceptance.md`: fresh clone of `a5b7b76`; dashboard green, validator 0/0, 235 tests at 99.50 percent, install dry run clean | met with a stated limit |
| The tag is created on `main` only after approval, and the release notes list the changes and the known gaps | `notes/releases/v0.1.0.md`; the tag command above waits for approval | met |

Limit: the rehearsal ran on the lab host, not on a blank physical machine. `notes/reference/acceptance.md`
records this. The repository is proven self-contained; a blank-host provisioning is not.

## 2. Workflow compliance

- Parent issue before the branch: #24 was created and its tasks #25 and #26 linked, then the branch
  was cut from `main`.
- Branch from `main`: branched from `a5b7b76`.
- Commit messages that start with task IDs: 3 of 3 (`P4 activate`, `P4.1`, `P4.2`).
- Gates for each commit: the phase head `ccd9952` passes the full dashboard; the P4.1 commit
  `49a5fb6` also passed the full dashboard and pre-commit.
- Roadmap and changelog in step: `ROADMAP.md` and `CHANGE_LOG.md` were updated with each task.
- Child issues closed with closeout evidence: #25 and #26 are closed with closeout comments.
- Approval gates: no tag, release, settings change, or external account was created.

## 3. Gate evidence

The phase head `ccd9952` was checked with the full dashboard:

- `python scripts/dashboard.py` — all six gates GREEN.
- `python -m pytest -q` — 235 passed, 99.50 percent branch coverage across `scripts/` and
  `web_service/` (gate 95).
- `python scripts/check_workflow.py` — 0 errors, 0 warnings.
- `pre-commit run --all-files` — all five hooks pass.

## 4. CI evidence

| Run ID | Head commit | Conclusion | Notes |
| --- | --- | --- | --- |
| 39166602834 | `ccd9952` | success | Three jobs, all success: Quality gates, Green dashboard summary, Pre-commit parity. |

## 5. Deviations

| Deviation | Cause | Remedy |
| --- | --- | --- |
| The acceptance rehearsal ran on the lab host, not a blank machine | No blank host was available | Recorded as a stated limit in `notes/reference/acceptance.md`; a blank-host run is a Phase 5 candidate |

## 6. Next phase

Phase 5, operate and maintain. Goal: keep the service current. Tasks:

- P5.1 Set a review cadence and record the first review.

Acceptance criteria:

- A review cadence is set, and the first review is recorded with its findings and dispositions.

Recommended default: a quarterly review, with the first review covering the known gaps from the
`v0.1.0` release notes and the deferred items in `ROADMAP.md`.

## 7. Decision

- [ ] Approve as written, including the tag and the release.
- [ ] Approve the merge only; hold the tag and the release.
- [ ] Approve with the changes stated here: <changes>.
