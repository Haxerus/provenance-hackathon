from __future__ import annotations

import json
import sqlite3
from typing import Any

from backend.store.base import ProductSummary, _walk


class SqliteStore:
    def __init__(self, path: str = ":memory:") -> None:
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS attestations "
            "(attestation_id TEXT PRIMARY KEY, product_id TEXT, action_type TEXT, "
            "supplier_id TEXT, blob TEXT)"
        )
        self._conn.commit()

    def put(self, att: dict[str, Any]) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO attestations VALUES (?,?,?,?,?)",
            (
                att["attestation_id"],
                att.get("product_id"),
                att.get("action_type"),
                att.get("supplier_id"),
                json.dumps(att),
            ),
        )
        self._conn.commit()

    def get(self, attestation_id: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT blob FROM attestations WHERE attestation_id=?",
            (attestation_id,),
        ).fetchone()
        return json.loads(row[0]) if row else None

    def list(
        self,
        *,
        action_type: str | None = None,
        supplier_id: str | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        query = "SELECT blob FROM attestations WHERE 1=1"
        params: list[object] = []
        if action_type:
            query += " AND action_type=?"
            params.append(action_type)
        if supplier_id:
            query += " AND supplier_id=?"
            params.append(supplier_id)
        query += " LIMIT ?"
        params.append(limit)
        return [json.loads(row[0]) for row in self._conn.execute(query, params).fetchall()]

    def resolve_chain(self, product_attestation_id: str) -> list[dict[str, Any]]:
        return _walk(self.get, product_attestation_id)

    def list_products(self) -> list[ProductSummary]:
        rows = self._conn.execute("SELECT blob FROM attestations").fetchall()
        atts = [json.loads(row[0]) for row in rows]
        referenced_parent_ids: set[str] = set()
        for att in atts:
            for pref in att.get("parents") or []:
                pid = pref.get("attestation_id")
                if pid:
                    referenced_parent_ids.add(str(pid))
        return [
            ProductSummary(str(att["attestation_id"]), str((att.get("output") or {}).get("name", "")))
            for att in atts
            if att["attestation_id"] not in referenced_parent_ids
        ]
