from collections import deque
from dataclasses import dataclass
from typing import Any

from backend.core.dag import ChainContext
from backend.core.parsing import get_costs, get_parents, node_cost

TRANSFORM_ACTIONS = {"component_manufacture", "subassembly", "final_integration"}


@dataclass(frozen=True)
class ComputationResult:
    percentage: float
    designation: str
    qualifying_statement: str
    ca_cost: float
    imported_cost: float


def _is_substantial(att: dict[str, Any]) -> bool:
    _material, hours, _labour = get_costs(att)
    return att.get("action_type") in TRANSFORM_ACTIONS and hours >= 4


def _last_substantial_country(ctx: ChainContext) -> tuple[str | None, bool]:
    if ctx.product_id not in ctx.attestations:
        return None, False
    visited: set[str] = set()
    queue: deque[str] = deque([ctx.product_id])
    while queue:
        aid = queue.popleft()
        if aid in visited or aid not in ctx.attestations:
            continue
        visited.add(aid)
        att = ctx.attestations[aid]
        if _is_substantial(att):
            country = att.get("performed_in_country")
            return str(country) if country is not None else None, True
        for pref in get_parents(att):
            pid = pref.get("attestation_id")
            if pid is not None and str(pid) not in visited:
                queue.append(str(pid))
    return None, False


def compute(ctx: ChainContext) -> ComputationResult:
    total = 0.0
    ca_cost = 0.0
    source_attestations = ctx.raw_attestations if ctx.raw_attestations else list(ctx.attestations.values())
    for att in source_attestations:
        cost = node_cost(att)
        total += cost
        if att.get("performed_in_country") == "CA":
            ca_cost += cost
    imported = total - ca_cost
    if total <= 0:
        return ComputationResult(0.0, "none", "", 0.0, 0.0)

    percentage = 100.0 * ca_cost / total
    country, exists = _last_substantial_country(ctx)
    if not exists or country != "CA":
        designation = "none"
    elif percentage >= 98:
        designation = "product_of_canada"
    elif percentage >= 51:
        designation = "made_in_canada"
    else:
        designation = "none"

    qualifying = ""
    if designation == "made_in_canada":
        qualifying = "Made in Canada with imported parts" if imported > 0 else "Made in Canada"

    return ComputationResult(
        round(percentage, 1),
        designation,
        qualifying,
        round(ca_cost, 2),
        round(imported, 2),
    )
