from backend.core.dag import ChainContext
from backend.core.parsing import get_output
from backend.detectors.base import Anomaly

EPSILON = 1e-6


def detect_mass_balance(ctx: ChainContext) -> list[Anomaly]:
    out: list[Anomaly] = []
    for pid, att in ctx.attestations.items():
        produced = get_output(att).get("quantity_produced")
        if not isinstance(produced, (int, float)):
            continue
        total = 0.0
        for _child_id, pref in ctx.children.get(pid, []):
            quantity = pref.get("quantity_consumed")
            if isinstance(quantity, (int, float)):
                total += quantity
        if total > produced + EPSILON:
            out.append(
                Anomaly(
                    "mass_balance_violation",
                    pid,
                    "hard",
                    f"consumed {total}, produced {produced}",
                )
            )
    return out
