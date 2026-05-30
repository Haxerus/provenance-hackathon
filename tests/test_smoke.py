from typing import Any


def test_reference_lib_imports() -> None:
    from reference_lib import canonical_serialize, content_hash, verify_attestation

    assert callable(canonical_serialize)
    assert callable(content_hash)
    assert callable(verify_attestation)


def test_worked_chain_fixture(worked_chain: dict[str, Any]) -> None:
    assert worked_chain["product_attestation_id"] == "att-anchor-0012"
    assert len(worked_chain["attestations"]) == 12
