"""Fit statistical detector baseline parameters from clean training data."""

import json
import os
import statistics
from typing import Any

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(ROOT, "training_corpus.jsonl")
OUT = os.path.join(ROOT, "backend", "model", "baseline_stats.json")
TRANSFORMS = {"component_manufacture", "subassembly", "final_integration"}


def mad(values: list[float], median: float) -> float:
    return statistics.median([abs(value - median) for value in values]) or 1e-9


def _costs(att: dict[str, Any]) -> tuple[float, float]:
    costs = att.get("costs") or {}
    return float(costs.get("labour_hours") or 0), float(costs.get("labour_cost_cad") or 0)


def main() -> None:
    hours = {action: [] for action in TRANSFORMS}
    rate = {action: [] for action in TRANSFORMS}
    supplier_country: dict[str, dict[str, int]] = {}
    timing: dict[str, dict[str, int]] = {}

    chains: list[dict[str, Any]] = []
    with open(CORPUS) as corpus:
        for line in corpus:
            row = json.loads(line)
            if row["labels"].get("attack", "clean") == "clean":
                chains.append(row["chain"])
    with open(os.path.join(ROOT, "worked-example", "recovery_drone_chain.json")) as f:
        chains.append(json.load(f))

    for chain in chains:
        for att in chain["attestations"]:
            action = att.get("action_type")
            labour_hours, labour_cost = _costs(att)
            if action in TRANSFORMS and labour_hours > 0:
                hours[action].append(labour_hours)
                rate[action].append(labour_cost / labour_hours)

            supplier = str(att.get("supplier_id"))
            country = str(att.get("performed_in_country"))
            supplier_country.setdefault(supplier, {})
            supplier_country[supplier][country] = supplier_country[supplier].get(country, 0) + 1

            timestamp = att.get("timestamp") or ""
            time_of_day = timestamp[11:] if len(timestamp) >= 20 else ""
            timing.setdefault(str(action), {})
            timing[str(action)][time_of_day] = timing[str(action)].get(time_of_day, 0) + 1

    action_stats: dict[str, dict[str, float]] = {}
    for action in TRANSFORMS:
        hours_median = statistics.median(hours[action])
        rate_median = statistics.median(rate[action])
        action_stats[action] = {
            "hours_median": hours_median,
            "hours_mad": mad(hours[action], hours_median),
            "hours_max": max(hours[action]),
            "rate_median": rate_median,
            "rate_mad": mad(rate[action], rate_median),
            "rate_max": max(rate[action]),
        }

    model = {
        "action_stats": action_stats,
        "supplier_country": supplier_country,
        "timing_whitelist": {action: sorted(times) for action, times in timing.items()},
        "thresholds": {
            "rate_z_hard": 6.0,
            "rate_z_soft": 3.75,
            "hours_z_soft": 3.0,
            "origin_min_count": 1,
        },
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(model, f, indent=2, sort_keys=True)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
