from typing import Any

from backend.core.dag import build_context
from backend.core.parsing import parse_request
from backend.detectors.invariants import detect_invariants


def _ctx(payload: dict[str, Any]):
    return build_context(parse_request(payload))


def test_clean_chain_no_flag(worked_chain: dict[str, Any]) -> None:
    assert detect_invariants(_ctx(worked_chain)) == []


def test_transformation_implausible_zero_parents() -> None:
    payload = {
        "product_attestation_id": "t",
        "attestations": [
            {
                "attestation_id": "t",
                "action_type": "final_integration",
                "parents": [],
                "costs": {"material_cad": 0, "labour_hours": 10, "labour_cost_cad": 1000},
            },
        ],
    }
    flagged = {(a.attestation_id, a.type) for a in detect_invariants(_ctx(payload))}
    assert ("t", "transformation_implausible") in flagged


def test_cost_role_violation_transform_with_material() -> None:
    payload = {
        "product_attestation_id": "t",
        "attestations": [
            {
                "attestation_id": "t",
                "action_type": "component_manufacture",
                "parents": [{"attestation_id": "p"}],
                "costs": {"material_cad": 50, "labour_hours": 5, "labour_cost_cad": 300},
            },
            {
                "attestation_id": "p",
                "action_type": "raw_material_supply",
                "parents": [],
                "costs": {"material_cad": 10, "labour_hours": 0, "labour_cost_cad": 0},
            },
        ],
    }
    flagged = {(a.attestation_id, a.type) for a in detect_invariants(_ctx(payload))}
    assert ("t", "cost_role_violation") in flagged


def test_negative_cost_flagged() -> None:
    payload = {
        "product_attestation_id": "r",
        "attestations": [
            {
                "attestation_id": "r",
                "action_type": "raw_material_supply",
                "parents": [],
                "costs": {"material_cad": -5, "labour_hours": 0, "labour_cost_cad": 0},
            },
        ],
    }
    flagged = {a.type for a in detect_invariants(_ctx(payload))}
    assert "impossible_value" in flagged
