from typing import Any

from backend.model.baseline import load_baseline
from backend.registry import load_registry
from backend.verify import verify_chain
from reference_lib import content_hash, sign_attestation

M = load_baseline()
REG = load_registry()


def test_worked_example_is_clean_and_correct(
    worked_chain: dict[str, Any],
    worked_expected: dict[str, Any],
) -> None:
    res = verify_chain(worked_chain, M, REG)
    assert res["chain_valid"] is True
    assert res["anomalies"] == []
    assert res["designation"] == worked_expected["designation"]
    assert abs(res["canadian_content_percentage"] - worked_expected["canadian_content_percentage"]) <= 0.1


def test_malformed_payload_returns_wellformed_response() -> None:
    res = verify_chain({"garbage": True}, M, REG)
    assert set(res) == {
        "product_attestation_id",
        "canadian_content_percentage",
        "designation",
        "chain_valid",
        "anomalies",
    }


def test_none_payload_does_not_crash() -> None:
    res = verify_chain(None, M, REG)
    assert res["designation"] == "none"


def test_hard_integrity_anomaly_suppresses_soft_statistical_extras() -> None:
    parent = {
        "attestation_id": "parent",
        "version": "1.0",
        "supplier_id": "sup-0001",
        "timestamp": "2026-01-01T09:00:00Z",
        "action_type": "raw_material_supply",
        "performed_in_country": "CA",
        "parents": [],
        "output": {"name": "Raw", "quantity_produced": 10, "unit": "u"},
        "costs": {"material_cad": 100, "labour_hours": 0, "labour_cost_cad": 0},
    }
    child = {
        "attestation_id": "child",
        "version": "1.0",
        "supplier_id": "sup-0001",
        "timestamp": "2026-01-02T14:30:00Z",
        "action_type": "final_integration",
        "performed_in_country": "ZZ",
        "parents": [{"attestation_id": "parent", "content_hash": "bad", "quantity_consumed": 1, "unit": "u"}],
        "output": {"name": "Done", "quantity_produced": 1, "unit": "units"},
        "costs": {"material_cad": 0, "labour_hours": 10, "labour_cost_cad": 1000},
    }
    payload = {
        "product_attestation_id": "child",
        "attestations": [
            sign_attestation(parent, REG.private_key("sup-0001")),
            sign_attestation(child, REG.private_key("sup-0001")),
        ],
    }
    assert payload["attestations"][1]["parents"][0]["content_hash"] != content_hash(payload["attestations"][0])
    res = verify_chain(payload, M, REG)
    assert {a["type"] for a in res["anomalies"]} == {"parent_hash_mismatch"}
