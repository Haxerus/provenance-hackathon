# Deterministic Checks Specification

**Project:** Cryptographic Provenance for Canadian Supply Chains
**Scope:** Hard-rule integrity checks for `POST /verify`
**Status:** Implementation-ready

---

## Overview

Deterministic checks are binary pass/fail integrity rules defined by the spec. There is no ambiguity: an attestation either violates the rule or it does not. Every team that reads the spec carefully should pass these, so they are table stakes for a competitive harness score. The differentiation comes later in the statistical layer, but the deterministic core must be airtight first because the statistical layer builds on a correctly parsed, correctly validated graph.

### Execution principles

1. **Run every check independently.** Do not short-circuit. A single tampered attestation can produce multiple anomalies (for example `signature_invalid` on the tampered node AND `parent_hash_mismatch` on every child referencing it). The training data is generated so these co-occur, and running checks independently catches all of them for free.
2. **Compute the Canadian content percentage and designation regardless of validity.** Anomalies populate `anomalies[]` and set `chain_valid = false`, but the percentage and designation are always computed from the data present.
3. **One flag per distinct violation.** Over-flagging hurts the F1 score as much as missing a violation. Do not flag the same attestation for the same reason twice.
4. **Use `reference_lib` for all serialization, hashing, and signature verification.** Never roll your own canonical serialization. One byte of difference and every signature and hash check fails.

### Shared setup (run once before all checks)

```python
# Build the lookup map and detect within-chain replay simultaneously
att_by_id = {}
anomalies = []

def flag(anomaly_type, attestation_id, details):
    anomalies.append({
        "type": anomaly_type,
        "attestation_id": attestation_id,
        "details": details,
    })
```

The order of checks below is the recommended execution order. Structural checks (replay, dangling, cycles) come first so later checks can safely assume the graph is traversable.

---

## Check 1: `replay_within_chain`

**What it catches:** The same attestation object appears twice in the submitted `attestations` array.

**How to detect:** Count `attestation_id` occurrences as you build `att_by_id`. If any ID appears more than once, flag the duplicate.

```python
seen = {}
for att in attestations:
    aid = att["attestation_id"]
    if aid in seen:
        flag("replay_within_chain", aid, "duplicate attestation_id in submission")
    seen[aid] = att

att_by_id = seen  # final lookup map
```

**Flag on:** The duplicated `attestation_id`. Flag the id itself, not the first or second copy specifically, since both copies are identical by the nature of the attack.

**Notes:** Build `att_by_id` from this same loop so you only iterate once. Every downstream check relies on `att_by_id`.

---

## Check 2: `signature_unknown_supplier` / `signature_invalid`

**What it catches:** Two sub-cases handled in the same loop.

**2a. Unknown supplier** - `supplier_id` is not in the public key registry. You cannot verify a signature against a key you do not have.

**2b. Signature invalid** - the supplier is known but the signature does not verify against their public key. This single check catches both `signature_corrupt` (garbled signature bytes) and `tamper_no_resign` (content was changed after signing but the old signature was kept).

```python
for att in attestations:
    aid = att["attestation_id"]
    if att["supplier_id"] not in public_keys:
        flag("signature_unknown_supplier", aid,
             f"supplier {att['supplier_id']} not in registry")
    else:
        pubkey = public_keys[att["supplier_id"]]
        if not verify_attestation(att, pubkey):  # from reference_lib
            flag("signature_invalid", aid,
                 "signature does not verify vs claimed supplier key")
```

**Flag on:** The attestation whose signature fails.

**Key detail:** `tamper_no_resign` produces **two** anomalies in the training data: the `signature_invalid` on the tampered attestation, AND a `parent_hash_mismatch` on every child that references it (since the content changed, the stored hash no longer matches). You get both for free if you run all checks independently. Do not try to "explain away" the second flag as redundant; the harness expects both.

**`verify_attestation` contract:** Use the reference library. It canonically serializes the attestation excluding the `signature` field, then verifies the Ed25519 signature in `signature.value` against the provided public key. Returns `True`/`False`.

---

## Check 3: `parent_hash_mismatch`

**What it catches:** A child attestation stores a `content_hash` for its parent, but that hash does not match the parent's actual content. This catches tampering even if the child's own signature has not been invalidated, and even if the parent's signature check is handled separately.

**How to detect:** For each attestation, for each entry in `parents[]`, recompute the parent's content hash and compare.

```python
for att in attestations:
    aid = att["attestation_id"]
    for parent_ref in att.get("parents", []):
        parent_id = parent_ref["attestation_id"]
        if parent_id not in att_by_id:
            continue  # handled by dangling_parent check
        actual_hash = content_hash(att_by_id[parent_id])  # from reference_lib
        if actual_hash != parent_ref["content_hash"]:
            flag("parent_hash_mismatch", aid,
                 f"content_hash mismatch for parent {parent_id}")
```

**Flag on:** The child attestation (the one whose `parents[]` entry has the wrong hash), not the parent.

**`content_hash` contract:** Use the reference library. It computes SHA-256 (lowercase hex) of the parent attestation's canonical serialization, excluding the parent's `signature` field. This is the same hash the spec defines for `parents[].content_hash`.

### Anchor registry bonus (Check 3 extension)

For any attestation whose `attestation_id` appears in the anchor registry, also verify its content hash matches the anchored value. This catches tampering on anchored nodes even when no child references them.

```python
if aid in anchor_registry:
    anchored_hash = anchor_registry[aid]["content_hash"]
    if content_hash(att) != anchored_hash:
        flag("anchor_mismatch", aid, "content differs from anchor registry")

    # Cross-product reuse: anchor says product X, submitted under product Y
    anchored_product = anchor_registry[aid]["product_id"]
    if anchored_product != product_attestation_id:
        flag("replay_cross_chain", aid,
             f"attestation belongs to product {anchored_product}, "
             f"not {product_attestation_id}")
```

**Critical reminder on the anchor registry:** It is **not exhaustive**. Absence from the registry is NOT a violation. A clean, unanchored chain must verify as valid. Only flag when the id IS present in the registry AND something mismatches.

---

## Check 4: `dangling_parent`

**What it catches:** A `parents[]` entry references an `attestation_id` that is not present in the submitted `attestations` array. The chain is broken; you cannot verify the missing link.

```python
for att in attestations:
    aid = att["attestation_id"]
    for parent_ref in att.get("parents", []):
        if parent_ref["attestation_id"] not in att_by_id:
            flag("dangling_parent", aid,
                 f"parent {parent_ref['attestation_id']} not in submission")
```

**Flag on:** The child that has the unresolvable parent reference.

**Notes:** This check must run before any traversal that dereferences parents, or those traversals must defensively skip missing parents (as Checks 3, 6, 7, 8 do with `if parent_id not in att_by_id: continue`).

---

## Check 5: `circular_reference`

**What it catches:** A cycle in the DAG. Some attestation is its own ancestor, which is physically impossible (a component cannot be built from itself).

**How to detect:** DFS from the product leaf. Track the current path (recursion stack). If you revisit a node that is already in the current path, you have a cycle.

```python
def detect_cycles(start_id, att_by_id):
    visiting = set()
    visited = set()
    cycles = []

    def dfs(node_id):
        if node_id in visiting:
            cycles.append(node_id)
            return
        if node_id in visited or node_id not in att_by_id:
            return
        visiting.add(node_id)
        for p in att_by_id[node_id].get("parents", []):
            dfs(p["attestation_id"])
        visiting.remove(node_id)
        visited.add(node_id)

    dfs(start_id)
    return cycles

for node_id in detect_cycles(product_attestation_id, att_by_id):
    flag("circular_reference", node_id, "node is part of a cycle in the DAG")
```

**Flag on:** The node where the cycle is detected.

**Training data note:** `circular_reference` always co-occurs with `parent_hash_mismatch` and `timestamp_inversion` in the training set; the generator creates them together. You will naturally catch all three if you run every check independently. Do not suppress any of them.

**Implementation caution:** Python's default recursion limit is 1000. If chains can be deep, convert the DFS to an iterative stack-based traversal to avoid a `RecursionError`. Test against the deepest training chain.

---

## Check 6: `timestamp_inversion`

**What it catches:** A child attestation has an earlier timestamp than one of its parents. A product assembled before its components were made is physically impossible.

```python
from datetime import datetime

def parse_ts(ts_str):
    return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))

for att in attestations:
    child_ts = parse_ts(att["timestamp"])
    for parent_ref in att.get("parents", []):
        pid = parent_ref["attestation_id"]
        if pid not in att_by_id:
            continue  # dangling, skip
        parent_ts = parse_ts(att_by_id[pid]["timestamp"])
        if child_ts < parent_ts:
            flag("timestamp_inversion", att["attestation_id"],
                 "child timestamp precedes parent")
            break  # one flag per attestation is enough
```

**Flag on:** The child (the one with the earlier timestamp).

**Training data note:** The anomalous attestation always carries a timestamp of `2020-01-01T00:00:00Z`, a very obvious backdating. This is a strong, clean signal in the training set, but do not hardcode that exact value, since the held-out set may use other backdated timestamps. The comparison logic is the robust approach.

**The `break`:** Once any parent is later than the child, the attestation is flagged. Checking remaining parents would only produce duplicate flags for the same node.

---

## Check 7: `unit_mismatch`

**What it catches:** A child's `parents[].unit` does not match its parent's `output.unit`. You cannot consume meters if the parent produced kilograms.

```python
for att in attestations:
    for parent_ref in att.get("parents", []):
        pid = parent_ref["attestation_id"]
        if pid not in att_by_id:
            continue
        expected_unit = att_by_id[pid]["output"]["unit"]
        consumed_unit = parent_ref["unit"]
        if consumed_unit != expected_unit:
            flag("unit_mismatch", att["attestation_id"],
                 f"consumes {consumed_unit} but parent outputs {expected_unit}")
```

**Flag on:** The child attestation.

**Relationship to mass balance:** Cross-unit parent references are caught here as `unit_mismatch`, NOT as `mass_balance_violation`. The mass-balance check only compares quantities when the units already match (see Check 8). Keep these two concerns separate.

---

## Check 8: `mass_balance_violation`

**What it catches:** The total quantity consumed from a parent node (across ALL its children, summed globally over the entire chain) exceeds what that parent produced.

**Critical:** This is a **global sum**, not a pairwise comparison. In a diamond DAG where two branches both consume from the same parent, you sum both consumptions. Implementations that check edges pairwise or per-immediate-subtree will miss violations where consumption of a shared node aggregates across distant branches.

```python
from collections import defaultdict

consumed_from = defaultdict(float)  # parent_id -> total consumed

for att in attestations:
    for parent_ref in att.get("parents", []):
        pid = parent_ref["attestation_id"]
        # Only count consumption when units match; cross-unit is unit_mismatch
        if att_by_id.get(pid, {}).get("output", {}).get("unit") == parent_ref.get("unit"):
            consumed_from[pid] += parent_ref["quantity_consumed"]

EPSILON = 1e-6
for parent_id, total_consumed in consumed_from.items():
    if parent_id not in att_by_id:
        continue
    produced = att_by_id[parent_id]["output"]["quantity_produced"]
    if total_consumed > produced + EPSILON:
        flag("mass_balance_violation", parent_id,
             f"consumed {total_consumed} > produced {produced}")
```

**Flag on:** The parent (the over-consumed node), NOT the consuming children. In multi-consumer cases no single child is individually illegal, so the violation is a property of the parent's budget.

**Over-consumption only:** Only flag when consumed `>` produced. Under-consumption (scrap, leftover, partial-lot use) is legitimate and must NOT be flagged. The `EPSILON = 1e-6` is for float-accumulation safety only, not a waste or yield allowance.

---

## Check 9: `transformation_implausible`

**What it catches:** Action types that require parents but have none. `component_manufacture`, `subassembly`, and `final_integration` all require consuming inputs. The training data shows the "consumes nothing" variant: an attestation of one of these types with no parents.

```python
REQUIRES_PARENTS = {"component_manufacture", "subassembly", "final_integration"}

for att in attestations:
    if att["action_type"] in REQUIRES_PARENTS and len(att.get("parents", [])) == 0:
        flag("transformation_implausible", att["attestation_id"],
             f"{att['action_type']} consumes nothing")
```

**Flag on:** The attestation with the missing inputs.

**Also worth checking (defensive):** A `raw_material_supply` that HAS parents. The spec says it should have none. This does not appear in the training data but is logically inconsistent and may show up in the held-out set.

```python
    if att["action_type"] == "raw_material_supply" and len(att.get("parents", [])) > 0:
        flag("transformation_implausible", att["attestation_id"],
             "raw_material_supply should consume nothing but has parents")
```

---

## Check 10: `cost_anomaly`

**What it catches:** The labour rate (CAD/hour) is wildly outside the normal band. All 15 training examples involve exactly 1000.0 CAD/hr. The normal range in clean chains is 40-142 CAD/hr (P99 = 124.8).

```python
LABOUR_RATE_MAX = 150.0  # clean max = 141.63 CAD/hr; anomalous cases start at ~158

for att in attestations:
    hours = att["costs"]["labour_hours"]
    cost = att["costs"]["labour_cost_cad"]
    if hours > 0:
        rate = cost / hours
        if rate > LABOUR_RATE_MAX:
            flag("cost_anomaly", att["attestation_id"],
                 f"labour rate {rate} CAD/hr outside band")
```

**Flag on:** The attestation with the implausible rate.

**Threshold choice:** The clean P99 is ~125 CAD/hr and all anomalous training cases are exactly 1000 CAD/hr. Setting the threshold at 200 gives a wide safety margin with zero false positives in the training set.

**Note on classification:** This sits at the boundary between deterministic and statistical. It is implemented here as a hard threshold because the training signal is so clean and separable (clean max ~142 vs anomalous 1000). If the held-out set introduces rates between 142 and 1000, revisit this as part of the statistical layer with a proper Z-score. For now, keep it simple and deterministic.

---

## Implementation order and integration

Run the checks in this order so structural integrity is established before deeper traversals:

1. `replay_within_chain` (also builds `att_by_id`)
2. `dangling_parent`
3. `circular_reference`
4. `signature_unknown_supplier` / `signature_invalid`
5. `parent_hash_mismatch` (+ anchor registry: `anchor_mismatch`, `replay_cross_chain`)
6. `unit_mismatch`
7. `timestamp_inversion`
8. `mass_balance_violation`
9. `transformation_implausible`
10. `cost_anomaly`

### Setting `chain_valid`

```python
chain_valid = len(anomalies) == 0
```

### Full response assembly

```python
response = {
    "product_attestation_id": product_attestation_id,
    "canadian_content_percentage": percentage,   # computed separately, always
    "designation": designation,                  # computed separately, always
    "chain_valid": chain_valid,
    "anomalies": anomalies,
}
```

---

## Testing checklist

Before moving to the statistical layer, confirm against the training corpus:

- [ ] `python3 -m reference_lib.tests.test_golden` passes (serialization is byte-exact)
- [ ] The worked example resolves to 58.4%, `made_in_canada`, valid, no anomalies
- [ ] Each deterministic anomaly family in `training_corpus.jsonl` is caught
- [ ] Co-occurring anomalies (tamper, cycle) all fire, none suppressed
- [ ] Clean unanchored chains return `chain_valid = true` with empty `anomalies`
- [ ] No false positives on clean chains (precision check via `self_test.py`)
- [ ] Mass balance catches diamond-DAG over-consumption (not just pairwise)
- [ ] Deep chains do not hit the recursion limit

### Anomaly type label reference

These are the labels used across the deterministic checks. The `type` field is free-form, but matching a recognizable label earns a classification bonus from the harness.

| Label | Check | Flagged node |
|---|---|---|
| `replay_within_chain` | 1 | duplicated id |
| `signature_unknown_supplier` | 2a | offending attestation |
| `signature_invalid` | 2b | offending attestation |
| `parent_hash_mismatch` | 3 | child |
| `anchor_mismatch` | 3 ext | offending attestation |
| `replay_cross_chain` | 3 ext | offending attestation |
| `dangling_parent` | 4 | child |
| `circular_reference` | 5 | node in cycle |
| `timestamp_inversion` | 6 | child |
| `unit_mismatch` | 7 | child |
| `mass_balance_violation` | 8 | parent (over-consumed) |
| `transformation_implausible` | 9 | offending attestation |
| `cost_anomaly` | 10 | offending attestation |
