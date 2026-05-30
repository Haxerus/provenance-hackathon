from typing import Any

from reference_lib import content_hash

from backend.core.canonical import recompute_hash
from backend.registry import load_registry


def test_recompute_hash_matches_reference(worked_chain: dict[str, Any]) -> None:
    att = worked_chain["attestations"][0]
    assert recompute_hash(att) == content_hash(att)


def test_registry_loads_keys_and_anchors() -> None:
    reg = load_registry()
    assert reg.public_key("sup-porcher")
    assert reg.private_key("sup-0001")
    anchor_id = next(iter(reg.anchors_by_id))
    assert reg.anchor(anchor_id) is not None
    assert reg.anchor(anchor_id)["product_id"]


def test_registry_unknown_supplier_returns_none() -> None:
    reg = load_registry()
    assert reg.public_key("sup-does-not-exist") is None
