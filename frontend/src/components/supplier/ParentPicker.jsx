import { useMemo, useState } from 'react'
import { actionTypeMeta } from '../../lib/actionTypes.js'
import { formatQty } from '../../lib/format.js'
import { NumberInput } from '../form/Field.jsx'
import styles from './ParentPicker.module.css'

function match(o, q) {
  if (!q) return true
  const hay = `${o.output?.name ?? ''} ${o.attestation_id}`.toLowerCase()
  return hay.includes(q.toLowerCase())
}

// Searchable multi-select of upstream attestations. The consume-unit is locked to
// each parent's output.unit (error prevention, DESIGN.md).
export default function ParentPicker({ options = [], value = [], onChange }) {
  const [query, setQuery] = useState('')
  const selectedIds = useMemo(() => new Set(value.map((v) => v.attestation_id)), [value])
  const available = useMemo(
    () => options.filter((o) => !selectedIds.has(o.attestation_id) && match(o, query)),
    [options, selectedIds, query],
  )

  const add = (o) =>
    onChange([
      ...value,
      {
        attestation_id: o.attestation_id,
        name: o.output?.name,
        unit: o.output?.unit,
        available: o.output?.quantity_produced,
        quantity_consumed: '',
      },
    ])
  const remove = (id) => onChange(value.filter((v) => v.attestation_id !== id))
  const setQty = (id, q) =>
    onChange(value.map((v) => (v.attestation_id === id ? { ...v, quantity_consumed: q } : v)))

  return (
    <div className={styles.wrap}>
      {value.length > 0 && (
        <ul className={styles.selected}>
          {value.map((v) => {
            const over = Number(v.quantity_consumed) > Number(v.available)
            return (
              <li key={v.attestation_id} className={styles.selRow}>
                <div className={styles.selInfo}>
                  <span className={styles.selName}>{v.name}</span>
                  <span className={`${styles.selId} mono`}>{v.attestation_id}</span>
                </div>
                <div className={styles.consume}>
                  <NumberInput
                    aria-label={`Quantity consumed of ${v.name}`}
                    min="0"
                    step="any"
                    placeholder="0"
                    value={v.quantity_consumed}
                    onChange={(e) => setQty(v.attestation_id, e.target.value)}
                    className={styles.qty}
                    invalid={over}
                  />
                  <span className={styles.unitLock} title="Unit locked to parent output">
                    {v.unit}
                  </span>
                  <button type="button" className={styles.remove} onClick={() => remove(v.attestation_id)}>
                    Remove
                  </button>
                </div>
                <p className={styles.avail}>
                  {over ? 'Over-consumed — ' : ''}
                  {formatQty(v.available, v.unit)} available
                </p>
              </li>
            )
          })}
        </ul>
      )}

      <input
        className={styles.search}
        type="search"
        placeholder="Search upstream attestations…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        aria-label="Search attestations to add as inputs"
      />

      <ul className={styles.options}>
        {available.length === 0 && <li className={styles.empty}>No matching attestations.</li>}
        {available.map((o) => {
          const m = actionTypeMeta(o.action_type)
          return (
            <li key={o.attestation_id}>
              <button type="button" className={styles.option} onClick={() => add(o)}>
                <span className={styles.swatch} style={{ background: m.color }} />
                <span className={styles.optInfo}>
                  <span className={styles.optName}>{o.output?.name}</span>
                  <span className={styles.optMeta}>
                    {formatQty(o.output?.quantity_produced, o.output?.unit)} ·{' '}
                    <span className="mono">{o.attestation_id}</span>
                  </span>
                </span>
                <span className={styles.add}>Add</span>
              </button>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
