from typing import Any

from pydantic import BaseModel, Field


class VerifyRequest(BaseModel):
    product_attestation_id: str | None = None
    attestations: list[dict[str, Any]] | None = None


class AnomalyOut(BaseModel):
    type: str
    attestation_id: str
    details: str = ""


class VerifyResponse(BaseModel):
    product_attestation_id: str
    canadian_content_percentage: float
    designation: str
    chain_valid: bool
    anomalies: list[AnomalyOut]


class IssueRequest(BaseModel):
    supplier_id: str
    action_type: str
    performed_in_country: str
    output: dict[str, Any]
    costs: dict[str, Any]
    timestamp: str | None = None
    parents: list[dict[str, Any]] = Field(default_factory=list)
    product_id: str | None = None
