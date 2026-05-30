from collections.abc import Callable
from typing import Any

import pytest

from backend.store.memory import InMemoryStore
from backend.store.sqlite import SqliteStore


def _att(aid: str, parents: tuple[str, ...] = ()) -> dict[str, Any]:
    return {
        "attestation_id": aid,
        "product_id": "prod-1",
        "parents": [{"attestation_id": parent} for parent in parents],
    }


@pytest.mark.parametrize("make", [lambda: InMemoryStore(), lambda: SqliteStore(":memory:")])
def test_put_get_and_resolve_chain(make: Callable[[], object]) -> None:
    store = make()
    store.put(_att("raw"))
    store.put(_att("leaf", parents=("raw",)))
    assert store.get("leaf")["attestation_id"] == "leaf"
    chain = store.resolve_chain("leaf")
    ids = {att["attestation_id"] for att in chain}
    assert ids == {"leaf", "raw"}


@pytest.mark.parametrize("make", [lambda: InMemoryStore(), lambda: SqliteStore(":memory:")])
def test_resolve_chain_cycle_safe(make: Callable[[], object]) -> None:
    store = make()
    store.put(_att("a", parents=("b",)))
    store.put(_att("b", parents=("a",)))
    chain = store.resolve_chain("a")
    assert {att["attestation_id"] for att in chain} == {"a", "b"}
