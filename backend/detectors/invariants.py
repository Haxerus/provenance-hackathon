from backend.core.computation import TRANSFORM_ACTIONS
from backend.core.dag import ChainContext
from backend.core.parsing import get_costs, get_output, get_parents
from backend.detectors.base import Anomaly


def detect_invariants(ctx: ChainContext) -> list[Anomaly]:
    out: list[Anomaly] = []
    for aid, att in ctx.attestations.items():
        action = att.get("action_type")
        material, hours, labour = get_costs(att)
        parents = get_parents(att)

        if action in TRANSFORM_ACTIONS and not parents:
            out.append(Anomaly("transformation_implausible", aid, "hard", "transformation step has no inputs"))

        if action in TRANSFORM_ACTIONS and material > 0:
            out.append(Anomaly("cost_role_violation", aid, "hard", "transformation step carries material cost"))
        if action == "raw_material_supply" and (labour > 0 or hours > 0):
            out.append(Anomaly("cost_role_violation", aid, "hard", "raw material step carries labour"))

        produced = get_output(att).get("quantity_produced")
        bad_value = (
            material < 0
            or labour < 0
            or hours < 0
            or (isinstance(produced, (int, float)) and produced <= 0)
        )
        if bad_value:
            out.append(Anomaly("impossible_value", aid, "hard", "negative cost or non-positive quantity"))

        if any(pref.get("attestation_id") == aid for pref in parents):
            out.append(Anomaly("circular_reference", aid, "hard", "attestation references itself"))
    return out
