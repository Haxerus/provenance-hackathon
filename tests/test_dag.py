from typing import Any

from backend.core.dag import build_context
from backend.core.parsing import parse_request


def _ctx(payload: dict[str, Any]):
    return build_context(parse_request(payload), model=None, registry=None)


def test_children_index_and_hashes(worked_chain: dict[str, Any]) -> None:
    ctx = _ctx(worked_chain)
    assert len(ctx.content_hashes) == 12
    assert ctx.product_id == "att-anchor-0012"


def test_cycle_detection_flags_cycle_nodes() -> None:
    payload = {
        "product_attestation_id": "att-a",
        "attestations": [
            {"attestation_id": "att-a", "parents": [{"attestation_id": "att-b"}]},
            {"attestation_id": "att-b", "parents": [{"attestation_id": "att-a"}]},
        ],
    }
    ctx = _ctx(payload)
    assert ctx.cycle_nodes == {"att-a", "att-b"}


def test_no_cycle_in_clean_chain(worked_chain: dict[str, Any]) -> None:
    ctx = _ctx(worked_chain)
    assert ctx.cycle_nodes == set()
