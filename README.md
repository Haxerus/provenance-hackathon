# Starter Kit: Cryptographic Provenance Challenge

Everything you need to build your submission. **Read [`CHALLENGE.md`](CHALLENGE.md) first** (what to build, what to submit, how you're judged), then [`TECHNICAL_GUIDE.md`](TECHNICAL_GUIDE.md) for the backend detail.

## Contents

| Path | What it is |
|---|---|
| `CHALLENGE.md` | Deliverables, submission, and judging. Read first. |
| `TECHNICAL_GUIDE.md` | The backend / `POST /verify` technical brief. |
| `spec/` | Full participant specs (attestation schema, computation, anchor registry) for byte-exact reimplementation. |
| `reference_lib/` | Byte-exact canonical serialization + Ed25519 sign/verify. Golden vectors in `reference_lib/tests/`. |
| `registry/supplier_public_keys.json` | `supplier_id` → Ed25519 public key (verify signatures against the claimed supplier). |
| `registry/anchor_registry.json` | Signed public ledger of genuine attestations (id → content hash → product). Not exhaustive; see guide §7. |
| `private_keys/supplier_private_keys.json` | All supplier private keys. Key theft is out of scope (guide §8). |
| `training_corpus.jsonl` | 1,000 labeled chains (clean + attacks) to develop and train against. |
| `self_test.py` | Grade your backend against the training labels, the way the official harness will. |
| `worked-example/` | A full valid recovery-drone chain + its expected verification result. |

## Quick start

```bash
pip install -r requirements.txt                      # backend dependencies
pip install -r reference_lib/requirements.txt        # cryptography
python3 -m reference_lib.tests.test_golden           # confirm byte-exact core

# inspect the worked example
cat worked-example/recovery_drone_chain.json
cat worked-example/recovery_drone_expected.json      # valid, 58.4%, made_in_canada

# once your backend is up (serve /verify on port 8000):
python3 self_test.py http://localhost:8000/verify
```

## Backend

Run the FastAPI verifier with Docker:

```bash
docker compose up --build
```

This serves `POST /verify` on port `8000`.

Development commands:

```bash
python -m pytest -q
python scripts/fit_model.py
```

API surface:

- `POST /verify` - graded stateless verification contract.
- `GET /api/suppliers`, `POST /api/attestations`, `GET /api/attestations`, `GET /api/attestations/{id}` - supplier flow.
- `GET /api/products`, `GET /api/products/{id}` - purchaser lookup with chain, verification, graph, and designation detail.
- `POST /api/canonicalize`, `GET /api/registry/keys`, `GET /api/registry/anchors/{id}`, `GET /health`.
- OpenAPI schema at `/openapi.json`; interactive docs at `/docs`.

## Training data format

Each line of `training_corpus.jsonl`:

```json
{ "chain": { "product_attestation_id": "...", "attestations": [ ... ] },
  "labels": { "canadian_content_percentage": ..., "designation": "...",
              "chain_valid": ..., "anomalies": [ ... ],
              "t4_perturbed": [ "att-..." ], "attack": "..." } }
```

`anomalies` are the integrity violations present (by attestation + a type label).
`t4_perturbed` lists attestations that are *statistically* anomalous though they
break no hard rule; these reward learning the distribution of genuine chains.
`attack` names the family for your convenience (clean chains omit it).
