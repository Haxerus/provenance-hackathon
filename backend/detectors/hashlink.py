from backend.core.dag import ChainContext
from backend.core.parsing import get_parents
from backend.detectors.base import Anomaly
from backend.registry import Registry


def detect_hashlink(ctx: ChainContext) -> list[Anomaly]:
    out: list[Anomaly] = []
    for aid, att in ctx.attestations.items():
        for pref in get_parents(att):
            pid = pref.get("attestation_id")
            claimed = pref.get("content_hash")
            if pid in ctx.attestations and claimed is not None:
                actual = ctx.content_hashes.get(str(pid))
                if actual is not None and claimed != actual:
                    out.append(
                        Anomaly(
                            "parent_hash_mismatch",
                            aid,
                            "hard",
                            f"parent {pid} content hash mismatch",
                        )
                    )

    registry = ctx.registry
    if not isinstance(registry, Registry):
        return out

    leaf_anchor = registry.anchor(ctx.product_id)
    expected_product = leaf_anchor["product_id"] if leaf_anchor else None
    for aid in ctx.attestations:
        anchor = registry.anchor(aid)
        if anchor is None:
            continue
        actual = ctx.content_hashes.get(aid)
        if actual is not None and actual != anchor["content_hash"]:
            out.append(Anomaly("anchor_mismatch", aid, "hard", "content differs from anchored record"))
        if expected_product is not None and anchor["product_id"] != expected_product:
            out.append(
                Anomaly(
                    "replay_cross_chain",
                    aid,
                    "hard",
                    f"anchored to product {anchor['product_id']}, not {expected_product}",
                )
            )
    return out
