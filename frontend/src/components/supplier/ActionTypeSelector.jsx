import { RadioGroup } from 'radix-ui'
import { ACTION_TYPE_ORDER, actionTypeMeta } from '../../lib/actionTypes.js'
import styles from './ActionTypeSelector.module.css'

const DESCRIPTIONS = {
  raw_material_supply: 'Source a raw material. No upstream inputs.',
  component_manufacture: 'Build a component from raw inputs.',
  subassembly: 'Combine components into a subassembly.',
  final_integration: 'Integrate inputs into the finished product.',
}

// Swatch token per type (NO side-stripe), accessible via Radix RadioGroup.
export default function ActionTypeSelector({ value, onChange }) {
  return (
    <RadioGroup.Root
      className={styles.grid}
      value={value || ''}
      onValueChange={onChange}
      aria-label="Action type"
    >
      {ACTION_TYPE_ORDER.map((t) => {
        const m = actionTypeMeta(t)
        return (
          <RadioGroup.Item key={t} value={t} className={styles.card}>
            <span className={styles.top}>
              <span className={styles.swatch} style={{ background: m.color }} />
              <span className={styles.label} style={{ color: m.color }}>
                {m.label}
              </span>
            </span>
            <span className={styles.desc}>{DESCRIPTIONS[t]}</span>
          </RadioGroup.Item>
        )
      })}
    </RadioGroup.Root>
  )
}
