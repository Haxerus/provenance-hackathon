// Pure layered DAG layout for the provenance graph.
// Raw materials on the left -> final product on the right (left-to-right flow).

export const NODE_W = 224
export const NODE_H = 104
const COL_GAP = 96
const ROW_GAP = 28

export function layoutChain(chain, { anomaliesByAtt = {}, productId, highlightId } = {}) {
  const atts = chain?.attestations ?? []
  const byId = new Map(atts.map((a) => [a.attestation_id, a]))

  // longest-path depth from a root (no in-registry parents)
  const depthCache = new Map()
  function depth(id, seen = new Set()) {
    if (depthCache.has(id)) return depthCache.get(id)
    if (seen.has(id)) return 0
    seen.add(id)
    const parents = (byId.get(id)?.parents ?? []).filter((p) => byId.has(p.attestation_id))
    const d = parents.length ? 1 + Math.max(...parents.map((p) => depth(p.attestation_id, seen))) : 0
    depthCache.set(id, d)
    return d
  }
  atts.forEach((a) => depth(a.attestation_id))

  // group ids by depth (column)
  const cols = new Map()
  atts.forEach((a) => {
    const d = depthCache.get(a.attestation_id)
    if (!cols.has(d)) cols.set(d, [])
    cols.get(d).push(a.attestation_id)
  })

  // order each column by barycenter of parent rows (reduces edge crossings)
  const rowIndex = new Map()
  const bary = (id) => {
    const parents = (byId.get(id)?.parents ?? []).filter((p) => rowIndex.has(p.attestation_id))
    if (!parents.length) return Number.MAX_SAFE_INTEGER // keep unparented in stable input order
    return parents.reduce((s, p) => s + rowIndex.get(p.attestation_id), 0) / parents.length
  }
  ;[...cols.keys()]
    .sort((a, b) => a - b)
    .forEach((d) => {
      const ids = cols.get(d)
      ids
        .map((id, i) => ({ id, i }))
        .sort((x, y) => bary(x.id) - bary(y.id) || x.i - y.i)
        .forEach((entry, i) => rowIndex.set(entry.id, i))
    })

  const totalH = Math.max(...[...cols.values()].map((c) => c.length), 1) * (NODE_H + ROW_GAP)

  const nodes = atts.map((a) => {
    const d = depthCache.get(a.attestation_id)
    const colCount = cols.get(d).length
    const i = rowIndex.get(a.attestation_id)
    const colH = colCount * (NODE_H + ROW_GAP)
    const yStart = (totalH - colH) / 2
    return {
      id: a.attestation_id,
      type: 'provenance',
      position: { x: d * (NODE_W + COL_GAP), y: yStart + i * (NODE_H + ROW_GAP) },
      data: {
        attestation: a,
        anomalies: anomaliesByAtt[a.attestation_id] ?? [],
        isProduct: a.attestation_id === productId,
        highlight: a.attestation_id === highlightId,
      },
    }
  })

  const edges = []
  atts.forEach((a) => {
    ;(a.parents ?? []).forEach((p) => {
      if (!byId.has(p.attestation_id)) return
      const childAnoms = anomaliesByAtt[a.attestation_id] ?? []
      const tampered = p.tampered === true || childAnoms.some((an) => an.type === 'parent_hash_mismatch')
      edges.push({
        id: `${p.attestation_id}__${a.attestation_id}`,
        source: p.attestation_id,
        target: a.attestation_id,
        data: { tampered },
      })
    })
  })

  return { nodes, edges }
}
