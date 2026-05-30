from backend.core.parsing import get_costs, get_parents, node_cost, parse_request


def test_parse_request_basic() -> None:
    payload = {
        "product_attestation_id": "att-1",
        "attestations": [{"attestation_id": "att-1"}, {"attestation_id": "att-2"}],
    }
    parsed = parse_request(payload)
    assert parsed.product_attestation_id == "att-1"
    assert set(parsed.attestations) == {"att-1", "att-2"}
    assert parsed.duplicate_ids == set()
    assert [att["attestation_id"] for att in parsed.raw_attestations] == ["att-1", "att-2"]


def test_parse_request_detects_duplicates() -> None:
    payload = {
        "product_attestation_id": "att-1",
        "attestations": [{"attestation_id": "att-1"}, {"attestation_id": "att-1"}],
    }
    parsed = parse_request(payload)
    assert parsed.duplicate_ids == {"att-1"}


def test_defensive_accessors_tolerate_missing_fields() -> None:
    assert get_costs({}) == (0.0, 0.0, 0.0)
    assert node_cost({"costs": {"material_cad": 5, "labour_cost_cad": 3}}) == 8.0
    assert get_parents({}) == []
