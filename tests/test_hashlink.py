from typing import Any

from backend.core.dag import build_context
from backend.core.parsing import parse_request
from backend.detectors.hashlink import detect_hashlink
from backend.registry import load_registry

REG = load_registry()


def _ctx(payload: dict[str, Any]):
    return build_context(parse_request(payload), registry=REG)


def test_clean_chain_no_hashlink_flags(worked_chain: dict[str, Any]) -> None:
    assert detect_hashlink(_ctx(worked_chain)) == []


def test_parent_hash_mismatch_flags_child() -> None:
    payload = {
        "product_attestation_id": "child",
        "attestations": [
            {
                "attestation_id": "child",
                "parents": [{"attestation_id": "par", "content_hash": "deadbeef"}],
                "output": {"unit": "u"},
            },
            {
                "attestation_id": "par",
                "parents": [],
                "output": {"name": "p", "quantity_produced": 1, "unit": "u"},
                "costs": {"material_cad": 1, "labour_hours": 0, "labour_cost_cad": 0},
            },
        ],
    }
    flagged = {(a.attestation_id, a.type) for a in detect_hashlink(_ctx(payload))}
    assert ("child", "parent_hash_mismatch") in flagged


def test_anchor_mismatch_flags_node() -> None:
    anchor_id = next(iter(REG.anchors_by_id))
    payload = {
        "product_attestation_id": anchor_id,
        "attestations": [
            {
                "attestation_id": anchor_id,
                "parents": [],
                "supplier_id": "sup-0001",
                "costs": {"material_cad": 999, "labour_hours": 0, "labour_cost_cad": 0},
            },
        ],
    }
    flagged = {(a.attestation_id, a.type) for a in detect_hashlink(_ctx(payload))}
    assert (anchor_id, "anchor_mismatch") in flagged
