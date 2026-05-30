from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class ProductSummary:
    product_attestation_id: str
    name: str = ""


class AttestationStore(Protocol):
    def put(self, att: dict[str, Any]) -> None: ...
    def get(self, attestation_id: str) -> dict[str, Any] | None: ...
    def list(
        self,
        *,
        action_type: str | None = None,
        supplier_id: str | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]: ...
    def resolve_chain(self, product_attestation_id: str) -> list[dict[str, Any]]: ...
    def list_products(self) -> list[ProductSummary]: ...


def _walk(
    get_fn: Callable[[str], dict[str, Any] | None],
    leaf_id: str,
) -> list[dict[str, Any]]:
    seen: set[str] = set()
    queue = [leaf_id]
    out: list[dict[str, Any]] = []
    while queue:
        aid = queue.pop()
        if aid in seen:
            continue
        seen.add(aid)
        att = get_fn(aid)
        if att is None:
            continue
        out.append(att)
        for pref in att.get("parents") or []:
            pid = pref.get("attestation_id")
            if pid and pid not in seen:
                queue.append(str(pid))
    return out
