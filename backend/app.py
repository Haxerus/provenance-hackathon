from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import uuid
from typing import Any, cast

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from backend import config
from backend.core.canonical import canonical_serialize, content_hash, sign_attestation
from backend.core.computation import compute
from backend.core.dag import build_context
from backend.core.parsing import parse_request
from backend.model.baseline import Baseline, load_baseline
from backend.registry import Registry, load_registry
from backend.schemas import IssueRequest
from backend.store.base import AttestationStore
from backend.store.memory import InMemoryStore
from backend.store.sqlite import SqliteStore
from backend.verify import verify_chain

STATE: dict[str, object] = {}


def _ensure_state() -> None:
    if "model" not in STATE:
        STATE["model"] = load_baseline()
    if "registry" not in STATE:
        STATE["registry"] = load_registry()
    if "store" not in STATE:
        STATE["store"] = SqliteStore(config.SQLITE_PATH) if config.STORE_BACKEND == "sqlite" else InMemoryStore()


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncIterator[None]:
    _ensure_state()
    yield


app = FastAPI(title="Cryptographic Provenance Verifier", lifespan=_lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _model() -> Baseline:
    _ensure_state()
    return cast(Baseline, STATE["model"])


def _registry() -> Registry:
    _ensure_state()
    return cast(Registry, STATE["registry"])


def _store() -> AttestationStore:
    _ensure_state()
    return cast(AttestationStore, STATE["store"])


@app.get("/health")
def health() -> dict[str, object]:
    _ensure_state()
    return {"status": "ok", "model": "model" in STATE, "registry": "registry" in STATE}


@app.post("/verify")
async def verify(request: Request) -> dict[str, object]:
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    return verify_chain(payload, _model(), _registry())


@app.get("/api/suppliers")
def list_suppliers() -> list[dict[str, object]]:
    registry = _registry()
    return [
        {"supplier_id": supplier_id, "has_private_key": registry.private_key(supplier_id) is not None}
        for supplier_id in registry.public_keys
    ]


@app.post("/api/attestations")
def issue_attestation(req: IssueRequest) -> dict[str, Any]:
    registry = _registry()
    private_key = registry.private_key(req.supplier_id)
    if private_key is None:
        raise HTTPException(status_code=400, detail="no private key for supplier")

    parents: list[dict[str, Any]] = []
    for pref in req.parents:
        pid = pref.get("attestation_id")
        parent = _store().get(str(pid)) if pid else None
        parent_hash = content_hash(parent) if parent else pref.get("content_hash", "")
        parents.append(
            {
                "attestation_id": pid,
                "content_hash": parent_hash,
                "quantity_consumed": pref.get("quantity_consumed", 0),
                "unit": pref.get("unit", ""),
            }
        )

    att: dict[str, Any] = {
        "attestation_id": "att-" + uuid.uuid4().hex[:24],
        "version": "1.0",
        "supplier_id": req.supplier_id,
        "timestamp": req.timestamp or "2026-05-30T09:00:00Z",
        "action_type": req.action_type,
        "performed_in_country": req.performed_in_country,
        "parents": parents,
        "output": req.output,
        "costs": req.costs,
    }
    if req.product_id is not None:
        att["product_id"] = req.product_id
    signed = sign_attestation(att, private_key)
    _store().put(signed)
    return signed


@app.get("/api/attestations")
def list_attestations(
    action_type: str | None = None,
    supplier_id: str | None = None,
    limit: int = 200,
) -> list[dict[str, Any]]:
    return _store().list(action_type=action_type, supplier_id=supplier_id, limit=limit)


@app.get("/api/attestations/{attestation_id}")
def get_attestation(attestation_id: str) -> dict[str, Any]:
    att = _store().get(attestation_id)
    if att is None:
        raise HTTPException(status_code=404, detail="not found")
    return att


@app.get("/api/products")
def list_products() -> list[dict[str, str]]:
    return [product.__dict__ for product in _store().list_products()]


@app.get("/api/products/{product_attestation_id}")
def get_product(product_attestation_id: str) -> dict[str, object]:
    chain = _store().resolve_chain(product_attestation_id)
    if not chain:
        raise HTTPException(status_code=404, detail="not found")
    payload = {"product_attestation_id": product_attestation_id, "attestations": chain}
    verification = verify_chain(payload, _model(), _registry())

    ctx = build_context(parse_request(payload), model=_model(), registry=_registry())
    comp = compute(ctx)
    anomalies_by_id: dict[str, list[dict[str, object]]] = {}
    for anomaly in verification["anomalies"]:
        if isinstance(anomaly, dict):
            anomalies_by_id.setdefault(str(anomaly["attestation_id"]), []).append(anomaly)

    nodes: list[dict[str, object]] = []
    edges: list[dict[str, object]] = []
    for aid, att in ctx.attestations.items():
        costs = att.get("costs") or {}
        nodes.append(
            {
                "attestation_id": aid,
                "name": (att.get("output") or {}).get("name", ""),
                "action_type": att.get("action_type"),
                "performed_in_country": att.get("performed_in_country"),
                "is_canadian": att.get("performed_in_country") == "CA",
                "cost": (costs.get("material_cad") or 0) + (costs.get("labour_cost_cad") or 0),
                "anomalies": anomalies_by_id.get(aid, []),
            }
        )
        for pref in att.get("parents") or []:
            edges.append({"from": pref.get("attestation_id"), "to": aid})

    return {
        "chain": payload,
        "verification": verification,
        "graph": {"nodes": nodes, "edges": edges},
        "designation_detail": {
            "designation": comp.designation,
            "qualifying_statement": comp.qualifying_statement,
            "percentage": comp.percentage,
            "ca_cost": comp.ca_cost,
            "imported_cost": comp.imported_cost,
        },
    }


@app.post("/api/canonicalize")
async def canonicalize(request: Request) -> dict[str, str]:
    att = await request.json()
    canonical = canonical_serialize(att, exclude_signature=True).decode("utf-8")
    return {"canonical": canonical, "content_hash": content_hash(att)}


@app.get("/api/registry/keys")
def registry_keys() -> dict[str, str]:
    return _registry().public_keys


@app.get("/api/registry/anchors/{attestation_id}")
def registry_anchor(attestation_id: str) -> dict[str, str]:
    anchor = _registry().anchor(attestation_id)
    if anchor is None:
        raise HTTPException(status_code=404, detail="not anchored")
    return anchor
