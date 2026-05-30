// Hardcoded /verify-shaped results. SWAP SEAM: replace verifyProduct() with a
// POST to /verify (TECHNICAL_GUIDE.md §9) when the backend is wired in.

export const VERIFICATIONS = {
  'att-anchor-0012': {
    product_attestation_id: 'att-anchor-0012',
    canadian_content_percentage: 58.4,
    designation: 'made_in_canada',
    chain_valid: true,
    anomalies: [],
  },
  'att-ms-anchor-0012': {
    product_attestation_id: 'att-ms-anchor-0012',
    canadian_content_percentage: 57.2,
    designation: 'made_in_canada',
    chain_valid: false,
    anomalies: [
      {
        type: 'invalid_signature',
        attestation_id: 'att-ms-anchor-0008',
        details: 'Signature does not verify against the public key registered to sup-sequre.',
      },
      {
        type: 'parent_hash_mismatch',
        attestation_id: 'att-ms-anchor-0012',
        details: 'Declared content_hash for parent att-ms-anchor-0007 does not match its canonical hash.',
      },
      {
        type: 'mass_balance_violation',
        attestation_id: 'att-ms-anchor-0005',
        details: 'Consumes 12 m of suspension line but the parent produced only 12 m across 2 consumers (over-consumed).',
      },
      {
        type: 't4_perturbed',
        attestation_id: 'att-ms-anchor-0007',
        details: 'Flight-controller cost is in-range but unusually low for this kind of step versus genuine chains.',
      },
    ],
  },
}

export function verifyProduct(productId) {
  return VERIFICATIONS[productId] ?? null
}
