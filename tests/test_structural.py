from typing import Any

from backend.core.dag import build_context
from backend.core.parsing import parse_request
from backend.detectors.structural import detect_structural


def _ctx(payload: dict[str, Any]):
    return build_context(parse_request(payload))


def test_clean_chain_no_flag(worked_chain: dict[str, Any]) -> None:
    assert detect_structural(_ctx(worked_chain)) == []


def test_unit_mismatch() -> None:
    payload = {
        "product_attestation_id": "c",
        "attestations": [
            {"attestation_id": "c", "parents": [{"attestation_id": "p", "unit": "kg"}]},
            {"attestation_id": "p", "parents": [], "output": {"unit": "m2", "quantity_produced": 1}},
        ],
    }
    flagged = {(a.attestation_id, a.type) for a in detect_structural(_ctx(payload))}
    assert ("c", "unit_mismatch") in flagged


def test_dangling_parent() -> None:
    payload = {
        "product_attestation_id": "c",
        "attestations": [{"attestation_id": "c", "parents": [{"attestation_id": "missing"}]}],
    }
    flagged = {(a.attestation_id, a.type) for a in detect_structural(_ctx(payload))}
    assert ("c", "dangling_parent") in flagged


def test_circular_reference() -> None:
    payload = {
        "product_attestation_id": "a",
        "attestations": [
            {"attestation_id": "a", "parents": [{"attestation_id": "b"}]},
            {"attestation_id": "b", "parents": [{"attestation_id": "a"}]},
        ],
    }
    flagged = {(a.attestation_id, a.type) for a in detect_structural(_ctx(payload))}
    assert ("a", "circular_reference") in flagged
    assert ("b", "circular_reference") in flagged


def test_circular_reference_prefers_parent_of_inverted_cycle_edge() -> None:
    payload = {
        "product_attestation_id": "a",
        "attestations": [
            {"attestation_id": "a", "timestamp": "2026-03-01T09:00:00Z", "parents": [{"attestation_id": "b"}]},
            {"attestation_id": "b", "timestamp": "2026-02-01T09:00:00Z", "parents": [{"attestation_id": "c"}]},
            {"attestation_id": "c", "timestamp": "2026-01-01T09:00:00Z", "parents": [{"attestation_id": "a"}]},
        ],
    }
    flagged = {(a.attestation_id, a.type) for a in detect_structural(_ctx(payload))}
    assert ("a", "circular_reference") in flagged
    assert ("b", "circular_reference") not in flagged
    assert ("c", "circular_reference") not in flagged
    assert ("c", "timestamp_inversion") in flagged


def test_timestamp_inversion() -> None:
    payload = {
        "product_attestation_id": "c",
        "attestations": [
            {"attestation_id": "c", "timestamp": "2026-01-01T09:00:00Z", "parents": [{"attestation_id": "p"}]},
            {"attestation_id": "p", "timestamp": "2026-02-01T09:00:00Z", "parents": []},
        ],
    }
    flagged = {(a.attestation_id, a.type) for a in detect_structural(_ctx(payload))}
    assert ("c", "timestamp_inversion") in flagged


def test_replay_within_chain_duplicate_id() -> None:
    payload = {
        "product_attestation_id": "leaf",
        "attestations": [{"attestation_id": "dup", "parents": []}, {"attestation_id": "dup", "parents": []}],
    }
    flagged = {(a.attestation_id, a.type) for a in detect_structural(_ctx(payload))}
    assert ("dup", "replay_within_chain") in flagged
