import { Handle, Position } from '@xyflow/react'
import { actionTypeMeta } from '../../lib/actionTypes.js'
import { anomalyMeta, worstSeverity } from '../../lib/anomalies.js'
import { directCost, formatCAD, formatQty } from '../../lib/format.js'
import SeverityDot from '../SeverityDot.jsx'
import styles from './ProvenanceNode.module.css'

// Type = swatch token + colour-matched label. Health = border + tint. No side-stripe.
export default function ProvenanceNode({ data, selected }) {
  const att = data.attestation
  const meta = actionTypeMeta(att.action_type)
  const anomalies = data.anomalies ?? []
  const severity = worstSeverity(anomalies)
  const isCA = att.performed_in_country === 'CA'
  const cost = directCost(att)

  const worstAnom = severity ? anomalies.find((a) => anomalyMeta(a.type).severity === severity) : null
  const worstMessage = worstAnom ? anomalyMeta(worstAnom.type).message : ''
  const extra = anomalies.length - 1

  const cls = [
    styles.node,
    severity && styles[`sev_${severity}`],
    selected && styles.selected,
    data.highlight && styles.highlight,
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <div className={cls}>
      <Handle type="target" position={Position.Left} className={styles.handle} />

      <div className={styles.header}>
        <span className={styles.swatch} style={{ background: meta.color }} />
        <span className={styles.type} style={{ color: meta.color }}>
          {meta.label}
        </span>
        {data.highlight && <span className={styles.newTag}>New</span>}
        <span className={styles.country}>
          <span className={isCA ? styles.dotFilled : styles.dotHollow} />
          {att.performed_in_country}
        </span>
      </div>

      <div className={styles.title} title={att.output?.name}>
        {att.output?.name}
      </div>

      <div className={`${styles.metaRow} mono tabular`}>
        {formatQty(att.output?.quantity_produced, att.output?.unit)} · {formatCAD(cost)} CAD
      </div>

      {severity && (
        <div className={styles.anomaly}>
          <SeverityDot severity={severity} />
          <span className={styles.anomalyMsg}>
            {worstMessage}
            {extra > 0 ? ` · +${extra}` : ''}
          </span>
        </div>
      )}

      <Handle type="source" position={Position.Right} className={styles.handle} />
    </div>
  )
}
