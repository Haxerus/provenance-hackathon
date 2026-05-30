import { Field, TextInput, NumberInput } from '../form/Field.jsx'
import styles from './FieldGrid.module.css'

export default function OutputFields({ value, onChange, errors = {} }) {
  const set = (key) => (e) => onChange({ ...value, [key]: e.target.value })

  return (
    <div className={styles.stack}>
      <Field label="Output name" htmlFor="out-name" error={errors.name}>
        <TextInput
          id="out-name"
          placeholder="e.g. Parachute Recovery Assembly"
          value={value.name}
          onChange={set('name')}
          invalid={!!errors.name}
        />
      </Field>
      <div className={styles.row}>
        <Field label="Quantity produced" htmlFor="out-qty" error={errors.quantity_produced}>
          <NumberInput
            id="out-qty"
            min="0"
            step="any"
            placeholder="1"
            value={value.quantity_produced}
            onChange={set('quantity_produced')}
            invalid={!!errors.quantity_produced}
          />
        </Field>
        <Field label="Unit" htmlFor="out-unit" hint="units · m · m2 · kg · L" error={errors.unit}>
          <TextInput
            id="out-unit"
            placeholder="units"
            value={value.unit}
            onChange={set('unit')}
            invalid={!!errors.unit}
            list="unit-options"
          />
          <datalist id="unit-options">
            <option value="units" />
            <option value="m" />
            <option value="m2" />
            <option value="kg" />
            <option value="L" />
          </datalist>
        </Field>
      </div>
    </div>
  )
}
