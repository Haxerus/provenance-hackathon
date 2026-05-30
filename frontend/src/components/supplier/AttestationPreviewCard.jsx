import { actionTypeMeta } from '../../lib/actionTypes.js'
import { formatCAD, formatQty } from '../../lib/format.js'
import styles from './AttestationPreviewCard.module.css'

export default function AttestationPreviewCard({ form }) {
  const m = actionTypeMeta(form.action_type || 'raw_material_supply')
  const cost = (Number(form.costs.material_cad) || 0) + (Number(form.costs.labour_cost_cad) || 0)
  const isCA = form.performed_in_country === 'CA'
  const inputs =
    form.action_type === 'raw_material_supply'
      ? 'None (raw material)'
      : `${form.parents.length} attestation${form.parents.length === 1 ? '' : 's'}`

  return (
    <aside className={styles.card} aria-label="Live attestation preview">
      <span className={styles.kicker}>Live preview</span>

      <div className={styles.node}>
        <div className={styles.header}>
          <span className={styles.swatch} style={{ background: m.color }} />
          <span className={styles.type} style={{ color: m.color }}>
            {m.label}
          </span>
          {form.performed_in_country && (
            <span className={styles.country}>
              <span className={isCA ? styles.dotFilled : styles.dotHollow} />
              {form.performed_in_country}
            </span>
          )}
        </div>
        <div className={styles.title}>{form.output.name || 'Output name'}</div>
        <div className={`${styles.meta} mono tabular`}>
          {formatQty(Number(form.output.quantity_produced) || 0, form.output.unit || 'unit')} ·{' '}
          {formatCAD(cost)} CAD
        </div>
      </div>

      <dl className={styles.facts}>
        <Fact label="Supplier" value={form.supplier_id || '—'} mono />
        <Fact label="Inputs" value={inputs} />
        <Fact label="Labour" value={`${Number(form.costs.labour_hours) || 0} h`} />
      </dl>
    </aside>
  )
}

function Fact({ label, value, mono }) {
  return (
    <div className={styles.fact}>
      <dt className={styles.factLabel}>{label}</dt>
      <dd className={`${styles.factValue} ${mono ? 'mono' : ''}`}>{value}</dd>
    </div>
  )
}
