import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any

from deterministic_checks import run_all_checks

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load static data once at startup — not per request
with open("/project/registry/supplier_public_keys.json") as f:
    SUPPLIER_KEYS: dict = json.load(f)["keys"]

with open("/project/registry/anchor_registry.json") as f:
    _registry = json.load(f)
    # Build lookup: attestation_id -> {content_hash, product_id}
    ANCHOR_REGISTRY: dict = {
        a["attestation_id"]: a for a in _registry.get("anchors", [])
    }


class VerifyRequest(BaseModel):
    product_attestation_id: str
    attestations: list[dict[str, Any]]


class Anomaly(BaseModel):
    type: str
    attestation_id: str
    details: str = ""


class VerifyResponse(BaseModel):
    product_attestation_id: str
    canadian_content_percentage: float
    designation: str
    chain_valid: bool
    anomalies: list[Anomaly]


@app.post("/verify", response_model=VerifyResponse)
def verify(body: VerifyRequest):
    result = run_all_checks(
        product_attestation_id=body.product_attestation_id,
        attestations=body.attestations,
        public_keys=SUPPLIER_KEYS,
        anchor_registry=ANCHOR_REGISTRY,
    )
    return VerifyResponse(**result)


@app.get("/health")
def health():
    return {"status": "ok"}
