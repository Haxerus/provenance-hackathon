from typing import Any

from backend.core.dag import build_context
from backend.core.parsing import parse_request
from backend.detectors.massbalance import detect_mass_balance


def _ctx(payload: dict[str, Any]):
    return build_context(parse_request(payload))


def test_clean_chain_no_flag(worked_chain: dict[str, Any]) -> None:
    assert detect_mass_balance(_ctx(worked_chain)) == []


def test_global_over_consumption_flags_parent() -> None:
    payload = {
        "product_attestation_id": "leaf",
        "attestations": [
            {
                "attestation_id": "raw",
                "parents": [],
                "output": {"name": "r", "quantity_produced": 10, "unit": "u"},
                "costs": {"material_cad": 1, "labour_hours": 0, "labour_cost_cad": 0},
            },
            {"attestation_id": "c1", "parents": [{"attestation_id": "raw", "quantity_consumed": 6, "unit": "u"}]},
            {"attestation_id": "c2", "parents": [{"attestation_id": "raw", "quantity_consumed": 6, "unit": "u"}]},
        ],
    }
    flagged = [(a.attestation_id, a.type) for a in detect_mass_balance(_ctx(payload))]
    assert flagged == [("raw", "mass_balance_violation")]


def test_under_consumption_not_flagged() -> None:
    payload = {
        "product_attestation_id": "leaf",
        "attestations": [
            {"attestation_id": "raw", "parents": [], "output": {"name": "r", "quantity_produced": 10, "unit": "u"}},
            {"attestation_id": "c1", "parents": [{"attestation_id": "raw", "quantity_consumed": 3, "unit": "u"}]},
        ],
    }
    assert detect_mass_balance(_ctx(payload)) == []
