from backend.core.computation import compute
from backend.core.dag import build_context
from backend.core.parsing import parse_request
from backend.detectors.base import Anomaly
from backend.detectors.runner import assemble_response, run_detectors


def _ctx(payload: dict[str, object]):
    return build_context(parse_request(payload))


def test_runner_isolates_detector_exceptions() -> None:
    def good(_ctx) -> list[Anomaly]:
        return [Anomaly("x", "att-1", "hard", "")]

    def boom(_ctx) -> list[Anomaly]:
        raise RuntimeError("detector bug")

    ctx = _ctx({"product_attestation_id": "att-1", "attestations": [{"attestation_id": "att-1"}]})
    anomalies = run_detectors(ctx, [good, boom])
    assert [a.attestation_id for a in anomalies] == ["att-1"]


def test_runner_dedups_same_id_and_type() -> None:
    def detector(_ctx) -> list[Anomaly]:
        return [Anomaly("t", "att-1", "hard", "")]

    ctx = _ctx({"product_attestation_id": "att-1", "attestations": [{"attestation_id": "att-1"}]})
    anomalies = run_detectors(ctx, [detector, detector])
    assert len(anomalies) == 1


def test_chain_valid_false_only_for_hard() -> None:
    ctx = _ctx({"product_attestation_id": "att-1", "attestations": [{"attestation_id": "att-1"}]})
    comp = compute(ctx)
    soft = assemble_response(ctx, comp, [Anomaly("t", "att-1", "soft", "")])
    hard = assemble_response(ctx, comp, [Anomaly("t", "att-1", "hard", "")])
    assert soft["chain_valid"] is True
    assert hard["chain_valid"] is False
    assert soft["anomalies"][0]["type"] == "t"
