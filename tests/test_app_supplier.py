from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


def test_list_suppliers() -> None:
    response = client.get("/api/suppliers")
    assert response.status_code == 200
    ids = {supplier["supplier_id"] for supplier in response.json()}
    assert "sup-0001" in ids


def test_issue_attestation_is_signed_and_verifiable() -> None:
    body = {
        "supplier_id": "sup-0001",
        "action_type": "raw_material_supply",
        "performed_in_country": "CA",
        "parents": [],
        "output": {"name": "Widget", "quantity_produced": 10, "unit": "u"},
        "costs": {"material_cad": 100, "labour_hours": 0, "labour_cost_cad": 0},
    }
    response = client.post("/api/attestations", json=body)
    assert response.status_code == 200
    att = response.json()
    assert att["attestation_id"].startswith("att-")
    assert att["signature"]["algorithm"] == "ed25519"
    got = client.get(f"/api/attestations/{att['attestation_id']}")
    assert got.status_code == 200

    from reference_lib import verify_attestation
    from backend.registry import load_registry

    assert verify_attestation(att, load_registry().public_key("sup-0001")) is True
