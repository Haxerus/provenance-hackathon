from typing import Any

from fastapi.testclient import TestClient

from backend.app import app
from backend.registry import load_registry

client = TestClient(app)


def test_canonicalize_returns_hash(worked_chain: dict[str, Any]) -> None:
    att = worked_chain["attestations"][0]
    response = client.post("/api/canonicalize", json=att)
    assert response.status_code == 200

    from reference_lib import content_hash

    assert response.json()["content_hash"] == content_hash(att)


def test_registry_keys_are_public_only() -> None:
    response = client.get("/api/registry/keys")
    assert response.status_code == 200
    assert "private" not in response.text.lower()


def test_anchor_lookup() -> None:
    anchor_id = next(iter(load_registry().anchors_by_id))
    response = client.get(f"/api/registry/anchors/{anchor_id}")
    assert response.status_code == 200
    assert response.json()["product_id"]
