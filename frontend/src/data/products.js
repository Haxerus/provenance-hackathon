import { CHAINS, ANOMALIES_BY_PRODUCT } from './chains.js'
import { verifyProduct } from './verification.js'

// Product registry. SWAP SEAM: getProduct() / resolveByHash() back onto
// GET /api/products/{id} when the backend is wired in.
export const PRODUCTS = {
  'att-anchor-0012': {
    id: 'att-anchor-0012',
    name: 'Recovery-Capable ISR Drone',
    maker: 'AVSS Corp',
    hash: '7c3f9a1e8b4d2056aa19f0c5e6d7b8a4c2f1903e5d6a7b8c9012d3e4f5a6b7c8',
    code: 'DRONE-12',
  },
  'att-ms-anchor-0012': {
    id: 'att-ms-anchor-0012',
    name: 'MapleShield Sensor Pod',
    maker: 'AVSS Corp',
    hash: 'a1b2c3d4e5f60718293a4b5c6d7e8f90112233445566778899aabbccddeeff00',
    code: 'POD-12',
  },
}

export function listProducts() {
  return Object.values(PRODUCTS)
}

export function getProduct(id) {
  const meta = PRODUCTS[id]
  if (!meta) return null
  return {
    ...meta,
    chain: CHAINS[id],
    anomaliesByAtt: ANOMALIES_BY_PRODUCT[id] ?? {},
    verification: verifyProduct(id),
  }
}

// Resolve a free-text lookup (product id, content hash, or short code) to a product id.
export function resolveByHash(input) {
  const q = String(input || '').trim().toLowerCase()
  if (!q) return null
  for (const p of Object.values(PRODUCTS)) {
    if ([p.id, p.hash, p.code].some((v) => String(v).toLowerCase() === q)) return p.id
  }
  return null
}
