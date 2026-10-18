"""LXD container management for the JupyterHub deployment service.

The module has three layers:

- Pure helpers that turn a slot number into a container name, a host port, and back.
  They hold no state and are the unit-tested core of the naming scheme.
- :class:`LxdBackend`, a protocol that describes the container operations the service
  needs, and :class:`PylxdBackend`, its implementation on top of ``pylxd``.
- :class:`HubManager`, which holds the business rules: which slots are free, which
  transitions are allowed, and how inputs are validated.

Keeping the rules in :class:`HubManager` and the I/O behind a protocol means the service
is tested against an in-memory backend, with no LXD daemon and no container churn.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Protocol

TAG_RE: re.Pattern[str] = re.compile(r"^[a-z0-9][a-z0-9._-]{0,62}$")
CONTROL_RE: re.Pattern[str] = re.compile(r"[\x00-\x1f\x7f]")
MAX_DESCRIPTION_LENGTH: int = 200
NO_DESCRIPTION: str = "No description provided"
DESCRIPTION_KEY: str = "user.description"


class HubError(Exception):
    """Base class for every error that the service reports to a client.

    Attributes
    ----------
    http_status : int
        HTTP status code that the API returns for this error.
    """

    http_status: int = 500


class InvalidInputError(HubError):
    """A request carried a value that the service cannot accept."""

    http_status = 400


class NotFoundError(HubError):
    """A named container does not exist."""

    http_status = 404


class ConflictError(HubError):
    """A request conflicts with the current state of a container."""

    http_status = 409


class SlotUnavailableError(HubError):
    """Every deployment slot is in use."""

    http_status = 409


class BackendError(HubError):
    """The LXD backend failed in a way the service cannot classify."""

    http_status = 502


@dataclass(frozen=True)
class Hub:
    """One JupyterHub container, as the service sees it.

    Attributes
    ----------
    name : str
        Container name.
    status : str
        LXD status string, such as ``Running`` or ``Stopped``.
    description : str
        Human-readable description stored in the container config.
    """

    name: str
    status: str
    description: str = NO_DESCRIPTION

    @property
    def running(self) -> bool:
        """Report whether the container is running.

        Returns
        -------
        bool
            ``True`` when the status is ``running``, ignoring case.
        """
        return self.status.lower() == "running"

    @property
    def stopped(self) -> bool:
        """Report whether the container is stopped.

        Returns
        -------
        bool
            ``True`` when the status is ``stopped``, ignoring case.
        """
        return self.status.lower() == "stopped"


def hub_name(prefix: str, slot: int) -> str:
    """Build the container name for a deployment slot.

    Parameters
    ----------
    prefix : str
        Container name prefix, such as ``jupyterhub``.
    slot : int
        Slot number in ``1..99``.

    Returns
    -------
    str
        The name, with the slot zero-padded to two digits, such as ``jupyterhub07``.
    """
    return f"{prefix}{slot:02d}"


def host_port(base: int, slot: int) -> int:
    """Map a deployment slot to its published host port.

    Parameters
    ----------
    base : int
        First host port, such as ``8100``.
    slot : int
        Slot number in ``1..99``.

    Returns
    -------
    int
        ``base + slot``, so slot 1 is ``8101`` and slot 50 is ``8150``.
    """
    return base + slot


def archive_name(prefix: str, tag: str) -> str:
    """Build the container name for an archived hub.

    Parameters
    ----------
    prefix : str
        Archive name prefix, such as ``jh-archive``.
    tag : str
        Validated archive tag.

    Returns
    -------
    str
        The name, such as ``jh-archive-spring-2026``.
    """
    return f"{prefix}-{tag}"


def parse_slot(prefix: str, name: str) -> int | None:
    """Recover the deployment slot from a container name.

    Parameters
    ----------
    prefix : str
        Container name prefix.
    name : str
        Container name to parse.

    Returns
    -------
    int or None
        The slot number when the name is ``prefix`` plus two or three digits, and
        ``None`` otherwise.
    """
    match = re.fullmatch(re.escape(prefix) + r"(\d{2,3})", name)
    return int(match.group(1)) if match else None


def validate_tag(tag: str) -> str:
    """Validate and normalize an archive tag.

    Parameters
    ----------
    tag : str
        Candidate tag.

    Returns
    -------
    str
        The lowercased tag.

    Raises
    ------
    InvalidInputError
        When the tag is empty, too long, or holds a character outside ``[a-z0-9._-]``.
    """
    normalized = tag.strip().lower()
    if not TAG_RE.match(normalized):
        raise InvalidInputError(
            "tag must be 1 to 63 characters of lowercase letters, digits, dots, "
            "underscores, or hyphens, and start with a letter or digit"
        )
    return normalized


def validate_description(description: str) -> str:
    """Validate and normalize a hub description.

    Parameters
    ----------
    description : str
        Candidate description.

    Returns
    -------
    str
        The trimmed description.

    Raises
    ------
    InvalidInputError
        When the description is empty, too long, or holds a control character.
    """
    normalized = description.strip()
    if not normalized:
        raise InvalidInputError("description is required")
    if len(normalized) > MAX_DESCRIPTION_LENGTH:
        raise InvalidInputError(f"description must be at most {MAX_DESCRIPTION_LENGTH} characters")
    if CONTROL_RE.search(normalized):
        raise InvalidInputError("description must not contain control characters")
    return normalized


def allocate_slot(prefix: str, names: list[str], max_deploy: int) -> int:
    """Return the lowest free deployment slot.

    Parameters
    ----------
    prefix : str
        Container name prefix used to parse slots from ``names``.
    names : list of str
        Names of the containers that already exist.
    max_deploy : int
        Number of slots, from ``1`` to this value.

    Returns
    -------
    int
        The lowest slot in ``1..max_deploy`` that no name uses.

    Raises
    ------
    SlotUnavailableError
        When every slot is in use.
    """
    used = {slot for name in names if (slot := parse_slot(prefix, name)) is not None}
    for slot in range(1, max_deploy + 1):
        if slot not in used:
            return slot
    raise SlotUnavailableError(f"all {max_deploy} deployment slots are in use")


class LxdBackend(Protocol):
    """The container operations that :class:`HubManager` depends on."""

    def list_all(self) -> list[Hub]:
        """List every container that the service manages."""
        ...

    def get(self, name: str) -> Hub:
        """Return one container, or raise :class:`NotFoundError`."""
        ...

    def create(
        self,
        *,
        name: str,
        template: str,
        description: str,
        host_port: int,
        container_port: int,
    ) -> None:
        """Create and start a container from a template, with a proxy device."""
        ...

    def start(self, name: str) -> None:
        """Start a container."""
        ...

    def stop(self, name: str) -> None:
        """Stop a container."""
        ...

    def rename(self, name: str, new_name: str) -> None:
        """Rename a container."""
        ...

    def add_proxy(self, name: str, *, host_port: int, container_port: int) -> None:
        """Add a proxy device that publishes a container port on the host."""
        ...


class PylxdBackend:
    """A :class:`LxdBackend` implemented with the ``pylxd`` client.

    The client connects lazily on first use, so importing the application never needs a
    running LXD daemon. ``pylxd`` ships no type information, so its objects are handled
    as ``Any`` at this boundary and converted to :class:`Hub` at once.
    """

    def __init__(self, endpoint: str = "") -> None:
        """Store the endpoint and defer the connection.

        Parameters
        ----------
        endpoint : str, optional
            LXD socket endpoint. Empty selects the ``pylxd`` default.
        """
        self._endpoint = endpoint
        self._client: Any | None = None

    def _connection(self) -> Any:
        """Return the pylxd client, connecting on first use.

        Returns
        -------
        Any
            The ``pylxd.Client`` instance.
        """
        if self._client is None:
            import pylxd

            self._client = (
                pylxd.Client(endpoint=self._endpoint) if self._endpoint else pylxd.Client()
            )
        return self._client

    @staticmethod
    def _to_hub(container: Any) -> Hub:
        """Convert a pylxd container into a :class:`Hub`.

        Parameters
        ----------
        container : Any
            A ``pylxd`` container or instance object.

        Returns
        -------
        Hub
            The converted record.
        """
        description = container.config.get(DESCRIPTION_KEY, NO_DESCRIPTION)
        return Hub(name=container.name, status=container.status, description=description)

    def list_all(self) -> list[Hub]:
        """List every container on the LXD server.

        Returns
        -------
        list of Hub
            The containers, converted from ``pylxd`` objects.
        """
        return [self._to_hub(container) for container in self._connection().containers.all()]

    def get(self, name: str) -> Hub:
        """Return one container by name.

        Parameters
        ----------
        name : str
            Container name.

        Returns
        -------
        Hub
            The container record.

        Raises
        ------
        NotFoundError
            When no container has that name.
        """
        import pylxd

        try:
            container = self._connection().containers.get(name)
        except pylxd.exceptions.NotFound as exc:
            raise NotFoundError(f"container {name} not found") from exc
        return self._to_hub(container)

    def create(
        self,
        *,
        name: str,
        template: str,
        description: str,
        host_port: int,
        container_port: int,
    ) -> None:
        """Create a container from a template, start it, and add its proxy device.

        Parameters
        ----------
        name : str
            New container name.
        template : str
            Source container to copy.
        description : str
            Description stored under ``user.description``.
        host_port : int
            Host port to publish.
        container_port : int
            Container port to forward.
        """
        client = self._connection()
        config = {
            "name": name,
            "source": {"type": "copy", "source": template},
            "config": {DESCRIPTION_KEY: description},
        }
        container = client.instances.create(config, wait=True)
        container.start(wait=True)
        self._apply_proxy(container, host_port=host_port, container_port=container_port)

    def start(self, name: str) -> None:
        """Start a container.

        Parameters
        ----------
        name : str
            Container name.
        """
        self._connection().containers.get(name).start(wait=True)

    def stop(self, name: str) -> None:
        """Stop a container.

        Parameters
        ----------
        name : str
            Container name.
        """
        self._connection().containers.get(name).stop(wait=True)

    def rename(self, name: str, new_name: str) -> None:
        """Rename a container.

        Parameters
        ----------
        name : str
            Current container name.
        new_name : str
            New container name.
        """
        self._connection().containers.get(name).rename(new_name, wait=True)

    def add_proxy(self, name: str, *, host_port: int, container_port: int) -> None:
        """Add a proxy device to a container.

        Parameters
        ----------
        name : str
            Container name.
        host_port : int
            Host port to publish.
        container_port : int
            Container port to forward.
        """
        container = self._connection().containers.get(name)
        self._apply_proxy(container, host_port=host_port, container_port=container_port)

    @staticmethod
    def _apply_proxy(container: Any, *, host_port: int, container_port: int) -> None:
        """Attach a proxy device and save the container.

        Parameters
        ----------
        container : Any
            A ``pylxd`` container or instance object.
        host_port : int
            Host port to publish.
        container_port : int
            Container port to forward.
        """
        container.devices.update(
            {
                f"proxy-{host_port}": {
                    "type": "proxy",
                    "listen": f"tcp:0.0.0.0:{host_port}",
                    "connect": f"tcp:127.0.0.1:{container_port}",
                }
            }
        )
        container.save(wait=True)


class HubManager:
    """Business rules for the JupyterHub containers.

    Attributes
    ----------
    backend : LxdBackend
        The container operations, real or in-memory.
    max_deploy : int
        Number of deployment slots.
    host_port_base : int
        First published host port.
    container_port : int
        Port that JupyterHub listens on inside a container.
    template_container : str
        Source container that new hubs are copied from.
    container_prefix : str
        Prefix of a live hub name.
    archive_prefix : str
        Prefix of an archived hub name.
    """

    def __init__(
        self,
        backend: LxdBackend,
        *,
        max_deploy: int,
        host_port_base: int,
        container_port: int,
        template_container: str,
        container_prefix: str = "jupyterhub",
        archive_prefix: str = "jh-archive",
    ) -> None:
        """Store the backend and the naming settings.

        Parameters
        ----------
        backend : LxdBackend
            The container operations.
        max_deploy : int
            Number of deployment slots.
        host_port_base : int
            First published host port.
        container_port : int
            Port that JupyterHub listens on inside a container.
        template_container : str
            Source container that new hubs are copied from.
        container_prefix : str, optional
            Prefix of a live hub name.
        archive_prefix : str, optional
            Prefix of an archived hub name.
        """
        self.backend = backend
        self.max_deploy = max_deploy
        self.host_port_base = host_port_base
        self.container_port = container_port
        self.template_container = template_container
        self.container_prefix = container_prefix
        self.archive_prefix = archive_prefix

    def list_hubs(self) -> list[Hub]:
        """List the live hubs, sorted by slot.

        Returns
        -------
        list of Hub
            Containers whose name starts with the live prefix, in slot order.
        """
        hubs = [
            hub for hub in self.backend.list_all() if parse_slot(self.container_prefix, hub.name)
        ]
        return sorted(hubs, key=lambda hub: parse_slot(self.container_prefix, hub.name) or 0)

    def list_archived(self) -> list[Hub]:
        """List the archived hubs.

        Returns
        -------
        list of Hub
            Stopped containers whose name starts with the archive prefix, by name.
        """
        prefix = f"{self.archive_prefix}-"
        archived = [
            hub for hub in self.backend.list_all() if hub.name.startswith(prefix) and hub.stopped
        ]
        return sorted(archived, key=lambda hub: hub.name)

    def archive_tag_exists(self, tag: str) -> bool:
        """Report whether an archive tag is already in use.

        Parameters
        ----------
        tag : str
            Candidate tag.

        Returns
        -------
        bool
            ``True`` when a container is already named for that tag.

        Raises
        ------
        InvalidInputError
            When the tag is invalid.
        """
        target = archive_name(self.archive_prefix, validate_tag(tag))
        return any(hub.name == target for hub in self.backend.list_all())

    def create_hub(self, description: str) -> str:
        """Create and start a new hub in the lowest free slot.

        Parameters
        ----------
        description : str
            Description for the new hub.

        Returns
        -------
        str
            The name of the new container.

        Raises
        ------
        InvalidInputError
            When the description is invalid.
        SlotUnavailableError
            When every slot is in use.
        """
        clean = validate_description(description)
        names = [hub.name for hub in self.list_hubs()]
        slot = allocate_slot(self.container_prefix, names, self.max_deploy)
        name = hub_name(self.container_prefix, slot)
        self.backend.create(
            name=name,
            template=self.template_container,
            description=clean,
            host_port=host_port(self.host_port_base, slot),
            container_port=self.container_port,
        )
        return name

    def start_hub(self, name: str) -> None:
        """Start a stopped hub.

        Parameters
        ----------
        name : str
            Container name.

        Raises
        ------
        NotFoundError
            When the container does not exist.
        ConflictError
            When the container is already running.
        """
        hub = self.backend.get(name)
        if hub.running:
            raise ConflictError(f"{name} is already running")
        self.backend.start(name)

    def stop_hub(self, name: str) -> None:
        """Stop a running hub.

        Parameters
        ----------
        name : str
            Container name.

        Raises
        ------
        NotFoundError
            When the container does not exist.
        ConflictError
            When the container is not running.
        """
        hub = self.backend.get(name)
        if not hub.running:
            raise ConflictError(f"{name} is not running")
        self.backend.stop(name)

    def archive_hub(self, name: str, tag: str) -> str:
        """Archive a stopped hub under a tag.

        Parameters
        ----------
        name : str
            Container name to archive.
        tag : str
            Archive tag.

        Returns
        -------
        str
            The new archive container name.

        Raises
        ------
        InvalidInputError
            When the tag is invalid.
        ConflictError
            When the tag is taken, or the container is not stopped.
        NotFoundError
            When the container does not exist.
        """
        clean = validate_tag(tag)
        target = archive_name(self.archive_prefix, clean)
        if any(hub.name == target for hub in self.backend.list_all()):
            raise ConflictError(f"archive name {target} already exists")
        hub = self.backend.get(name)
        if not hub.stopped:
            raise ConflictError(f"{name} is not stopped and cannot be archived")
        self.backend.rename(name, target)
        return target

    def deploy_archived(self, name: str) -> str:
        """Rename a stopped archive into the lowest free slot and start it.

        Parameters
        ----------
        name : str
            Archived container name.

        Returns
        -------
        str
            The new live container name.

        Raises
        ------
        NotFoundError
            When the container does not exist.
        ConflictError
            When the container is not stopped.
        SlotUnavailableError
            When every slot is in use.
        """
        hub = self.backend.get(name)
        if not hub.stopped:
            raise ConflictError(f"{name} is not stopped")
        names = [live.name for live in self.list_hubs()]
        slot = allocate_slot(self.container_prefix, names, self.max_deploy)
        new_name = hub_name(self.container_prefix, slot)
        self.backend.rename(name, new_name)
        self.backend.add_proxy(
            new_name,
            host_port=host_port(self.host_port_base, slot),
            container_port=self.container_port,
        )
        self.backend.start(new_name)
        return new_name
