from __future__ import annotations

from typing import Any

from backend.store.base import ProductSummary, _walk


class InMemoryStore:
    def __init__(self) -> None:
        self._data: dict[str, dict[str, Any]] = {}

    def put(self, att: dict[str, Any]) -> None:
        self._data[str(att["attestation_id"])] = att

    def get(self, attestation_id: str) -> dict[str, Any] | None:
        return self._data.get(attestation_id)

    def list(
        self,
        *,
        action_type: str | None = None,
        supplier_id: str | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for att in self._data.values():
            if action_type and att.get("action_type") != action_type:
                continue
            if supplier_id and att.get("supplier_id") != supplier_id:
                continue
            out.append(att)
            if len(out) >= limit:
                break
        return out

    def resolve_chain(self, product_attestation_id: str) -> list[dict[str, Any]]:
        return _walk(self.get, product_attestation_id)

    def list_products(self) -> list[ProductSummary]:
        referenced_parent_ids: set[str] = set()
        for att in self._data.values():
            for pref in att.get("parents") or []:
                pid = pref.get("attestation_id")
                if pid:
                    referenced_parent_ids.add(str(pid))
        leaves = [att for aid, att in self._data.items() if aid not in referenced_parent_ids]
        return [
            ProductSummary(str(att["attestation_id"]), str((att.get("output") or {}).get("name", "")))
            for att in leaves
        ]
