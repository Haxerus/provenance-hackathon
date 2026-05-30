from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ParsedRequest:
    product_attestation_id: str
    attestations: dict[str, dict[str, Any]]
    order: list[str]
    duplicate_ids: set[str]
    raw_attestations: list[dict[str, Any]]


def parse_request(payload: dict[str, Any]) -> ParsedRequest:
    product_id = str(payload.get("product_attestation_id", "") or "")
    raw = payload.get("attestations") or []
    attestations: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    seen: set[str] = set()
    duplicate_ids: set[str] = set()
    if not isinstance(raw, list):
        raw = []
    for att in raw:
        if not isinstance(att, dict):
            continue
        aid = att.get("attestation_id")
        if aid is None:
            continue
        attestation_id = str(aid)
        if attestation_id in seen:
            duplicate_ids.add(attestation_id)
        else:
            seen.add(attestation_id)
            order.append(attestation_id)
        attestations[attestation_id] = att
    raw_attestations = [att for att in raw if isinstance(att, dict)]
    return ParsedRequest(product_id, attestations, order, duplicate_ids, raw_attestations)


def _num(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def get_costs(att: dict[str, Any]) -> tuple[float, float, float]:
    costs = att.get("costs") or {}
    if not isinstance(costs, dict):
        costs = {}
    return (
        _num(costs.get("material_cad")),
        _num(costs.get("labour_hours")),
        _num(costs.get("labour_cost_cad")),
    )


def node_cost(att: dict[str, Any]) -> float:
    material, _hours, labour = get_costs(att)
    return material + labour


def get_parents(att: dict[str, Any]) -> list[dict[str, Any]]:
    parents = att.get("parents")
    return parents if isinstance(parents, list) else []


def get_output(att: dict[str, Any]) -> dict[str, Any]:
    output = att.get("output")
    return output if isinstance(output, dict) else {}
