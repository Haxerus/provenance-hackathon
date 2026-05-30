import recoveryDrone from './recovery_drone.json'

// Deep-clone a base chain and namespace every attestation id with a prefix,
// so we can derive distinct demo products from one realistic DAG.
function cloneChain(base, prefix) {
  const remap = (id) => id.replace(/^att-/, `att-${prefix}-`)
  const attestations = base.attestations.map((a) => ({
    ...structuredClone(a),
    attestation_id: remap(a.attestation_id),
    parents: (a.parents ?? []).map((p) => ({ ...p, attestation_id: remap(p.attestation_id) })),
  }))
  return { product_attestation_id: remap(base.product_attestation_id), attestations }
}

// --- Clean product: the worked example, untouched ---
export const recoveryDroneChain = recoveryDrone

// --- Invalid product: same structure, tampered + forged + anomalous nodes ---
export const mapleShieldChain = cloneChain(recoveryDrone, 'ms')

// Mark the edge from the flight controller into the final integration as tampered
{
  const finalAtt = mapleShieldChain.attestations.find((a) => a.action_type === 'final_integration')
  const ref = finalAtt?.parents.find((p) => p.attestation_id === 'att-ms-anchor-0007')
  if (ref) ref.tampered = true
}

// anomalies keyed by attestation id, per product
export const ANOMALIES_BY_PRODUCT = {
  'att-anchor-0012': {},
  'att-ms-anchor-0012': {
    'att-ms-anchor-0008': [{ type: 'invalid_signature' }],
    'att-ms-anchor-0005': [{ type: 'mass_balance_violation' }],
    'att-ms-anchor-0007': [{ type: 't4_perturbed' }],
    'att-ms-anchor-0012': [{ type: 'parent_hash_mismatch' }],
  },
}

export const CHAINS = {
  'att-anchor-0012': recoveryDroneChain,
  'att-ms-anchor-0012': mapleShieldChain,
}
