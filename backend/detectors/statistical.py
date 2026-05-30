from backend.core.computation import TRANSFORM_ACTIONS
from backend.core.dag import ChainContext
from backend.core.parsing import get_costs
from backend.detectors.base import Anomaly
from backend.model.baseline import Baseline


def detect_statistical(ctx: ChainContext) -> list[Anomaly]:
    out: list[Anomaly] = []
    model = ctx.model
    if not isinstance(model, Baseline):
        return out
    thresholds = model.thresholds
    for aid, att in ctx.attestations.items():
        action = att.get("action_type")
        _material, hours, labour = get_costs(att)

        if action in TRANSFORM_ACTIONS and hours > 0:
            rate_z = model.rate_z(str(action), labour / hours)
            if rate_z > thresholds["rate_z_hard"]:
                out.append(Anomaly("cost_anomaly", aid, "hard", f"labour rate z={rate_z:.1f}"))
            elif rate_z > thresholds["rate_z_soft"]:
                out.append(Anomaly("cost_anomaly", aid, "soft", f"labour rate z={rate_z:.1f}"))

            hours_z = model.hours_z(str(action), hours)
            if hours_z > thresholds["hours_z_soft"]:
                out.append(Anomaly("labour_anomaly", aid, "soft", f"labour hours z={hours_z:.1f}"))

        supplier = att.get("supplier_id")
        country = att.get("performed_in_country")
        if supplier and country and not model.is_known_country(str(supplier), str(country)):
            out.append(Anomaly("origin_anomaly", aid, "soft", f"{country} unseen for supplier {supplier}"))

        timestamp = att.get("timestamp") or ""
        time_of_day = timestamp[11:] if len(timestamp) >= 20 else ""
        if time_of_day and not model.is_valid_time(str(action), time_of_day):
            out.append(Anomaly("timing_anomaly", aid, "soft", f"time-of-day {time_of_day} unexpected"))
    return out
