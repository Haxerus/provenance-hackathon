# FAQ: Common Technical Issues

Quick answers to the problems teams hit most. See `TECHNICAL_GUIDE.md` for the full spec.

## Signatures & hashing

**My signatures won't verify, even on the provided worked example.**
99% of the time this is a **canonical serialization** bug. Signatures are computed over a
byte-exact JSON form, so any difference changes the bytes. Check, in order:
- You **exclude the `signature` field** before verifying/hashing.
- **Number formatting:** whole numbers are integers (`1`, not `1.0`); non-whole have no
  trailing zeros (`520.5`, not `520.50`). This is the most common mistake.
- **Keys sorted** at every nesting level; **no whitespace**; UTF-8.
- You verify against the public key registered to the attestation's **`supplier_id`**, not
  some other key.

If you use Python, call `reference_lib`; it's byte-exact. If you reimplement in
another language, make your output match the **golden vectors** in
`reference_lib/tests/test_golden.py` exactly before anything else.

**`content_hash` never matches / I get `parent_hash_mismatch` on a clean chain.**
`content_hash` is `SHA-256` (lowercase hex) of the parent's **canonical form with the
`signature` excluded**, the same bytes you'd sign. Recompute it the same way the signature
is computed.

**Do I need to verify the anchor registry's signature?**
Optional. It's signed by the event authority key included in the registry file; you may
verify it, but you don't have to.

## The `/verify` contract

**What exactly does my service receive and return?**
See `TECHNICAL_GUIDE.md` §9. Request: `{product_attestation_id, attestations:[...]}`.
Response: `{product_attestation_id, canadian_content_percentage, designation, chain_valid,
anomalies:[...]}`. `designation` must be exactly one of `product_of_canada`,
`made_in_canada`, `none`.

**The attestations seem out of order.**
Array order is **unspecified**; sometimes a child appears before its parent. Build the DAG
from each attestation's `parents` references; never assume topological or sorted order.

**What port?** Serve `POST /verify` on **8000**, brought up by `docker compose up`.

**Does each request contain the whole chain?** Yes: the leaf product plus all ancestors
are in one request. There's no statefulness required across requests.

## Computation gotchas

**My percentage is off by a bit.**
- Use `material_cad + labour_cost_cad` per attestation. **`labour_hours` is NOT a cost** and
  does not enter the percentage.
- Attribute by **`performed_in_country`** on each attestation, *not* the supplier's
  `registered_country` (they can differ).
- It's a flat sum over all attestations, not a recursive/weighted propagation.

**My designation is wrong even though the percentage is right.**
Designation also requires a **substantial transformation performed in Canada**. A node
qualifies only if its `action_type` is a transformation (`component_manufacture`,
`subassembly`, `final_integration`) **and** `labour_hours >= 4`. The relevant one is the
*last* substantial transformation (closest to the product). If it's not in CA, or none
exists, designation is `none` regardless of percentage. Thresholds are inclusive: 51 →
made_in_canada, 98 → product_of_canada.

**Mass-balance false positives / misses.**
Sum **all** consumers of a node across the whole DAG and compare to its
`output.quantity_produced`. Don't check one parent-child edge at a time. Only
**over-consumption** (consumed > produced) is a violation; under-consumption (leftover) is
legitimate. Consumption must be in the parent's `output.unit`.

**Zero-cost chains.** If total chain cost is 0, treat as `insufficient_data` → `none`.

## Anomalies & detection

**The spec doesn't list all the anomaly types.**
That's intentional. `anomalies[].type` is a free-form label, and the examples are not
exhaustive. Part of the challenge is identifying attacks the spec doesn't name. You get credit for
flagging the **right attestation**; a matching `type` label is a bonus. When unsure of the
type, still flag the attestation.

**Every signature is valid but the chain is clearly fake. Is that expected?**
Yes. All supplier private keys ship with the kit, so a sophisticated attacker can sign
anything. Valid signatures are necessary but **not sufficient**; robust detection
checks whether a chain is internally consistent and plausible.

**Some bad chains break no rule I can find.**
Those are the statistical cases: legal on every individual rule but anomalous relative to
how genuine chains look (e.g. a cost or timing that's in-range but unusual *for that kind of
step*). The training corpus labels these under `t4_perturbed`. Learn the distribution of
genuine chains from the data; you won't catch them all with hard rules. A correct rules
implementation scores well; modeling these is what reaches the top.

**Flagging everything to be safe.** Don't. Anomaly detection is scored by F1, so flagging
clean attestations tanks your precision and your score.

## Self-test & scoring

**How do I know how I'm doing?**
Run `python3 self_test.py http://localhost:8000/verify` to grade against the labeled
training corpus, the same way the official harness grades you on the held-out set. The
held-out set is unseen and a bit harder, so expect your official score to be a touch lower.

**My self-test score is low.** Check, in order: signatures verifying (canonical form),
percentage/designation on the **clean** cases, then anomaly precision (are you over-flagging
clean chains?).

## Environment / submission

**`reference_lib` import fails.** `pip install -r reference_lib/requirements.txt`
(it needs the `cryptography` package). Python 3.8+.

**Submission.** Your repo must come up with `docker compose up` and serve `/verify` on 8000.
Include a short README. Keep `/verify` fast; the harness sends hundreds of
chains, so avoid reloading models or keys on every request. A crash, timeout, or malformed
response scores 0 for that case only; the harness continues.
