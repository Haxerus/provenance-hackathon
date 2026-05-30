from backend.core.dag import ChainContext
from backend.core.parsing import get_output, get_parents
from backend.detectors.base import Anomaly


def detect_structural(ctx: ChainContext) -> list[Anomaly]:
    out: list[Anomaly] = []
    seen: set[tuple[str, str]] = set()

    def add(anomaly: Anomaly) -> None:
        key = (anomaly.attestation_id, anomaly.type)
        if key in seen:
            return
        seen.add(key)
        out.append(anomaly)

    for duplicate_id in ctx.duplicate_ids:
        add(
            Anomaly(
                "replay_within_chain",
                duplicate_id,
                "hard",
                "attestation id appears more than once",
            )
        )

    cycle_attributed = False

    for aid, att in ctx.attestations.items():
        timestamp = att.get("timestamp")
        for pref in get_parents(att):
            pid = pref.get("attestation_id")
            if pid not in ctx.attestations:
                add(Anomaly("dangling_parent", aid, "hard", f"parent {pid} not present"))
                continue

            parent = ctx.attestations[str(pid)]
            child_unit = pref.get("unit")
            parent_unit = get_output(parent).get("unit")
            if child_unit is not None and parent_unit is not None and child_unit != parent_unit:
                add(
                    Anomaly(
                        "unit_mismatch",
                        aid,
                        "hard",
                        f"consumes {child_unit}, parent produces {parent_unit}",
                    )
                )

            parent_timestamp = parent.get("timestamp")
            if (
                isinstance(timestamp, str)
                and isinstance(parent_timestamp, str)
                and timestamp < parent_timestamp
            ):
                add(
                    Anomaly(
                        "timestamp_inversion",
                        aid,
                        "hard",
                        f"timestamp {timestamp} precedes parent {parent_timestamp}",
                    )
                )
                if aid in ctx.cycle_nodes and str(pid) in ctx.cycle_nodes:
                    add(
                        Anomaly(
                            "circular_reference",
                            str(pid),
                            "hard",
                            "cycle detected in parent references",
                        )
                    )
                    cycle_attributed = True
    if not cycle_attributed:
        for aid in ctx.cycle_nodes:
            add(Anomaly("circular_reference", aid, "hard", "attestation participates in a cycle"))
    return out
