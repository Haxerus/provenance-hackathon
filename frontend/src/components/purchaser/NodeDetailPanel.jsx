import StatusDot from '../StatusDot.jsx'
import SeverityDot from '../SeverityDot.jsx'
import CopyButton from '../CopyButton.jsx'
import { actionTypeMeta } from '../../lib/actionTypes.js'
import { anomalyMeta } from '../../lib/anomalies.js'
import { directCost, formatCAD, formatDate, formatPercent, formatQty, truncateMiddle } from '../../lib/format.js'
import styles from './NodeDetailPanel.module.css'

export default function NodeDetailPanel({ attestation, anomalies = [], totalCost = 0 }) {
  if (!attestation) {
    return (
      <div className={styles.empty}>
        <p className={styles.emptyTitle}>No node selected</p>
        <p className={styles.emptyText}>
          Select a node in the graph, or an anomaly, to inspect its attestation, costs, and signature.
        </p>
      </div>
    )
  }

  const meta = actionTypeMeta(attestation.action_type)
  const invalidSig = anomalies.some((a) => a.type === 'invalid_signature')
  const cost = directCost(attestation)
  const share = totalCost > 0 ? cost / totalCost : 0
  const isCA = attestation.performed_in_country === 'CA'

  return (
    <div className={styles.panel}>
      <header className={styles.header}>
        <div className={styles.typeChip}>
          <span className={styles.swatch} style={{ background: meta.color }} />
          <span className={styles.type} style={{ color: meta.color }}>
            {meta.label}
          </span>
        </div>
        <h2 className={styles.name}>{attestation.output?.name}</h2>
        <StatusDot state={invalidSig ? 'invalid' : 'verified'}>
          {invalidSig ? 'Signature does not verify' : 'Signature verified (ed25519)'}
        </StatusDot>
      </header>

      <Section title="Attestation">
        <Row label="ID">
          <span className="mono">{truncateMiddle(attestation.attestation_id, 16, 6)}</span>
          <CopyButton value={attestation.attestation_id} />
        </Row>
        <Row label="Supplier">
          <span className="mono">{attestation.supplier_id}</span>
        </Row>
        <Row label="Performed in">
          {attestation.performed_in_country}
          {isCA ? ' · Canada' : ''}
        </Row>
        <Row label="Timestamp">{formatDate(attestation.timestamp)}</Row>
      </Section>

      <Section title="Canadian content">
        <div className={styles.bar} role="img" aria-label={`${formatPercent(share * 100)} percent of chain cost`}>
          <span className={styles.barFill} style={{ width: `${Math.min(share * 100, 100)}%` }} />
        </div>
        <p className={styles.caption}>
          <span className="tabular">{formatPercent(share * 100)}%</span> of chain direct cost · performed{' '}
          {isCA ? 'in Canada' : 'abroad'}
        </p>
      </Section>

      <Section title="Output & cost">
        <Row label="Output">{formatQty(attestation.output?.quantity_produced, attestation.output?.unit)}</Row>
        <Row label="Material">
          <span className="tabular">{formatCAD(attestation.costs?.material_cad)}</span>
        </Row>
        <Row label="Labour">
          <span className="tabular">{attestation.costs?.labour_hours ?? 0} h</span> ·{' '}
          <span className="tabular">{formatCAD(attestation.costs?.labour_cost_cad)}</span>
        </Row>
        <Row label="Direct cost">
          <span className="tabular">{formatCAD(cost)}</span>
        </Row>
      </Section>

      {attestation.parents?.length > 0 && (
        <Section title={`Inputs (${attestation.parents.length})`}>
          <ul className={styles.parents}>
            {attestation.parents.map((p) => (
              <li key={p.attestation_id} className={styles.parent}>
                <div className={styles.parentTop}>
                  <span className="mono">{truncateMiddle(p.attestation_id, 16, 6)}</span>
                  <span className={styles.parentQty}>
                    <span className="tabular">{formatQty(p.quantity_consumed, p.unit)}</span>
                  </span>
                </div>
                <div className={styles.parentHash}>
                  <span className="mono">{truncateMiddle(p.content_hash, 10, 8)}</span>
                  {p.tampered && <span className={styles.tamperTag}>tampered</span>}
                  <CopyButton value={p.content_hash} label="Copy hash" />
                </div>
              </li>
            ))}
          </ul>
        </Section>
      )}

      <Section title="Signature">
        <Row label="ed25519">
          <span className="mono">{truncateMiddle(attestation.signature?.value, 12, 8)}</span>
          <CopyButton value={attestation.signature?.value} />
        </Row>
      </Section>

      {anomalies.length > 0 && (
        <Section title="Flags on this node">
          <ul className={styles.flags}>
            {anomalies.map((a, i) => {
              const am = anomalyMeta(a.type)
              return (
                <li key={i} className={styles.flag}>
                  <SeverityDot severity={am.severity} />
                  <div>
                    <p className={styles.flagLabel}>{am.label}</p>
                    {a.details && <p className={styles.flagDetail}>{a.details}</p>}
                  </div>
                </li>
              )
            })}
          </ul>
        </Section>
      )}
    </div>
  )
}

function Section({ title, children }) {
  return (
    <section className={styles.section}>
      <h3 className={styles.sectionTitle}>{title}</h3>
      {children}
    </section>
  )
}

function Row({ label, children }) {
  return (
    <div className={styles.row}>
      <span className={styles.rowLabel}>{label}</span>
      <span className={styles.rowValue}>{children}</span>
    </div>
  )
}
