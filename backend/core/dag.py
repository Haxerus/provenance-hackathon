from dataclasses import dataclass, field
from typing import Any

from backend.core.canonical import recompute_hash
from backend.core.parsing import ParsedRequest, get_parents


@dataclass
class ChainContext:
    product_id: str
    attestations: dict[str, dict[str, Any]]
    raw_attestations: list[dict[str, Any]]
    order: list[str]
    duplicate_ids: set[str]
    children: dict[str, list[tuple[str, dict[str, Any]]]] = field(default_factory=dict)
    content_hashes: dict[str, str | None] = field(default_factory=dict)
    cycle_nodes: set[str] = field(default_factory=set)
    model: object | None = None
    registry: object | None = None


def _detect_cycles(attestations: dict[str, dict[str, Any]]) -> set[str]:
    white, grey, black = 0, 1, 2
    color = {aid: white for aid in attestations}
    cycle_nodes: set[str] = set()

    def visit(aid: str, stack: list[str]) -> None:
        color[aid] = grey
        stack.append(aid)
        for pref in get_parents(attestations[aid]):
            pid = pref.get("attestation_id")
            if pid not in attestations:
                continue
            if color[pid] == grey:
                cycle_nodes.update(stack[stack.index(pid) :])
            elif color[pid] == white:
                visit(pid, stack)
        stack.pop()
        color[aid] = black

    for aid in attestations:
        if color[aid] == white:
            visit(aid, [])
    return cycle_nodes


def build_context(
    parsed: ParsedRequest,
    model: object | None = None,
    registry: object | None = None,
) -> ChainContext:
    children: dict[str, list[tuple[str, dict[str, Any]]]] = {}
    content_hashes: dict[str, str | None] = {}
    for aid, att in parsed.attestations.items():
        try:
            content_hashes[aid] = recompute_hash(att)
        except Exception:
            content_hashes[aid] = None
        for pref in get_parents(att):
            pid = pref.get("attestation_id")
            if pid is not None:
                children.setdefault(str(pid), []).append((aid, pref))
    return ChainContext(
        product_id=parsed.product_attestation_id,
        attestations=parsed.attestations,
        raw_attestations=parsed.raw_attestations,
        order=parsed.order,
        duplicate_ids=parsed.duplicate_ids,
        children=children,
        content_hashes=content_hashes,
        cycle_nodes=_detect_cycles(parsed.attestations),
        model=model,
        registry=registry,
    )
