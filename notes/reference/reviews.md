# Reviews

The service is reviewed on a **quarterly** cadence. The maintainer sets the date; the agent
prepares the evidence. Each finding gets one disposition: fixed, filed as an issue, or accepted.

## 2026-10-18: first review

Scope: the `v0.1.0` known gaps, the deferred roadmap items, and the state of the live host.

### Findings

| Finding | Disposition |
| --- | --- |
| Authentication is disabled on the live host; `jupyterhub-deploy.service` sets no `JHD_AUTH_TOKEN` | filed as #30 |
| The production nginx serves the app under a path prefix, but the app builds absolute URLs at the root, so a login redirect would 404 under that prefix | filed as #31 |
| The production unit sets `FLASK_ENV=development`, so the live service runs in debug mode | filed as #32 |
| The unit name differs between the repository (`jupyterhub-container-deploy.service`) and the host (`jupyterhub-deploy.service`); a stale unit was stuck in a restart loop | filed as #33 |
| The acceptance rehearsal ran on the lab host, not a blank machine | filed as #34 |
| One shared token, with no per-user identity or audit trail | accepted: the service has a single operator; revisit if it becomes multi-user |
| No container image or PyPI package | accepted: out of scope for `v0.1.0` |
| The nginx config has no TLS block | accepted: the operator owns TLS termination |
| Model choices for agent-assisted work | accepted: none recorded yet; revisit at the next review |

### Notes

- The live host was restarted onto the released code during the `v0.1.0` close-out. The dashboard
  answers at `http://fresh01.01101.dev/jupyterhub-container-deploy/` and reports 50 slots.
- The next review is due in the first quarter of 2027.
