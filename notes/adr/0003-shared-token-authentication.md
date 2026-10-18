# ADR 0003: Shared-token authentication for the dashboard and the API

Status: accepted
Date: 2026-10-18
Issues: #17

## Context

The service had no authentication. Any client that could reach the reverse proxy could create,
stop, and archive containers, and could read the hub list. The lab host is not on the public
internet, but the service still needs a boundary, and the boundary should protect a new route by
default rather than route by route.

## Decision

Require a shared token, read from `JHD_AUTH_TOKEN`, on every request except a health probe:

- API clients present it as `Authorization: Bearer <token>`.
- The dashboard presents it once at `GET /login`, which sets an `HttpOnly`, `SameSite=Lax`
  cookie, and `GET /logout` clears it.
- `GET /health` stays open, so an external monitor can check liveness without the token.
- The comparison uses `secrets.compare_digest`, so it does not leak the token length or content
  through timing.
- When `JHD_AUTH_TOKEN` is empty, authentication is disabled. This keeps local development and
  the test suite simple; the setting is documented as required in production.

The check runs in a Flask `before_request` hook, so every route is protected unless it is named in
the small open list.

## Consequences

- A new route is authenticated by default. Forgetting to add a check cannot expose it.
- The token is a single shared secret, not per-user identity. There is no audit trail of who did
  what, which is acceptable for the current single-operator use and is recorded as a limit.
- The cookie carries the token; the service must sit behind TLS, which the reverse proxy owns.
- Rotating the token is a settings change and a service restart.

## Alternatives considered

- **HTTP basic auth.** Rejected: it is weaker for a JSON API and still shares one credential.
- **Per-user accounts.** Deferred: it is more work than the current need justifies, and it is a
  larger change than Phase 2.
- **No authentication, network isolation only.** Rejected: a reverse-proxy misconfiguration would
  expose container control.
