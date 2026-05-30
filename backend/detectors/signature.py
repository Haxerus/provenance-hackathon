from backend.core.canonical import verify_attestation
from backend.core.dag import ChainContext
from backend.detectors.base import Anomaly
from backend.registry import Registry


def detect_signatures(ctx: ChainContext) -> list[Anomaly]:
    registry = ctx.registry
    out: list[Anomaly] = []
    if not isinstance(registry, Registry):
        return out
    for aid, att in ctx.attestations.items():
        supplier = att.get("supplier_id")
        pub = registry.public_key(str(supplier) if supplier is not None else None)
        if pub is None:
            out.append(
                Anomaly(
                    "signature_unknown_supplier",
                    aid,
                    "hard",
                    f"supplier {supplier} not in registry",
                )
            )
            continue
        try:
            ok = verify_attestation(att, pub)
        except Exception:
            ok = False
        if not ok:
            out.append(
                Anomaly(
                    "signature_invalid",
                    aid,
                    "hard",
                    "signature does not verify against registered key",
                )
            )
    return out
