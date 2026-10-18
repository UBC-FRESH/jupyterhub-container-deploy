# AGENTS.md

This file is the working contract for coding agents in the JupyterHub container deployment
service. It is built with the UBC-FRESH dev workflow, so changes here follow the same rules
that the workflow gives every project.

The service is a Flask application that manages JupyterHub LXD containers on the FRESH lab
host: it creates, starts, stops, archives, and restores hubs, and publishes each one on a
host port. It manages up to fifty containers at a time.

Keep this file short. Each rule below either checks itself or points to the page that
explains it.

## Session start

Before you change anything, read in this order:

1. This file.
2. `ROADMAP.md`: the active phase and its "Detailed Next Steps Notes".
3. The latest entries in `CHANGE_LOG.md`.
4. The notes your task names, in `notes/`.
5. The docs pages that govern your task, in `docs/`. Start with
   `docs/agents/session-protocol.rst`.

Cite the pages you relied on in your report.

## Repository state

- `README.md`: public overview and quick start.
- `ROADMAP.md`: phases, tasks, and the issue tracker map.
- `CHANGE_LOG.md`: append-only narrative, newest entries last.
- `docs/`: the Sphinx site, the RTFM surface. Published to GitHub Pages from `main`.
- `notes/`: ADRs, reference notes, and focused plans.
- `scripts/`: the workflow validator and the green dashboard.
- `tests/`: the pytest suite for the framework scripts and the application.
- `web_service/`: the Flask application: settings, the LXD service layer, and the routes.
- `run.py`: the development and WSGI entry point.
- `.github/`: CI, the docs deploy workflow, and the issue templates.

Do not claim a capability, a CI job, or a release that the roadmap has not recorded as complete.

## Working principles

- **Evidence over trust.** Treat a prose report as untrusted until you have checked the state it
  describes. Cite command output, diffs, commit hashes, and URLs.
- **One bounded move at a time.** Stop and report after each one.
- **No oracle, no capability.** A new agent-facing capability needs a validator that can fail.
- **Workflow as scaffold.** Create the parent issue, branch, and roadmap entry before the work.
- **Structured handoff.** Issues, roadmap entries, notes, and the changelog carry the state.
- **Preserve uncertainty.** Say what you did not verify, and why.
- **Scope discipline.** Stay inside the active phase and task. Record adjacent ideas; do not start them.
- **Sanitized output.** Keep raw transcripts, credentials, private data, and personal paths out of
  tracked files.

## The green dashboard rule

The dashboard in `scripts/dashboard.py` is the single signal that the repository is healthy. It
runs every quality gate: lint, format, strict types, tests with the coverage gate, the workflow
validator, and the docs build with warnings as errors.

- Every commit leaves the dashboard green. Run `python scripts/dashboard.py`, or let the pre-commit
  hooks run, before each commit.
- Any change from green is investigated and fixed immediately. There are no exceptions.
- Do not weaken a gate to make it pass. A gate changes only with a changelog entry that explains why.
- Record the dashboard result in the changelog entry for each task that you close.

## Typing and docstrings

- Every function, method, and test has complete type annotations. `mypy --strict` must pass on
  `scripts/`, `tests/`, `docs/conf.py`, `web_service/`, and `run.py`.
- Every public function in `scripts/` has a numpy-style docstring that matches its annotations.
- Do not use `Any`, `# type: ignore`, or `cast` without a comment that says why. A suppression
  names its error code.

## Testing policy

- Every function you write or change gets unit tests in the same change set. Tests must be able to
  fail, and each one asserts a specific behavior.
- Keep the layers: unit tests for each function, contract tests for public interfaces, integration
  tests that run the command-line tools, property tests for invariants, and the API tests.
- The container operations sit behind the `LxdBackend` protocol, so the business rules are tested
  against an in-memory backend. Never require a live LXD daemon in a test.
- The coverage gate is 95 percent branch coverage of `scripts/` and `web_service/`.

## CI and merges

- CI runs every gate on every pull request, and on every push to `main`.
- No pull request merges while CI is red. Branch protection makes the CI jobs required.
- A merge happens only as part of an approved phase close-out. Queue the pull request, write the
  report in `notes/reports/`, and wait for the maintainer's approval.

## Planning workflow

- One phase is one GitHub parent issue and one feature branch, `feature/p<n>-<slug>`.
- One task is one child issue, linked to the parent as a sub-issue.
- A subtask is a checklist item in the child issue body. Three levels at most.
- Keep `ROADMAP.md`, `CHANGE_LOG.md`, `notes/`, issue bodies, and PR descriptions in step.

## Approval gates

You may, within the active phase: create and commit to its branch, push that branch, open and update
its issues and pull requests, run local checks, and write notes and reports.

After the maintainer approves a phase close-out, carry out what the report recommends: squash-merge
the pull request, delete its branch, close the parent issue, and launch the next phase. Name every
settings change, tag, release, or external account in the report, with its exact command, and wait
for approval of each one.

You must wait for an explicit approval before you: create a tag or a release; change repository
visibility, settings, or branch protection; create an external account, repository, or server;
touch private data or credentials; or delete anything beyond the branch that an approved report names.

## GitHub hygiene

- Audit read-only first: `gh issue list`, `gh issue view <n>`, `gh pr list`.
- Write bodies and comments to files, and post them with `--body-file`. Never build them from
  escaped strings.
- Read back every comment or edit with `gh issue view` before you report it as posted.
- Post a progress comment when a task or phase milestone completes, and a closeout comment before
  you close an issue.

## Formatting

- Put section labels on their own lines, such as `Phase identifier: P0`.
- Use real task-list syntax, one item per line.
- Wrap branch names, paths, commands, and commit hashes in backticks.
- Start commit messages with the task ID, for example `P0.6 add the typed service layer`.

## Verification

Run the dashboard before you report a change as done:

```bash
python scripts/dashboard.py
```

Record the result in the changelog entry for the milestone.

## Public safety

- No private data, credentials, raw transcripts, unpublished documents, or machine-specific paths in
  tracked files.
- Use placeholders, repository-relative paths, or environment variables in examples.

## Project-specific rules

- **Never run a state-changing LXD command to test a change.** The lab host runs live student
  containers. Test the rules against the in-memory backend, and test the pylxd adapter against a
  fake `pylxd` module.
- **Keep the naming scheme stable.** A container is `jupyterhub<NN>`, its host port is
  `host_port_base + NN`, and its archive is `jh-archive-<tag>`. Existing deployments depend on it.
- **Validate every input at the boundary.** Container names, tags, and descriptions come from the
  network. Reject bad input with a 400 before it reaches LXD.
- **The dashboard runs as a service.** Do not restart `jupyterhub-container-deploy` from a task
  unless the task is about the service itself, and never while a request could be in flight.
