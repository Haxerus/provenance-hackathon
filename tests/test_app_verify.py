from typing import Any

from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


def test_verify_endpoint_on_worked_example(
    worked_chain: dict[str, Any],
    worked_expected: dict[str, Any],
) -> None:
    response = client.post("/verify", json=worked_chain)
    assert response.status_code == 200
    body = response.json()
    assert body["product_attestation_id"] == "att-anchor-0012"
    assert body["designation"] == worked_expected["designation"]
    assert body["chain_valid"] is True


def test_verify_endpoint_malformed_returns_200() -> None:
    response = client.post("/verify", json={"nonsense": 1})
    assert response.status_code == 200
    assert response.json()["designation"] == "none"


def test_health() -> None:
    assert client.get("/health").json()["status"] == "ok"
