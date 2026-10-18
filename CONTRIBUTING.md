# Contributing

This is a public repository from the UBC FRESH Lab. Contributions should keep it public-safe,
reproducible, and aligned with the active roadmap phase.

## Development setup

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pip install -r requirements.txt
pre-commit install
```

The pre-commit hooks call `python` from `PATH`, so commit from a shell where the environment is
active. A commit from a shell without it runs the hooks in the system Python, which lacks the dev
tools, and the hooks fail.

## The green dashboard

The dashboard is the signal that every commit must keep green:

```bash
python scripts/dashboard.py
```

It runs lint, format, strict types, the test suite with its coverage gate, the workflow validator,
and the docs build with warnings as errors. Any change from green is investigated and fixed before
you continue. There are no exceptions.

## Workflow

- Read `AGENTS.md` and `ROADMAP.md` before non-trivial work.
- Work on the branch for the active phase, named `feature/p<n>-<slug>`.
- Start every commit message with the task ID, for example `P0.6 add the typed service layer`.
- Write every function with full type annotations and a numpy-style docstring, and add unit tests
  for it in the same change set.
- Keep `ROADMAP.md`, `CHANGE_LOG.md`, `notes/`, and the matching GitHub issues in step with the work.
- Change the docs in the same change set as the behavior they describe.
- Open pull requests against `main` with `Part of #<parent issue>` in the body. CI must be green.

## Control characters and public safety

- Write issue and pull request bodies to files, and post them with `--body-file`. Do not build them
  from escaped strings. Sequences such as `\f` and `\t` become control characters, which can
  silently corrupt a branch name or a command.
- Use LF line endings. Carriage returns are rejected.
- Run `python scripts/check_workflow.py` before you push. To check one body file, run
  `python scripts/check_workflow.py --files path/to/body.md`.
- Do not commit private data, raw transcripts, credentials, generated local outputs, or
  machine-specific paths.
