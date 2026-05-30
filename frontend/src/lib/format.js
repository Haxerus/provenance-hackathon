export function formatCAD(n) {
  if (n == null || Number.isNaN(Number(n))) return '—'
  return '$' + Number(n).toLocaleString('en-CA', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

export function formatQty(n, unit) {
  if (n == null || Number.isNaN(Number(n))) return '—'
  const v = Number(n).toLocaleString('en-CA', { maximumFractionDigits: 3 })
  return unit ? `${v} ${unit}` : v
}

export function formatPercent(n) {
  if (n == null || Number.isNaN(Number(n))) return '—'
  return Number(n).toLocaleString('en-CA', { minimumFractionDigits: 1, maximumFractionDigits: 1 })
}

export function truncateMiddle(str, head = 10, tail = 6) {
  if (!str) return ''
  if (str.length <= head + tail + 1) return str
  return `${str.slice(0, head)}…${str.slice(-tail)}`
}

// direct cost of one attestation = material_cad + labour_cost_cad (labour_hours is NOT a cost)
export function directCost(att) {
  const c = att?.costs ?? {}
  return (Number(c.material_cad) || 0) + (Number(c.labour_cost_cad) || 0)
}

export function formatDate(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  return d.toLocaleDateString('en-CA', { year: 'numeric', month: 'short', day: 'numeric' })
}
