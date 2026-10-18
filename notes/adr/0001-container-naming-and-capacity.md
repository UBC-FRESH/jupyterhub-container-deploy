# ADR 0001: Container naming and fifty-slot capacity

Status: accepted
Date: 2026-10-18
Issues: #7

## Context

The service names a container `jupyterhub<NN>` and publishes it on host port `81<NN>`, where
`<NN>` is a two-digit slot. The old code hard-coded a limit of 30 slots in `web_service/config.py`,
parsed the slot with `int(name[-2:])`, and built the port with `f"81{number}"`. The lab now needs
fifty concurrent dev containers. The parsing also breaks on any container whose name does not end
in exactly two digits.

## Decision

Keep the existing name and port scheme, and widen it to two or three digits of slot:

- A container is `<prefix><NN>`, with the slot zero-padded to two digits (`jupyterhub01` to
  `jupyterhub50`).
- Its host port is `host_port_base + slot` (`8101` to `8150` for the default base of `8100`).
- An archive is `<archive_prefix>-<tag>` (`jh-archive-<tag>`).
- The slot count, the port base, the container port, the template name, and the two prefixes are
  all settings, read from the environment with `JHD_` prefixed names.

The slot is recovered with a full-match regular expression, not by slicing the name. The manager
allocates the lowest free slot in `1..max_deploy`.

## Consequences

- Existing deployments keep their names and ports, so no migration is needed.
- Raising the limit to 50 only changes `MAX_DEPLOY`, which now defaults to 50.
- The scheme stays within two digits to 99; the settings reject a base port plus slot count that
  would exceed port 65535.
- A test can drive the whole scheme in memory, so capacity rules need no live LXD.

## Alternatives considered

- **A four-digit host port with a wider slot.** Rejected: it breaks the existing proxy devices and
  the URLs that students already hold.
- **Deriving the slot by slicing the name.** Rejected: it silently misreads a name such as
  `jupyterhub7` or a non-hub container.
