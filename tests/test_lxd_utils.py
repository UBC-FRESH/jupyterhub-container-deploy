"""Tests for the container naming rules, the hub manager, and the pylxd backend."""

from __future__ import annotations

import sys
from typing import Any

import pytest

from tests.fakes import FailingBackend, FakeBackend, FakePylxdClient, make_fake_pylxd
from web_service.lxd_utils import (
    BackendError,
    ConflictError,
    Hub,
    HubManager,
    InvalidInputError,
    NotFoundError,
    PylxdBackend,
    SlotUnavailableError,
    allocate_slot,
    archive_name,
    host_port,
    hub_name,
    parse_slot,
    validate_description,
    validate_tag,
)


def make_manager(backend: FakeBackend, *, max_deploy: int = 50) -> HubManager:
    """Build a manager over a fake backend.

    Parameters
    ----------
    backend : FakeBackend
        The in-memory backend.
    max_deploy : int, optional
        Number of slots.

    Returns
    -------
    HubManager
        The manager under test.
    """
    return HubManager(
        backend,
        max_deploy=max_deploy,
        host_port_base=8100,
        container_port=8000,
        template_container="jh-template",
    )


def test_hub_name_pads_the_slot() -> None:
    """The name zero-pads the slot to two digits."""
    assert hub_name("jupyterhub", 7) == "jupyterhub07"
    assert hub_name("jupyterhub", 50) == "jupyterhub50"


def test_host_port_is_base_plus_slot() -> None:
    """Slot 1 is port 8101 and slot 50 is port 8150."""
    assert host_port(8100, 1) == 8101
    assert host_port(8100, 50) == 8150


def test_archive_name_prefixes_the_tag() -> None:
    """The archive name joins the prefix and the tag with a hyphen."""
    assert archive_name("jh-archive", "spring") == "jh-archive-spring"


@pytest.mark.parametrize(
    ("name", "expected"),
    [("jupyterhub01", 1), ("jupyterhub50", 50), ("jupyterhub7", None), ("jh-archive-x", None)],
)
def test_parse_slot_recovers_the_number(name: str, expected: int | None) -> None:
    """Only ``prefix`` plus two or three digits yields a slot."""
    assert parse_slot("jupyterhub", name) == expected


@pytest.mark.parametrize("tag", ["spring", "sp-2026", "a.b_c", "x1"])
def test_valid_tags_are_lowercased(tag: str) -> None:
    """A valid tag is normalized to lowercase."""
    assert validate_tag(tag) == tag.lower()


@pytest.mark.parametrize("tag", ["", "-bad", "has space", "UPPER!", "a" * 64])
def test_invalid_tags_are_rejected(tag: str) -> None:
    """An empty, long, or oddly-shaped tag is rejected."""
    with pytest.raises(InvalidInputError):
        validate_tag(tag)


def test_valid_description_is_trimmed() -> None:
    """Surrounding whitespace is removed from a description."""
    assert validate_description("  spring cohort  ") == "spring cohort"


@pytest.mark.parametrize("description", ["", "   ", "x" * 201, "bad\nline"])
def test_invalid_descriptions_are_rejected(description: str) -> None:
    """An empty, long, or control-character description is rejected."""
    with pytest.raises(InvalidInputError):
        validate_description(description)


def test_allocate_slot_returns_the_lowest_free_slot() -> None:
    """The lowest unused slot wins, even when higher slots are free."""
    assert allocate_slot("jupyterhub", ["jupyterhub01", "jupyterhub03"], 50) == 2


def test_allocate_slot_raises_when_full() -> None:
    """A full set of slots raises ``SlotUnavailableError``."""
    names = [f"jupyterhub{slot:02d}" for slot in range(1, 51)]
    with pytest.raises(SlotUnavailableError):
        allocate_slot("jupyterhub", names, 50)


def test_hub_status_helpers() -> None:
    """The status helpers ignore case."""
    assert Hub("x", "Running").running
    assert Hub("x", "Stopped").stopped
    assert not Hub("x", "Running").stopped


def test_list_hubs_filters_and_sorts_by_slot() -> None:
    """Live hubs are returned in slot order, and other containers are ignored."""
    backend = FakeBackend(
        [
            Hub("jupyterhub10", "Running"),
            Hub("jupyterhub02", "Stopped"),
            Hub("jh-archive-x", "Stopped"),
            Hub("unrelated", "Running"),
        ]
    )
    names = [hub.name for hub in make_manager(backend).list_hubs()]
    assert names == ["jupyterhub02", "jupyterhub10"]


def test_list_archived_keeps_only_stopped_archives() -> None:
    """Archived hubs are the stopped containers that carry the archive prefix."""
    backend = FakeBackend(
        [
            Hub("jh-archive-a", "Stopped"),
            Hub("jh-archive-b", "Running"),
            Hub("jupyterhub01", "Stopped"),
        ]
    )
    names = [hub.name for hub in make_manager(backend).list_archived()]
    assert names == ["jh-archive-a"]


def test_create_hub_uses_the_lowest_slot_and_sets_the_port() -> None:
    """A new hub lands in the lowest free slot with the matching host port."""
    backend = FakeBackend([Hub("jupyterhub01", "Running")])
    name = make_manager(backend).create_hub("spring")
    assert name == "jupyterhub02"
    assert backend.created[0]["host_port"] == 8102
    assert backend.created[0]["template"] == "jh-template"
    assert backend.created[0]["description"] == "spring"


def test_create_hub_rejects_a_bad_description() -> None:
    """An empty description is rejected before any backend call."""
    backend = FakeBackend()
    with pytest.raises(InvalidInputError):
        make_manager(backend).create_hub("")
    assert backend.created == []


def test_create_hub_raises_when_full() -> None:
    """A full set of slots raises before any backend call."""
    backend = FakeBackend([Hub(f"jupyterhub{slot:02d}", "Running") for slot in range(1, 51)])
    with pytest.raises(SlotUnavailableError):
        make_manager(backend).create_hub("spring")
    assert backend.created == []


def test_start_hub_starts_a_stopped_hub() -> None:
    """Starting a stopped hub calls the backend once."""
    backend = FakeBackend([Hub("jupyterhub01", "Stopped")])
    make_manager(backend).start_hub("jupyterhub01")
    assert backend.started == ["jupyterhub01"]


def test_start_hub_conflicts_when_running() -> None:
    """Starting a running hub is a conflict."""
    backend = FakeBackend([Hub("jupyterhub01", "Running")])
    with pytest.raises(ConflictError):
        make_manager(backend).start_hub("jupyterhub01")


def test_start_hub_reports_a_missing_hub() -> None:
    """Starting an unknown hub is a not-found error."""
    with pytest.raises(NotFoundError):
        make_manager(FakeBackend()).start_hub("jupyterhub99")


def test_stop_hub_stops_a_running_hub() -> None:
    """Stopping a running hub calls the backend once."""
    backend = FakeBackend([Hub("jupyterhub01", "Running")])
    make_manager(backend).stop_hub("jupyterhub01")
    assert backend.stopped == ["jupyterhub01"]


def test_stop_hub_conflicts_when_stopped() -> None:
    """Stopping a stopped hub is a conflict."""
    backend = FakeBackend([Hub("jupyterhub01", "Stopped")])
    with pytest.raises(ConflictError):
        make_manager(backend).stop_hub("jupyterhub01")


def test_archive_hub_renames_a_stopped_hub() -> None:
    """Archiving a stopped hub renames it to the archive name."""
    backend = FakeBackend([Hub("jupyterhub01", "Stopped")])
    target = make_manager(backend).archive_hub("jupyterhub01", "Spring")
    assert target == "jh-archive-spring"
    assert backend.renamed == [("jupyterhub01", "jh-archive-spring")]


def test_archive_hub_rejects_a_taken_tag() -> None:
    """An archive tag that is already in use is a conflict."""
    backend = FakeBackend([Hub("jupyterhub01", "Stopped"), Hub("jh-archive-spring", "Stopped")])
    with pytest.raises(ConflictError, match="already exists"):
        make_manager(backend).archive_hub("jupyterhub01", "spring")


def test_archive_hub_rejects_a_running_hub() -> None:
    """A running hub cannot be archived."""
    backend = FakeBackend([Hub("jupyterhub01", "Running")])
    with pytest.raises(ConflictError, match="not stopped"):
        make_manager(backend).archive_hub("jupyterhub01", "spring")


def test_archive_hub_rejects_a_bad_tag() -> None:
    """An invalid tag is rejected."""
    backend = FakeBackend([Hub("jupyterhub01", "Stopped")])
    with pytest.raises(InvalidInputError):
        make_manager(backend).archive_hub("jupyterhub01", "bad tag")


def test_archive_tag_exists_reads_the_store() -> None:
    """The tag check reflects the containers that exist."""
    backend = FakeBackend([Hub("jh-archive-spring", "Stopped")])
    manager = make_manager(backend)
    assert manager.archive_tag_exists("spring") is True
    assert manager.archive_tag_exists("summer") is False


def test_deploy_archived_renames_proxies_and_starts() -> None:
    """Deploying an archive renames it into a slot, adds a proxy, and starts it."""
    backend = FakeBackend([Hub("jh-archive-spring", "Stopped"), Hub("jupyterhub01", "Running")])
    name = make_manager(backend).deploy_archived("jh-archive-spring")
    assert name == "jupyterhub02"
    assert backend.renamed == [("jh-archive-spring", "jupyterhub02")]
    assert backend.proxies == [("jupyterhub02", 8102, 8000)]
    assert backend.started == ["jupyterhub02"]


def test_deploy_archived_rejects_a_running_container() -> None:
    """A running container cannot be deployed from the archive list."""
    backend = FakeBackend([Hub("jh-archive-spring", "Running")])
    with pytest.raises(ConflictError, match="not stopped"):
        make_manager(backend).deploy_archived("jh-archive-spring")


def test_deploy_archived_raises_when_full() -> None:
    """Deploying an archive with no free slot is a conflict."""
    backend = FakeBackend(
        [Hub("jh-archive-spring", "Stopped")]
        + [Hub(f"jupyterhub{slot:02d}", "Running") for slot in range(1, 51)]
    )
    with pytest.raises(SlotUnavailableError):
        make_manager(backend).deploy_archived("jh-archive-spring")


def test_pylxd_backend_create_get_and_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    """The pylxd backend creates a running container with a proxy device."""
    monkeypatch.setitem(sys.modules, "pylxd", make_fake_pylxd())
    backend = PylxdBackend()
    backend.create(
        name="jupyterhub01",
        template="jh-template",
        description="spring",
        host_port=8101,
        container_port=8000,
    )
    hub = backend.get("jupyterhub01")
    assert hub.running
    assert hub.description == "spring"
    store: dict[str, Any] = backend._connection().store
    assert store["jupyterhub01"].devices["proxy-8101"]["connect"] == "tcp:127.0.0.1:8000"


def test_pylxd_backend_get_missing_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """A missing container becomes a ``NotFoundError``."""
    monkeypatch.setitem(sys.modules, "pylxd", make_fake_pylxd())
    with pytest.raises(NotFoundError):
        PylxdBackend().get("jupyterhub99")


def test_pylxd_backend_lifecycle(monkeypatch: pytest.MonkeyPatch) -> None:
    """Start, stop, rename, and add_proxy reach the fake client."""
    monkeypatch.setitem(sys.modules, "pylxd", make_fake_pylxd())
    backend = PylxdBackend()
    client: FakePylxdClient = backend._connection()
    client.add_container("jupyterhub01", "Stopped")
    backend.start("jupyterhub01")
    assert backend.get("jupyterhub01").running
    backend.stop("jupyterhub01")
    assert backend.get("jupyterhub01").stopped
    backend.rename("jupyterhub01", "jh-archive-x")
    assert "jh-archive-x" in client.store
    backend.add_proxy("jh-archive-x", host_port=8105, container_port=8000)
    assert client.store["jh-archive-x"].devices["proxy-8105"]["listen"] == "tcp:0.0.0.0:8105"


def test_pylxd_backend_reuses_the_connection(monkeypatch: pytest.MonkeyPatch) -> None:
    """The client connects once and is reused."""
    monkeypatch.setitem(sys.modules, "pylxd", make_fake_pylxd())
    backend = PylxdBackend(endpoint="/tmp/lxd.sock")
    first = backend._connection()
    assert backend._connection() is first
    assert first.endpoint == "/tmp/lxd.sock"


def test_capacity_counts_used_and_free_slots() -> None:
    """The capacity counts the live hubs against the slot total."""
    backend = FakeBackend([Hub("jupyterhub01", "Running"), Hub("jupyterhub02", "Stopped")])
    usage = make_manager(backend).capacity()
    assert (usage.used, usage.free, usage.total) == (2, 48, 50)


def test_health_reports_a_reachable_backend() -> None:
    """A reachable backend is healthy, with the free slot count."""
    status = make_manager(FakeBackend()).health()
    assert status.healthy is True
    assert status.free_slots == 50
    assert status.total_slots == 50


def test_health_reports_an_unreachable_backend() -> None:
    """A failing backend is unhealthy, with zero free slots."""
    status = make_manager(FailingBackend()).health()
    assert status.healthy is False
    assert status.free_slots == 0
    assert status.total_slots == 50


def _raise_runtime(*_args: object, **_kwargs: object) -> object:
    """Raise a transport error, for the error-translation tests."""
    raise RuntimeError("socket gone")


def test_pylxd_backend_list_all_translates_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """A transport error while listing becomes a ``BackendError``."""
    monkeypatch.setitem(sys.modules, "pylxd", make_fake_pylxd())
    backend = PylxdBackend()
    monkeypatch.setattr(backend._connection().containers, "all", _raise_runtime)
    with pytest.raises(BackendError):
        backend.list_all()


def test_pylxd_backend_get_translates_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """A transport error while fetching becomes a ``BackendError``."""
    monkeypatch.setitem(sys.modules, "pylxd", make_fake_pylxd())
    backend = PylxdBackend()
    monkeypatch.setattr(backend._connection().containers, "get", _raise_runtime)
    with pytest.raises(BackendError):
        backend.get("jupyterhub01")


def test_pylxd_backend_write_translates_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """A transport error during a write becomes a ``BackendError``."""
    monkeypatch.setitem(sys.modules, "pylxd", make_fake_pylxd())
    backend = PylxdBackend()
    monkeypatch.setattr(backend._connection().containers, "get", _raise_runtime)
    with pytest.raises(BackendError):
        backend.start("jupyterhub01")
