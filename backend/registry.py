import json
from dataclasses import dataclass
from typing import Any

from backend import config


@dataclass(frozen=True)
class Registry:
    public_keys: dict[str, str]
    private_keys: dict[str, str]
    anchors_by_id: dict[str, dict[str, str]]

    def public_key(self, supplier_id: str | None) -> str | None:
        if supplier_id is None:
            return None
        return self.public_keys.get(supplier_id)

    def private_key(self, supplier_id: str | None) -> str | None:
        if supplier_id is None:
            return None
        return self.private_keys.get(supplier_id)

    def anchor(self, attestation_id: str | None) -> dict[str, str] | None:
        if attestation_id is None:
            return None
        return self.anchors_by_id.get(attestation_id)


def _load_keys(path: str) -> dict[str, str]:
    with open(path) as f:
        payload: dict[str, Any] = json.load(f)
    return dict(payload.get("keys", {}))


def load_registry() -> Registry:
    with open(config.ANCHOR_PATH) as f:
        anchor_payload: dict[str, Any] = json.load(f)
    anchors = anchor_payload.get("anchors", [])
    by_id = {
        anchor["attestation_id"]: {
            "content_hash": anchor["content_hash"],
            "product_id": anchor["product_id"],
        }
        for anchor in anchors
    }
    return Registry(
        public_keys=_load_keys(config.PUBLIC_KEYS_PATH),
        private_keys=_load_keys(config.PRIVATE_KEYS_PATH),
        anchors_by_id=by_id,
    )
