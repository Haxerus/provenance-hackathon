from typing import Any

from backend.core.computation import compute
from backend.core.dag import build_context
from backend.core.parsing import parse_request


def _ctx(payload: dict[str, Any]):
    return build_context(parse_request(payload))


def test_worked_example(worked_chain: dict[str, Any], worked_expected: dict[str, Any]) -> None:
    res = compute(_ctx(worked_chain))
    assert abs(res.percentage - worked_expected["canadian_content_percentage"]) <= 0.1
    assert res.designation == worked_expected["designation"]


def test_zero_cost_is_none() -> None:
    payload = {
        "product_attestation_id": "a",
        "attestations": [
            {
                "attestation_id": "a",
                "action_type": "final_integration",
                "performed_in_country": "CA",
                "parents": [],
                "costs": {"material_cad": 0, "labour_hours": 0, "labour_cost_cad": 0},
            },
        ],
    }
    res = compute(_ctx(payload))
    assert res.designation == "none"


def test_last_substantial_transformation_not_ca_is_none() -> None:
    payload = {
        "product_attestation_id": "leaf",
        "attestations": [
            {
                "attestation_id": "leaf",
                "action_type": "final_integration",
                "performed_in_country": "US",
                "parents": [{"attestation_id": "raw"}],
                "costs": {"material_cad": 0, "labour_hours": 10, "labour_cost_cad": 1000},
            },
            {
                "attestation_id": "raw",
                "action_type": "raw_material_supply",
                "performed_in_country": "CA",
                "parents": [],
                "costs": {"material_cad": 10, "labour_hours": 0, "labour_cost_cad": 0},
            },
        ],
    }
    res = compute(_ctx(payload))
    assert res.designation == "none"


def test_made_in_canada_qualifying_statement() -> None:
    payload = {
        "product_attestation_id": "leaf",
        "attestations": [
            {
                "attestation_id": "leaf",
                "action_type": "final_integration",
                "performed_in_country": "CA",
                "parents": [{"attestation_id": "raw"}],
                "costs": {"material_cad": 0, "labour_hours": 10, "labour_cost_cad": 600},
            },
            {
                "attestation_id": "raw",
                "action_type": "raw_material_supply",
                "performed_in_country": "US",
                "parents": [],
                "costs": {"material_cad": 400, "labour_hours": 0, "labour_cost_cad": 0},
            },
        ],
    }
    res = compute(_ctx(payload))
    assert res.designation == "made_in_canada"
    assert "imported" in res.qualifying_statement.lower()


def test_duplicate_attestations_are_counted_for_percentage() -> None:
    payload = {
        "product_attestation_id": "leaf",
        "attestations": [
            {
                "attestation_id": "leaf",
                "action_type": "final_integration",
                "performed_in_country": "CA",
                "parents": [{"attestation_id": "raw"}],
                "costs": {"material_cad": 0, "labour_hours": 10, "labour_cost_cad": 100},
            },
            {
                "attestation_id": "raw",
                "action_type": "raw_material_supply",
                "performed_in_country": "US",
                "parents": [],
                "costs": {"material_cad": 100, "labour_hours": 0, "labour_cost_cad": 0},
            },
            {
                "attestation_id": "raw",
                "action_type": "raw_material_supply",
                "performed_in_country": "US",
                "parents": [],
                "costs": {"material_cad": 100, "labour_hours": 0, "labour_cost_cad": 0},
            },
        ],
    }
    res = compute(_ctx(payload))
    assert res.percentage == 33.3
