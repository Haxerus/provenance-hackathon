from backend.core.dag import build_context
from backend.core.parsing import parse_request
from backend.detectors.statistical import detect_statistical
from backend.model.baseline import load_baseline

M = load_baseline()


def _ctx(payload: dict[str, object]):
    return build_context(parse_request(payload), model=M)


def test_cost_anomaly_thousand_per_hour() -> None:
    payload = {
        "product_attestation_id": "t",
        "attestations": [
            {
                "attestation_id": "t",
                "action_type": "component_manufacture",
                "performed_in_country": "CA",
                "timestamp": "2026-02-01T14:30:00Z",
                "supplier_id": "sup-0001",
                "parents": [{"attestation_id": "p"}],
                "costs": {"material_cad": 0, "labour_hours": 8, "labour_cost_cad": 8000},
            },
        ],
    }
    flagged = {(a.attestation_id, a.type) for a in detect_statistical(_ctx(payload))}
    assert ("t", "cost_anomaly") in flagged


def test_timing_outlier() -> None:
    payload = {
        "product_attestation_id": "t",
        "attestations": [
            {
                "attestation_id": "t",
                "action_type": "final_integration",
                "performed_in_country": "CA",
                "timestamp": "2026-02-01T04:03:21Z",
                "supplier_id": "sup-0001",
                "parents": [{"attestation_id": "p"}],
                "costs": {"material_cad": 0, "labour_hours": 12, "labour_cost_cad": 1260},
            },
        ],
    }
    flagged = {(a.attestation_id, a.type) for a in detect_statistical(_ctx(payload))}
    assert ("t", "timing_anomaly") in flagged


def test_normal_node_not_flagged() -> None:
    payload = {
        "product_attestation_id": "t",
        "attestations": [
            {
                "attestation_id": "t",
                "action_type": "component_manufacture",
                "performed_in_country": "CA",
                "timestamp": "2026-02-01T14:30:00Z",
                "supplier_id": "sup-0001",
                "parents": [{"attestation_id": "p"}],
                "costs": {"material_cad": 0, "labour_hours": 7, "labour_cost_cad": 455},
            },
        ],
    }
    assert detect_statistical(_ctx(payload)) == []
