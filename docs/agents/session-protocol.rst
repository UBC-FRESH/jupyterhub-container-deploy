Session protocol
================

Read this page at the start of every session, then follow it in order. It keeps a session
bounded and makes the handoff to the next session possible without the conversation.

Steps
-----

1. Read ``AGENTS.md``, then ``ROADMAP.md``, then the latest entries in ``CHANGE_LOG.md``.
2. Read the notes that your task names, and the docs pages that govern it.
3. Confirm the active phase and task. If your work is not in the roadmap, record it and stop.
4. Work one bounded move at a time. Stop and report after each one.
5. Run ``python scripts/dashboard.py`` before each commit. It must be green.
6. Update the roadmap, the changelog, and the notes in the same change set as the behavior.
7. Cite the pages you relied on, and say what you did not verify.

Rules
-----

- Do not start work outside the active phase. Record adjacent ideas instead.
- Do not weaken a gate to make it pass. A gate changes only with a changelog entry that says why.
- Do not run a state-changing LXD command to test a change. Use the in-memory backend.
- Do not restart the ``jupyterhub-container-deploy`` service unless the task is about the service.
- Write issue and pull request bodies to files, and post them with ``--body-file``.

See also
--------

- ``AGENTS.md``: the operating contract and the approval gates.
- ``ROADMAP.md``: the phases and the issue tracker map.
