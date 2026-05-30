"""Run training_corpus.jsonl through checks.py and compare to expected labels."""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

with open("registry/supplier_public_keys.json") as f:
    PUBLIC_KEYS = json.load(f)["keys"]

with open("registry/anchor_registry.json") as f:
    _reg = json.load(f)
    ANCHOR_REGISTRY = {a["attestation_id"]: a for a in _reg.get("anchors", [])}

from deterministic_checks import run_all_checks

PERCENTAGE_TOLERANCE = 0.5

pass_count = 0
fail_count = 0
total = 0

for line_num, line in enumerate(open("training_corpus.jsonl"), 1):
    line = line.strip()
    if not line:
        continue
    record = json.loads(line)
    chain = record["chain"]
    expected = record["labels"]
    total += 1

    result = run_all_checks(
        product_attestation_id=chain["product_attestation_id"],
        attestations=chain["attestations"],
        public_keys=PUBLIC_KEYS,
        anchor_registry=ANCHOR_REGISTRY,
    )

    # Compare
    issues = []

    pct_diff = abs(result["canadian_content_percentage"] - expected["canadian_content_percentage"])
    if pct_diff > PERCENTAGE_TOLERANCE:
        issues.append(
            f"  percentage: got {result['canadian_content_percentage']:.2f}  "
            f"expected {expected['canadian_content_percentage']:.2f}  "
            f"(diff {pct_diff:.2f})"
        )

    if result["designation"] != expected["designation"]:
        issues.append(
            f"  designation: got '{result['designation']}'  "
            f"expected '{expected['designation']}'"
        )

    if result["chain_valid"] != expected["chain_valid"]:
        issues.append(
            f"  chain_valid: got {result['chain_valid']}  "
            f"expected {expected['chain_valid']}"
        )

    got_types = sorted(a["type"] for a in result["anomalies"])
    exp_types = sorted(a["type"] for a in expected["anomalies"])
    if got_types != exp_types:
        issues.append(
            f"  anomaly types: got {got_types}  expected {exp_types}"
        )
    else:
        # Same types — check attestation_ids match per type
        got_by_type: dict = {}
        for a in result["anomalies"]:
            got_by_type.setdefault(a["type"], []).append(a["attestation_id"])
        exp_by_type: dict = {}
        for a in expected["anomalies"]:
            exp_by_type.setdefault(a["type"], []).append(a["attestation_id"])
        for t in got_by_type:
            g = sorted(got_by_type[t])
            e = sorted(exp_by_type.get(t, []))
            if g != e:
                issues.append(
                    f"  anomaly ids for '{t}': got {g}  expected {e}"
                )

    attack = record["labels"].get("attack", "clean")
    pid = chain["product_attestation_id"]

    if issues:
        fail_count += 1
        print(f"FAIL  line {line_num:3d}  [{attack:35s}]  {pid}")
        for iss in issues:
            print(iss)
    else:
        pass_count += 1
        print(f"PASS  line {line_num:3d}  [{attack:35s}]  {pid}")

print()
print(f"Results: {pass_count}/{total} passed, {fail_count}/{total} failed")
