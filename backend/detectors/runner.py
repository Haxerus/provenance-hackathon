from collections.abc import Callable, Iterable

from backend.core.dag import ChainContext
from backend.core.computation import ComputationResult
from backend.detectors.base import Anomaly

Detector = Callable[[ChainContext], Iterable[Anomaly]]


def run_detectors(ctx: ChainContext, detectors: Iterable[Detector]) -> list[Anomaly]:
    found: list[Anomaly] = []
    seen: set[tuple[str, str]] = set()
    for detector in detectors:
        try:
            results = detector(ctx) or []
        except Exception:
            results = []
        for anomaly in results:
            key = (anomaly.attestation_id, anomaly.type)
            if key not in seen:
                seen.add(key)
                found.append(anomaly)
    return found


def assemble_response(
    ctx: ChainContext,
    comp: ComputationResult,
    anomalies: list[Anomaly],
) -> dict[str, object]:
    return {
        "product_attestation_id": ctx.product_id,
        "canadian_content_percentage": comp.percentage,
        "designation": comp.designation,
        "chain_valid": not any(anomaly.severity == "hard" for anomaly in anomalies),
        "anomalies": [anomaly.to_dict() for anomaly in anomalies],
    }


from backend.detectors.hashlink import detect_hashlink
from backend.detectors.invariants import detect_invariants
from backend.detectors.massbalance import detect_mass_balance
from backend.detectors.signature import detect_signatures
from backend.detectors.statistical import detect_statistical
from backend.detectors.structural import detect_structural

DETERMINISTIC_DETECTORS: list[Detector] = [
    detect_signatures,
    detect_hashlink,
    detect_mass_balance,
    detect_structural,
    detect_invariants,
]

STATISTICAL_DETECTORS: list[Detector] = [
    detect_statistical,
]

DETECTORS: list[Detector] = DETERMINISTIC_DETECTORS + STATISTICAL_DETECTORS
