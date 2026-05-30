from typing import Any

from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


def _issue(body: dict[str, Any]) -> dict[str, Any]:
    return client.post("/api/attestations", json=body).json()


def test_product_lookup_returns_chain_verification_graph() -> None:
    raw = _issue(
        {
            "supplier_id": "sup-0001",
            "action_type": "raw_material_supply",
            "performed_in_country": "CA",
            "parents": [],
            "output": {"name": "Raw", "quantity_produced": 10, "unit": "u"},
            "costs": {"material_cad": 100, "labour_hours": 0, "labour_cost_cad": 0},
        }
    )
    leaf = _issue(
        {
            "supplier_id": "sup-0001",
            "action_type": "final_integration",
            "performed_in_country": "CA",
            "parents": [{"attestation_id": raw["attestation_id"], "quantity_consumed": 1, "unit": "u"}],
            "output": {"name": "Drone", "quantity_produced": 1, "unit": "units"},
            "costs": {"material_cad": 0, "labour_hours": 10, "labour_cost_cad": 1000},
        }
    )
    response = client.get(f"/api/products/{leaf['attestation_id']}")
    assert response.status_code == 200
    body = response.json()
    assert "verification" in body
    assert "graph" in body
    assert "designation_detail" in body
    assert body["verification"]["designation"] in {"made_in_canada", "product_of_canada", "none"}
    assert len(body["graph"]["nodes"]) == 2
    assert "qualifying_statement" in body["designation_detail"]


def test_list_products() -> None:
    response = client.get("/api/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_unknown_product_returns_404() -> None:
    response = client.get("/api/products/does-not-exist")
    assert response.status_code == 404
