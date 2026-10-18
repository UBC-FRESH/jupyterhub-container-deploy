"""In-memory stand-ins for LXD, used by the application tests.

:class:`FakeBackend` implements the :class:`~web_service.lxd_utils.LxdBackend` protocol
with a dictionary of hubs, so the business rules are tested with no daemon and no
container churn. :func:`make_fake_pylxd` builds a fake ``pylxd`` module so that
:class:`~web_service.lxd_utils.PylxdBackend` is tested without the real client.
"""

from __future__ import annotations

import types
from typing import Any

from web_service.lxd_utils import DESCRIPTION_KEY, Hub, NotFoundError


class FakeBackend:
    """An in-memory :class:`~web_service.lxd_utils.LxdBackend`.

    Attributes
    ----------
    hubs : dict of str to Hub
        The containers, keyed by name.
    created : list of dict of str to object
        Arguments passed to each :meth:`create` call.
    started : list of str
        Names passed to :meth:`start`.
    stopped : list of str
        Names passed to :meth:`stop`.
    renamed : list of tuple of (str, str)
        ``(old, new)`` pairs passed to :meth:`rename`.
    proxies : list of tuple of (str, int, int)
        ``(name, host_port, container_port)`` triples passed to :meth:`add_proxy` and
        :meth:`create`.
    """

    def __init__(self, hubs: list[Hub] | None = None) -> None:
        """Build the backend, optionally with existing hubs.

        Parameters
        ----------
        hubs : list of Hub or None, optional
            Containers to seed the store with.
        """
        self.hubs: dict[str, Hub] = {hub.name: hub for hub in hubs or []}
        self.created: list[dict[str, object]] = []
        self.started: list[str] = []
        self.stopped: list[str] = []
        self.renamed: list[tuple[str, str]] = []
        self.proxies: list[tuple[str, int, int]] = []

    def list_all(self) -> list[Hub]:
        """Return every hub.

        Returns
        -------
        list of Hub
            The stored hubs.
        """
        return list(self.hubs.values())

    def get(self, name: str) -> Hub:
        """Return one hub.

        Parameters
        ----------
        name : str
            Container name.

        Returns
        -------
        Hub
            The stored hub.

        Raises
        ------
        NotFoundError
            When the name is unknown.
        """
        if name not in self.hubs:
            raise NotFoundError(f"container {name} not found")
        return self.hubs[name]

    def create(
        self,
        *,
        name: str,
        template: str,
        description: str,
        host_port: int,
        container_port: int,
    ) -> None:
        """Record a creation and store the new running hub.

        Parameters
        ----------
        name : str
            New container name.
        template : str
            Source container name.
        description : str
            Description to store.
        host_port : int
            Host port to publish.
        container_port : int
            Container port to forward.
        """
        self.hubs[name] = Hub(name=name, status="Running", description=description)
        self.created.append(
            {
                "name": name,
                "template": template,
                "description": description,
                "host_port": host_port,
                "container_port": container_port,
            }
        )
        self.proxies.append((name, host_port, container_port))

    def start(self, name: str) -> None:
        """Start a hub.

        Parameters
        ----------
        name : str
            Container name.
        """
        self._set_status(name, "Running")
        self.started.append(name)

    def stop(self, name: str) -> None:
        """Stop a hub.

        Parameters
        ----------
        name : str
            Container name.
        """
        self._set_status(name, "Stopped")
        self.stopped.append(name)

    def rename(self, name: str, new_name: str) -> None:
        """Rename a hub.

        Parameters
        ----------
        name : str
            Current name.
        new_name : str
            New name.
        """
        hub = self.hubs.pop(name)
        self.hubs[new_name] = Hub(new_name, hub.status, hub.description)
        self.renamed.append((name, new_name))

    def add_proxy(self, name: str, *, host_port: int, container_port: int) -> None:
        """Record a proxy device.

        Parameters
        ----------
        name : str
            Container name.
        host_port : int
            Host port to publish.
        container_port : int
            Container port to forward.
        """
        self.proxies.append((name, host_port, container_port))

    def _set_status(self, name: str, status: str) -> None:
        """Replace a stored hub with the same name and a new status.

        Parameters
        ----------
        name : str
            Container name.
        status : str
            New status.
        """
        hub = self.hubs[name]
        self.hubs[name] = Hub(hub.name, status, hub.description)


class FakePylxdContainer:
    """A stand-in for a ``pylxd`` container object."""

    def __init__(
        self,
        name: str,
        status: str = "Stopped",
        description: str | None = None,
        store: dict[str, FakePylxdContainer] | None = None,
    ) -> None:
        """Build the container.

        Parameters
        ----------
        name : str
            Container name.
        status : str, optional
            Initial status.
        description : str or None, optional
            Value for ``user.description``.
        store : dict of str to FakePylxdContainer or None, optional
            Container store to keep in step when the container is renamed.
        """
        self.name = name
        self.status = status
        self.config: dict[str, str] = {} if description is None else {DESCRIPTION_KEY: description}
        self.devices: dict[str, dict[str, str]] = {}
        self.save_count = 0
        self._store = store

    def start(self, wait: bool = False) -> None:
        """Set the status to running."""
        self.status = "Running"

    def stop(self, wait: bool = False) -> None:
        """Set the status to stopped."""
        self.status = "Stopped"

    def rename(self, new_name: str, wait: bool = False) -> None:
        """Rename the container and re-key it in the store."""
        if self._store is not None:
            self._store.pop(self.name, None)
            self._store[new_name] = self
        self.name = new_name

    def save(self, wait: bool = False) -> None:
        """Count a save."""
        self.save_count += 1


class _FakeNotFoundError(Exception):
    """Stand-in for ``pylxd.exceptions.NotFound``."""


class _FakeContainers:
    """A stand-in for ``pylxd.Client().containers``."""

    def __init__(self, store: dict[str, FakePylxdContainer]) -> None:
        self._store = store

    def all(self) -> list[FakePylxdContainer]:
        """Return every container."""
        return list(self._store.values())

    def get(self, name: str) -> FakePylxdContainer:
        """Return one container or raise the fake NotFound."""
        if name not in self._store:
            raise _FakeNotFoundError(name)
        return self._store[name]


class _FakeInstances:
    """A stand-in for ``pylxd.Client().instances``."""

    def __init__(self, store: dict[str, FakePylxdContainer]) -> None:
        self._store = store

    def create(self, config: dict[str, Any], wait: bool = False) -> FakePylxdContainer:
        """Create a container from the pylxd config mapping."""
        name = str(config["name"])
        description = str(config.get("config", {}).get(DESCRIPTION_KEY, ""))
        container = FakePylxdContainer(
            name, status="Stopped", description=description, store=self._store
        )
        self._store[name] = container
        return container


class FakePylxdClient:
    """A stand-in for ``pylxd.Client``."""

    def __init__(self, endpoint: str | None = None) -> None:
        """Build the client and its container store."""
        self.endpoint = endpoint
        self.store: dict[str, FakePylxdContainer] = {}
        self.containers = _FakeContainers(self.store)
        self.instances = _FakeInstances(self.store)

    def add_container(
        self, name: str, status: str = "Stopped", description: str | None = None
    ) -> FakePylxdContainer:
        """Add a container to the store.

        Parameters
        ----------
        name : str
            Container name.
        status : str, optional
            Initial status.
        description : str or None, optional
            Value for ``user.description``.

        Returns
        -------
        FakePylxdContainer
            The added container.
        """
        container = FakePylxdContainer(name, status, description, store=self.store)
        self.store[name] = container
        return container


def make_fake_pylxd() -> types.ModuleType:
    """Build a fake ``pylxd`` module for ``sys.modules``.

    Returns
    -------
    types.ModuleType
        A module with ``Client`` and ``exceptions.NotFound``.
    """
    module = types.ModuleType("pylxd")
    module.Client = FakePylxdClient  # type: ignore[attr-defined]
    module.exceptions = types.SimpleNamespace(NotFound=_FakeNotFoundError)  # type: ignore[attr-defined]
    return module
