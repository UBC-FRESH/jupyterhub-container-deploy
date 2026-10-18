# Clean-checkout acceptance rehearsal

Date: 2026-10-18
Commit under test: `a5b7b76` (`main`, the Phase 3 squash merge)
Method: a fresh clone of `main` from GitHub, with the checks run inside the clone.

## What was run

```bash
git clone --branch main --depth 1 \
  https://github.com/UBC-FRESH/jupyterhub-container-deploy.git acc-clone
cd acc-clone
python scripts/dashboard.py
python scripts/check_workflow.py
python -m pytest -q
bash scripts/install.sh --dry-run
```

The clone had no virtual environment and no untracked files, so the checks ran against exactly
what a reviewer would receive.

## Results

| Check | Result |
| --- | --- |
| `python scripts/dashboard.py` | all six gates GREEN: lint, format, types, tests, validator, docs |
| `python scripts/check_workflow.py` | 0 errors, 0 warnings |
| `python -m pytest -q` | 235 passed, 99.50 percent branch coverage (gate 95) |
| `bash scripts/install.sh --dry-run` | printed the plan and ran no state-changing command |

The install dry run printed the plan and changed nothing. It reported that the virtual
environment is already present, the unit is already up to date, and the service is already
enabled. Those three lines reflect the lab host's existing deployment under
`/opt/jupyterhub-container-deploy`, which the dry run reads but does not change; they are not a
property of the clone.

## Stated limits

- The rehearsal ran on the lab host, not on a fresh physical machine. It proves the repository is
  self-contained, not that a blank host is provisioned.
- The checks used the development interpreter on the lab host, which has the pinned dev tools. A
  clone on a machine without those tools would need `pip install -r requirements-dev.txt` first,
  which `CONTRIBUTING.md` documents.
- No state-changing LXD command was run.
