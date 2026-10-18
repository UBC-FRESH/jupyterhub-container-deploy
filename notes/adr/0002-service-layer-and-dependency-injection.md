# ADR 0002: A service layer behind an LxdBackend protocol

Status: accepted
Date: 2026-10-18
Issues: #7

## Context

The original `web_service/routes.py` called `pylxd` directly from each route. A module-level
`client = pylxd.Client()` ran at import time, so importing the app needed a live LXD daemon. The
business rules (which slot is free, which transitions are allowed, how inputs are validated) were
mixed into the HTTP handlers, and none of it could be tested without a daemon.

## Decision

Split the code into three layers in `web_service/`:

- `config.py`: an immutable `Settings` dataclass, read from the environment.
- `lxd_utils.py`: pure naming helpers, the `Hub` record, an `LxdBackend` protocol, a
  `PylxdBackend` implementation, and a `HubManager` that holds the rules.
- `routes.py`: a blueprint factory that reads the manager and settings from the Flask app.

The manager depends only on the `LxdBackend` protocol. `PylxdBackend` connects lazily, so importing
the package never contacts LXD. The application factory injects the manager, so tests pass an
in-memory backend and production passes the LXD backend.

## Consequences

- The business rules are tested in memory, with no daemon and no container churn.
- The pylxd adapter is thin and is tested against a fake `pylxd` module.
- A future backend (a test double, a remote LXD, a different container runtime) plugs in behind the
  same protocol.
- There is a little more code than one flat module, which the testability and the safety justify.

## Alternatives considered

- **Keep the routes calling pylxd directly.** Rejected: it cannot be tested without a daemon, and
  it mixes transport with rules.
- **Mock `pylxd.Client` in every test.** Rejected: the tests would encode the pylxd object shape in
  many places, and the rules would still be untested in isolation.
