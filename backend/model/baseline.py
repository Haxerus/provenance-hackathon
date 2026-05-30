import json
from dataclasses import dataclass

from backend import config


@dataclass
class Baseline:
    action_stats: dict[str, dict[str, float]]
    supplier_country: dict[str, dict[str, int]]
    timing_whitelist: dict[str, list[str]]
    thresholds: dict[str, float]

    def rate_z(self, action: str | None, rate: float) -> float:
        stats = self.action_stats.get(str(action))
        if not stats:
            return 0.0
        return abs(rate - stats["rate_median"]) / (1.4826 * stats["rate_mad"])

    def hours_z(self, action: str | None, hours: float) -> float:
        stats = self.action_stats.get(str(action))
        if not stats:
            return 0.0
        return abs(hours - stats["hours_median"]) / (1.4826 * stats["hours_mad"])

    def is_known_country(self, supplier: str | None, country: str | None) -> bool:
        counts = self.supplier_country.get(str(supplier))
        if not counts:
            return True
        return counts.get(str(country), 0) >= self.thresholds.get("origin_min_count", 1)

    def is_valid_time(self, action: str | None, time_of_day: str) -> bool:
        whitelist = self.timing_whitelist.get(str(action))
        if not whitelist:
            return True
        return time_of_day in whitelist


def load_baseline() -> Baseline:
    with open(config.MODEL_PATH) as f:
        data = json.load(f)
    return Baseline(
        data["action_stats"],
        data["supplier_country"],
        data["timing_whitelist"],
        data["thresholds"],
    )
