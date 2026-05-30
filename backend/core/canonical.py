"""Single import point for the byte-exact canonical core."""

from typing import Any

from reference_lib import (
    canonical_serialize,
    content_hash,
    sign_attestation,
    verify_attestation,
)

__all__ = [
    "canonical_serialize",
    "content_hash",
    "sign_attestation",
    "verify_attestation",
    "recompute_hash",
]


def recompute_hash(attestation: dict[str, Any]) -> str:
    """Return the SHA-256 hex hash of canonical attestation content."""
    return content_hash(attestation)
