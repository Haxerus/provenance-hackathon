from dataclasses import dataclass


@dataclass(frozen=True)
class Anomaly:
    type: str
    attestation_id: str
    severity: str
    details: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "type": self.type,
            "attestation_id": self.attestation_id,
            "details": self.details,
        }
