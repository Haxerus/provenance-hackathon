import { Field, NumberInput } from '../form/Field.jsx'
import { isTransformation } from '../../lib/actionTypes.js'
import styles from './FieldGrid.module.css'

export default function CostFields({ value, onChange, actionType, errors = {} }) {
  const set = (key) => (e) => onChange({ ...value, [key]: e.target.value })
  const hours = Number(value.labour_hours) || 0
  const transform = isTransformation(actionType)
  const substantialHint =
    transform && hours > 0
      ? hours >= 4
        ? 'Qualifies as a substantial transformation (≥ 4 h).'
        : 'Below 4 h — not a substantial transformation.'
      : 'Labour hours are not a cost; they decide substantial transformation.'

  return (
    <div className={styles.row3}>
      <Field label="Material cost (CAD)" htmlFor="c-mat" hint="Purchased materials" error={errors.material_cad}>
        <NumberInput
          id="c-mat"
          min="0"
          step="any"
          placeholder="0"
          value={value.material_cad}
          onChange={set('material_cad')}
          invalid={!!errors.material_cad}
        />
      </Field>
      <Field label="Labour hours" htmlFor="c-hrs" hint={substantialHint} error={errors.labour_hours}>
        <NumberInput
          id="c-hrs"
          min="0"
          step="any"
          placeholder="0"
          value={value.labour_hours}
          onChange={set('labour_hours')}
          invalid={!!errors.labour_hours}
        />
      </Field>
      <Field label="Labour cost (CAD)" htmlFor="c-lab" hint="Wages for this step" error={errors.labour_cost_cad}>
        <NumberInput
          id="c-lab"
          min="0"
          step="any"
          placeholder="0"
          value={value.labour_cost_cad}
          onChange={set('labour_cost_cad')}
          invalid={!!errors.labour_cost_cad}
        />
      </Field>
    </div>
  )
}
