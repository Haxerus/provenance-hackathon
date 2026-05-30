from typing import Any

from reference_lib import sign_attestation

from backend.core.dag import build_context
from backend.core.parsing import parse_request
from backend.detectors.signature import detect_signatures
from backend.registry import load_registry

REG = load_registry()


def _ctx(payload: dict[str, Any]):
    return build_context(parse_request(payload), registry=REG)


def test_valid_signature_not_flagged(worked_chain: dict[str, Any]) -> None:
    ctx = _ctx(worked_chain)
    assert detect_signatures(ctx) == []


def test_unknown_supplier_flagged() -> None:
    att = {
        "attestation_id": "att-x",
        "supplier_id": "sup-nope",
        "version": "1.0",
        "action_type": "raw_material_supply",
        "performed_in_country": "CA",
        "parents": [],
        "output": {"name": "x", "quantity_produced": 1, "unit": "u"},
        "costs": {"material_cad": 1, "labour_hours": 0, "labour_cost_cad": 0},
    }
    signed = sign_attestation(att, REG.private_key("sup-0001"))
    ctx = _ctx({"product_attestation_id": "att-x", "attestations": [signed]})
    types = {a.type for a in detect_signatures(ctx)}
    assert "signature_unknown_supplier" in types


def test_corrupt_signature_flagged(worked_chain: dict[str, Any]) -> None:
    bad = dict(worked_chain)
    atts = [dict(a) for a in bad["attestations"]]
    atts[0] = dict(atts[0])
    atts[0]["signature"] = {"algorithm": "ed25519", "value": "AAAA"}
    bad["attestations"] = atts
    ctx = _ctx(bad)
    flagged = {(a.attestation_id, a.type) for a in detect_signatures(ctx)}
    assert (atts[0]["attestation_id"], "signature_invalid") in flagged
