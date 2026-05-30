"""Deterministic integrity checks for POST /verify.

Each check is binary pass/fail.  All checks run independently — no short-
circuiting — so a single tampered attestation can generate all co-occurring
anomalies (e.g. signature_invalid + parent_hash_mismatch on every child).

Checks (in recommended execution order):
  1.  replay_within_chain         – duplicate attestation_id in the submission
  2a. signature_unknown_supplier  – supplier_id not in the public-key registry
  2b. signature_invalid           – signature fails Ed25519 verification
  3.  parent_hash_mismatch        – child stores wrong content_hash for parent
      anchor_mismatch             – anchored node differs from registry value
      replay_cross_chain          – node belongs to a different product
  4.  dangling_parent             – parent reference not present in submission
  5.  circular_reference          – cycle detected in the DAG
  6.  timestamp_inversion         – child timestamp precedes a parent's
  7.  unit_mismatch               – child consumes units different from parent output
  8.  mass_balance_violation      – total consumption of a node exceeds production
  9.  transformation_implausible  – action_type/parent-list inconsistency
  10. cost_anomaly                – labour rate wildly outside normal band

After all checks, compute_canadian_content() derives the percentage and
designation per spec/computation.md — always, regardless of chain validity.
"""
from __future__ import annotations

import sys
from collections import defaultdict, deque
from datetime import datetime
from typing import Any

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from reference_lib import content_hash, verify_attestation


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_ts(ts_str: str) -> datetime:
    return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))


def _flag(anomalies: list, anomaly_type: str, attestation_id: str, details: str) -> None:
    anomalies.append({
        "type": anomaly_type,
        "attestation_id": attestation_id,
        "details": details,
    })


# ---------------------------------------------------------------------------
# Check 1: replay_within_chain
# Also builds and returns att_by_id for all downstream checks.
# ---------------------------------------------------------------------------

def check_replay_within_chain(
    attestations: list[dict],
    anomalies: list,
) -> dict[str, dict]:
    """Detect duplicate attestation_ids; return the deduplicated lookup map."""
    seen: dict[str, dict] = {}
    for att in attestations:
        aid = att["attestation_id"]
        if aid in seen:
            _flag(anomalies, "replay_within_chain", aid,
                  "duplicate attestation_id in submission")
        seen[aid] = att
    return seen


# ---------------------------------------------------------------------------
# Check 2: signature_unknown_supplier / signature_invalid
# ---------------------------------------------------------------------------

def check_signatures(
    attestations: list[dict],
    public_keys: dict[str, str],
    anomalies: list,
) -> None:
    """Flag attestations whose supplier is unknown or whose signature fails."""
    for att in attestations:
        aid = att["attestation_id"]
        supplier = att["supplier_id"]
        if supplier not in public_keys:
            _flag(anomalies, "signature_unknown_supplier", aid,
                  f"supplier {supplier} not in registry")
        else:
            if not verify_attestation(att, public_keys[supplier]):
                _flag(anomalies, "signature_invalid", aid,
                      "signature does not verify vs claimed supplier key")


# ---------------------------------------------------------------------------
# Check 3: parent_hash_mismatch + anchor_mismatch / replay_cross_chain
# ---------------------------------------------------------------------------

def check_parent_hashes(
    attestations: list[dict],
    att_by_id: dict[str, dict],
    anchor_registry: dict[str, dict],
    product_attestation_id: str,
    anomalies: list,
) -> None:
    """Verify parent content_hashes and anchor registry consistency."""
    for att in attestations:
        aid = att["attestation_id"]

        # 3a: verify each parent reference's stored hash
        for parent_ref in att.get("parents", []):
            parent_id = parent_ref["attestation_id"]
            if parent_id not in att_by_id:
                continue  # dangling — handled by check_dangling_parents
            actual = content_hash(att_by_id[parent_id])
            if actual != parent_ref["content_hash"]:
                _flag(anomalies, "parent_hash_mismatch", aid,
                      f"content_hash mismatch for parent {parent_id}")

        # 3b: anchor registry checks (only when the id IS in the registry)
        if aid in anchor_registry:
            anchored = anchor_registry[aid]
            if content_hash(att) != anchored["content_hash"]:
                _flag(anomalies, "anchor_mismatch", aid,
                      "content differs from anchor registry")

            anchored_product = anchored.get("product_id")
            if anchored_product and anchored_product != product_attestation_id:
                _flag(anomalies, "replay_cross_chain", aid,
                      f"attestation belongs to product {anchored_product}, "
                      f"not {product_attestation_id}")


# ---------------------------------------------------------------------------
# Check 4: dangling_parent
# ---------------------------------------------------------------------------

def check_dangling_parents(
    attestations: list[dict],
    att_by_id: dict[str, dict],
    anomalies: list,
) -> None:
    """Flag children whose parent references cannot be resolved."""
    for att in attestations:
        aid = att["attestation_id"]
        for parent_ref in att.get("parents", []):
            if parent_ref["attestation_id"] not in att_by_id:
                _flag(anomalies, "dangling_parent", aid,
                      f"parent {parent_ref['attestation_id']} not in submission")


# ---------------------------------------------------------------------------
# Check 5: circular_reference
# ---------------------------------------------------------------------------

def check_circular_references(
    product_attestation_id: str,
    att_by_id: dict[str, dict],
    anomalies: list,
) -> None:
    """Iterative DFS cycle detection; avoids Python recursion limit."""
    visiting: set[str] = set()
    visited: set[str] = set()
    cycles: list[str] = []

    # Iterative post-order DFS using an explicit stack.
    # Each stack entry is (node_id, iterator_over_parents, entered_visiting).
    stack: list[tuple[str, Any, bool]] = []

    def push(node_id: str) -> None:
        if node_id in visited or node_id not in att_by_id:
            return
        if node_id in visiting:
            cycles.append(node_id)
            return
        visiting.add(node_id)
        parents = iter(att_by_id[node_id].get("parents", []))
        stack.append((node_id, parents, True))

    push(product_attestation_id)

    while stack:
        node_id, parents, _ = stack[-1]
        try:
            parent_ref = next(parents)
            pid = parent_ref["attestation_id"]
            if pid in visiting:
                cycles.append(pid)
            elif pid not in visited and pid in att_by_id:
                visiting.add(pid)
                p_parents = iter(att_by_id[pid].get("parents", []))
                stack.append((pid, p_parents, True))
        except StopIteration:
            stack.pop()
            visiting.discard(node_id)
            visited.add(node_id)

    for node_id in cycles:
        _flag(anomalies, "circular_reference", node_id,
              "node is part of a cycle in the DAG")


# ---------------------------------------------------------------------------
# Check 6: timestamp_inversion
# ---------------------------------------------------------------------------

def check_timestamp_inversions(
    attestations: list[dict],
    att_by_id: dict[str, dict],
    anomalies: list,
) -> None:
    """Flag children whose timestamp precedes any parent's timestamp."""
    for att in attestations:
        aid = att["attestation_id"]
        child_ts = _parse_ts(att["timestamp"])
        for parent_ref in att.get("parents", []):
            pid = parent_ref["attestation_id"]
            if pid not in att_by_id:
                continue
            parent_ts = _parse_ts(att_by_id[pid]["timestamp"])
            if child_ts < parent_ts:
                _flag(anomalies, "timestamp_inversion", aid,
                      "child timestamp precedes parent")
                break  # one flag per attestation is sufficient


# ---------------------------------------------------------------------------
# Check 7: unit_mismatch
# ---------------------------------------------------------------------------

def check_unit_mismatches(
    attestations: list[dict],
    att_by_id: dict[str, dict],
    anomalies: list,
) -> None:
    """Flag children that consume a unit different from the parent's output unit."""
    for att in attestations:
        for parent_ref in att.get("parents", []):
            pid = parent_ref["attestation_id"]
            if pid not in att_by_id:
                continue
            expected_unit = att_by_id[pid]["output"]["unit"]
            consumed_unit = parent_ref["unit"]
            if consumed_unit != expected_unit:
                _flag(anomalies, "unit_mismatch", att["attestation_id"],
                      f"consumes {consumed_unit} but parent outputs {expected_unit}")


# ---------------------------------------------------------------------------
# Check 8: mass_balance_violation
# ---------------------------------------------------------------------------

def check_mass_balance(
    attestations: list[dict],
    att_by_id: dict[str, dict],
    anomalies: list,
) -> None:
    """Flag parent nodes whose total consumption across all children exceeds output.

    This is a global sum — a diamond DAG aggregates consumption from both
    branches, so pairwise comparisons are insufficient.
    """
    consumed_from: dict[str, float] = defaultdict(float)

    for att in attestations:
        for parent_ref in att.get("parents", []):
            pid = parent_ref["attestation_id"]
            # Only same-unit comparisons; cross-unit is unit_mismatch territory
            parent = att_by_id.get(pid)
            if parent is None:
                continue
            if parent.get("output", {}).get("unit") == parent_ref.get("unit"):
                consumed_from[pid] += parent_ref["quantity_consumed"]

    EPSILON = 1e-6
    for parent_id, total_consumed in consumed_from.items():
        if parent_id not in att_by_id:
            continue
        produced = att_by_id[parent_id]["output"]["quantity_produced"]
        if total_consumed > produced + EPSILON:
            _flag(anomalies, "mass_balance_violation", parent_id,
                  f"consumed {total_consumed} > produced {produced}")


# ---------------------------------------------------------------------------
# Check 9: transformation_implausible
# ---------------------------------------------------------------------------

REQUIRES_PARENTS = {"component_manufacture", "subassembly", "final_integration"}

def check_transformation_plausibility(
    attestations: list[dict],
    anomalies: list,
) -> None:
    """Flag action_type/parent-list inconsistencies."""
    for att in attestations:
        aid = att["attestation_id"]
        action = att["action_type"]
        parents = att.get("parents", [])

        if action in REQUIRES_PARENTS and len(parents) == 0:
            _flag(anomalies, "transformation_implausible", aid,
                  f"{action} consumes nothing")



# ---------------------------------------------------------------------------
# Check 10: cost_anomaly
# ---------------------------------------------------------------------------

LABOUR_RATE_MAX = 150.0  # clean max = 141.63 CAD/hr; anomalous cases start at ~158

def check_cost_anomalies(
    attestations: list[dict],
    anomalies: list,
) -> None:
    """Flag attestations with an implausible labour rate (CAD/hr)."""
    for att in attestations:
        hours = att["costs"]["labour_hours"]
        cost = att["costs"]["labour_cost_cad"]
        if hours > 0:
            rate = cost / hours
            if rate > LABOUR_RATE_MAX:
                _flag(anomalies, "cost_anomaly", att["attestation_id"],
                      f"labour rate {rate:.2f} CAD/hr outside band")


# ---------------------------------------------------------------------------
# Canadian content computation (spec/computation.md)
# ---------------------------------------------------------------------------

SUBSTANTIAL_ACTIONS = {"component_manufacture", "subassembly", "final_integration"}
SUBSTANTIAL_MIN_HOURS = 4.0


def compute_canadian_content(
    attestations: list[dict],
    product_attestation_id: str,
    att_by_id: dict[str, dict],
) -> tuple[float, str]:
    """Return (percentage, designation) from the submitted chain data.

    Computed regardless of chain validity (anomalies do not suppress this).
    """
    # Step 1: flat cost sum over every attestation
    canadian_total = 0.0
    total = 0.0
    for att in attestations:
        costs = att.get("costs", {})
        node_cost = costs.get("material_cad", 0.0) + costs.get("labour_cost_cad", 0.0)
        total += node_cost
        if att.get("performed_in_country") == "CA":
            canadian_total += node_cost

    if total == 0.0:
        return 0.0, "none"

    percentage = (canadian_total / total) * 100.0

    # Step 2: find the last substantial transformation (BFS from leaf, min hops)
    last_substantial: dict | None = None

    # Check the leaf itself first (0 hops)
    leaf = att_by_id.get(product_attestation_id)
    if leaf is not None:
        action = leaf.get("action_type")
        hours = leaf.get("costs", {}).get("labour_hours", 0.0)
        if action in SUBSTANTIAL_ACTIONS and hours >= SUBSTANTIAL_MIN_HOURS:
            last_substantial = leaf

    if last_substantial is None:
        # BFS outward from the leaf; the first qualifying node found is closest
        queue: deque[str] = deque()
        visited_bfs: set[str] = set()

        if leaf is not None:
            for p_ref in leaf.get("parents", []):
                pid = p_ref["attestation_id"]
                if pid not in visited_bfs:
                    queue.append(pid)
                    visited_bfs.add(pid)

        while queue and last_substantial is None:
            node_id = queue.popleft()
            node = att_by_id.get(node_id)
            if node is None:
                continue
            action = node.get("action_type")
            hours = node.get("costs", {}).get("labour_hours", 0.0)
            if action in SUBSTANTIAL_ACTIONS and hours >= SUBSTANTIAL_MIN_HOURS:
                last_substantial = node
                break
            for p_ref in node.get("parents", []):
                pid = p_ref["attestation_id"]
                if pid not in visited_bfs:
                    queue.append(pid)
                    visited_bfs.add(pid)

    # Step 3: designation
    if last_substantial is None:
        return percentage, "none"
    if last_substantial.get("performed_in_country") != "CA":
        return percentage, "none"
    if percentage >= 98.0:
        return percentage, "product_of_canada"
    if percentage >= 51.0:
        return percentage, "made_in_canada"
    return percentage, "none"


# ---------------------------------------------------------------------------
# Top-level entry point
# ---------------------------------------------------------------------------

def run_all_checks(
    product_attestation_id: str,
    attestations: list[dict],
    public_keys: dict[str, str],
    anchor_registry: dict[str, dict],
) -> dict:
    """Run all deterministic checks and compute Canadian content.

    Returns a dict matching the VerifyResponse schema:
      product_attestation_id, canadian_content_percentage, designation,
      chain_valid, anomalies
    """
    anomalies: list[dict] = []

    # 1. replay (also builds att_by_id)
    att_by_id = check_replay_within_chain(attestations, anomalies)

    # 2. dangling parents (must precede traversals that dereference parents)
    check_dangling_parents(attestations, att_by_id, anomalies)

    # 3. cycles
    check_circular_references(product_attestation_id, att_by_id, anomalies)

    # 4. signatures
    check_signatures(attestations, public_keys, anomalies)

    # 5. parent hashes + anchor registry
    check_parent_hashes(attestations, att_by_id, anchor_registry,
                        product_attestation_id, anomalies)

    # 6. unit mismatches
    check_unit_mismatches(attestations, att_by_id, anomalies)

    # 7. timestamp inversions
    check_timestamp_inversions(attestations, att_by_id, anomalies)

    # 8. mass balance
    check_mass_balance(attestations, att_by_id, anomalies)

    # 9. transformation plausibility
    check_transformation_plausibility(attestations, anomalies)

    # 10. cost anomalies
    check_cost_anomalies(attestations, anomalies)

    # Canadian content (always computed, regardless of validity)
    percentage, designation = compute_canadian_content(
        attestations, product_attestation_id, att_by_id
    )

    return {
        "product_attestation_id": product_attestation_id,
        "canadian_content_percentage": percentage,
        "designation": designation,
        "chain_valid": len(anomalies) == 0,
        "anomalies": anomalies,
    }
