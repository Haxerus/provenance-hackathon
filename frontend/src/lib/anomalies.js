// Anomaly + severity metadata. Two encoding channels (DESIGN.md):
// colour (border/tint) AND shape (dot cue + dashed border) so it survives colour-blindness.

export const SEVERITY = {
  critical: { rank: 3, label: 'Critical', border: 'var(--crit-border)', tint: 'var(--crit-tint)', dashed: false },
  warning: { rank: 2, label: 'Warning', border: 'var(--warn-border)', tint: 'var(--warn-tint)', dashed: false },
  subtle: { rank: 1, label: 'Subtle', border: 'var(--subtle-border)', tint: 'var(--subtle-tint)', dashed: true },
}

export const ANOMALY_TYPES = {
  invalid_signature: { severity: 'critical', label: 'Invalid signature', message: 'Signature does not verify' },
  parent_hash_mismatch: { severity: 'critical', label: 'Parent hash mismatch', message: 'Parent hash mismatch' },
  mass_balance_violation: { severity: 'warning', label: 'Mass balance violation', message: 'Over-consumed vs produced' },
  timestamp_anomaly: { severity: 'warning', label: 'Timestamp anomaly', message: 'Timestamp out of expected range' },
  unknown_supplier: { severity: 'warning', label: 'Unknown supplier', message: 'Supplier not in registry' },
  t4_perturbed: { severity: 'subtle', label: 'Statistically anomalous', message: 'Unusual for this kind of step' },
}

function humanize(t) {
  return String(t || 'anomaly')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
}

export function anomalyMeta(type) {
  return ANOMALY_TYPES[type] ?? { severity: 'warning', label: humanize(type), message: humanize(type) }
}

export function severityMeta(severity) {
  return SEVERITY[severity] ?? SEVERITY.warning
}

// Worst severity name across a list of anomaly objects ({ type }). Returns null if empty.
export function worstSeverity(anomalies = []) {
  let worst = null
  for (const a of anomalies) {
    const sev = anomalyMeta(a.type).severity
    if (!worst || SEVERITY[sev].rank > SEVERITY[worst].rank) worst = sev
  }
  return worst
}
