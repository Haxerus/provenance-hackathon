import { useMemo, useState } from 'react'
import { Progress } from 'radix-ui'

import ActionTypeSelector from './ActionTypeSelector.jsx'
import ParentPicker from './ParentPicker.jsx'
import OutputFields from './OutputFields.jsx'
import CostFields from './CostFields.jsx'
import CountrySelect from './CountrySelect.jsx'
import AttestationPreviewCard from './AttestationPreviewCard.jsx'
import { Field, TextInput } from '../form/Field.jsx'
import styles from './AttestationForm.module.css'

const EMPTY = {
  action_type: '',
  supplier_id: 'sup-avss-corp',
  performed_in_country: '',
  parents: [],
  output: { name: '', quantity_produced: '', unit: 'units' },
  costs: { material_cad: '', labour_hours: '', labour_cost_cad: '' },
}

function genHash(seed) {
  let h = 2166136261 >>> 0
  const s = String(seed) + Date.now()
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i)
    h = Math.imul(h, 16777619)
  }
  let out = ''
  for (let i = 0; i < 8; i++) {
    h ^= h << 13
    h >>>= 0
    h ^= h >> 17
    h ^= h << 5
    h >>>= 0
    out += h.toString(16).padStart(8, '0')
  }
  return out.slice(0, 64)
}

export default function AttestationForm({ options = [], onSubmit }) {
  const [form, setForm] = useState(EMPTY)
  const [stepIdx, setStepIdx] = useState(0)
  const [showErrors, setShowErrors] = useState(false)

  const isRaw = form.action_type === 'raw_material_supply'

  const steps = useMemo(() => {
    const all = [
      { id: 'type', title: 'Action type', desc: 'What kind of contribution is this?' },
      { id: 'inputs', title: 'Inputs', desc: 'Which upstream attestations does this consume?', skip: isRaw },
      { id: 'output', title: 'Output', desc: 'What does this step produce?' },
      { id: 'costs', title: 'Costs', desc: 'Materials and labour for this step.' },
      { id: 'location', title: 'Location & review', desc: 'Where it happened, then sign.' },
    ]
    return all.filter((s) => !s.skip)
  }, [isRaw])

  const step = steps[Math.min(stepIdx, steps.length - 1)]

  function errorsFor(id) {
    const e = {}
    if (id === 'type' && !form.action_type) e.action_type = 'Choose an action type.'
    if (id === 'output') {
      if (!form.output.name.trim()) e.name = 'Name is required.'
      if (!(Number(form.output.quantity_produced) > 0)) e.quantity_produced = 'Must be greater than 0.'
      if (!form.output.unit.trim()) e.unit = 'Unit is required.'
    }
    if (id === 'location') {
      if (!form.performed_in_country) e.performed_in_country = 'Select where this step happened.'
      if (!form.supplier_id.trim()) e.supplier_id = 'Supplier id is required.'
    }
    return e
  }

  // inputs step is valid when at least one parent is chosen with a positive quantity
  const inputsValid =
    isRaw || (form.parents.length > 0 && form.parents.every((p) => Number(p.quantity_consumed) > 0))

  function stepValid(id) {
    if (id === 'inputs') return inputsValid
    return Object.keys(errorsFor(id)).length === 0
  }

  const overConsumed = form.parents.filter((p) => Number(p.quantity_consumed) > Number(p.available))

  const isLast = stepIdx === steps.length - 1
  const currentErrors = showErrors ? errorsFor(step.id) : {}

  function goNext() {
    if (!stepValid(step.id)) {
      setShowErrors(true)
      return
    }
    setShowErrors(false)
    if (isLast) return submit()
    setStepIdx((i) => Math.min(i + 1, steps.length - 1))
  }
  function goBack() {
    setShowErrors(false)
    setStepIdx((i) => Math.max(i - 1, 0))
  }
  function jumpTo(i) {
    setShowErrors(false)
    setStepIdx(i)
  }

  function submit() {
    const attestation = {
      attestation_id: `att-new-${Date.now().toString(36)}`,
      version: '1.0',
      supplier_id: form.supplier_id.trim(),
      timestamp: new Date().toISOString(),
      action_type: form.action_type,
      performed_in_country: form.performed_in_country,
      parents: isRaw
        ? []
        : form.parents.map((p) => ({
            attestation_id: p.attestation_id,
            content_hash: genHash(p.attestation_id),
            quantity_consumed: Number(p.quantity_consumed) || 0,
            unit: p.unit,
          })),
      output: {
        name: form.output.name.trim(),
        quantity_produced: Number(form.output.quantity_produced) || 0,
        unit: form.output.unit.trim(),
      },
      costs: {
        material_cad: Number(form.costs.material_cad) || 0,
        labour_hours: Number(form.costs.labour_hours) || 0,
        labour_cost_cad: Number(form.costs.labour_cost_cad) || 0,
      },
      signature: { algorithm: 'ed25519', value: 'demo-unsigned' },
    }
    onSubmit?.(attestation)
  }

  const pct = ((stepIdx + 1) / steps.length) * 100

  return (
    <div className={styles.form}>
      <nav className={styles.sidebar} aria-label="Form steps">
        <ol className={styles.stepList}>
          {steps.map((s, i) => {
            const state = i === stepIdx ? 'current' : i < stepIdx ? 'done' : 'todo'
            return (
              <li key={s.id}>
                <button
                  type="button"
                  className={`${styles.stepItem} ${styles[state]}`}
                  onClick={() => jumpTo(i)}
                  aria-current={i === stepIdx ? 'step' : undefined}
                >
                  <span className={styles.stepNum}>{i + 1}</span>
                  <span className={styles.stepTitle}>{s.title}</span>
                </button>
              </li>
            )
          })}
        </ol>
      </nav>

      <section className={styles.main}>
        <Progress.Root className={styles.progress} value={pct}>
          <Progress.Indicator className={styles.progressInd} style={{ transform: `translateX(-${100 - pct}%)` }} />
        </Progress.Root>

        <header className={styles.stepHeader}>
          <span className={styles.stepCount}>
            Step {stepIdx + 1} of {steps.length}
          </span>
          <h2 className={styles.stepHeading}>{step.title}</h2>
          <p className={styles.stepDesc}>{step.desc}</p>
        </header>

        <div className={styles.body}>
          {step.id === 'type' && (
            <ActionTypeSelector
              value={form.action_type}
              onChange={(action_type) => {
                setForm((f) => ({ ...f, action_type, parents: action_type === 'raw_material_supply' ? [] : f.parents }))
                setShowErrors(false)
              }}
            />
          )}

          {step.id === 'inputs' && (
            <ParentPicker
              options={options}
              value={form.parents}
              onChange={(parents) => setForm((f) => ({ ...f, parents }))}
            />
          )}

          {step.id === 'output' && (
            <OutputFields
              value={form.output}
              onChange={(output) => setForm((f) => ({ ...f, output }))}
              errors={currentErrors}
            />
          )}

          {step.id === 'costs' && (
            <CostFields
              value={form.costs}
              actionType={form.action_type}
              onChange={(costs) => setForm((f) => ({ ...f, costs }))}
            />
          )}

          {step.id === 'location' && (
            <div className={styles.locationGrid}>
              <Field label="Performed in country" htmlFor="loc-country" error={currentErrors.performed_in_country}>
                <CountrySelect
                  id="loc-country"
                  value={form.performed_in_country}
                  onChange={(performed_in_country) => setForm((f) => ({ ...f, performed_in_country }))}
                />
              </Field>
              <Field label="Supplier id" htmlFor="loc-supplier" error={currentErrors.supplier_id}>
                <TextInput
                  id="loc-supplier"
                  className="mono"
                  value={form.supplier_id}
                  onChange={(e) => setForm((f) => ({ ...f, supplier_id: e.target.value }))}
                  invalid={!!currentErrors.supplier_id}
                />
              </Field>
              {overConsumed.length > 0 && (
                <p className={styles.warn} role="status">
                  Heads up: {overConsumed.length} input{overConsumed.length === 1 ? '' : 's'} consume more than the
                  parent produced. The verifier would flag this as a mass-balance violation.
                </p>
              )}
              <p className={styles.signNote}>
                On submit, this attestation is canonicalized and Ed25519-signed by the backend, then linked into the
                product chain.
              </p>
            </div>
          )}
        </div>

        <footer className={styles.nav}>
          {stepIdx > 0 ? (
            <button type="button" className={styles.secondary} onClick={goBack}>
              Back
            </button>
          ) : (
            <span />
          )}
          <button type="button" className={styles.primary} onClick={goNext}>
            {isLast ? 'Sign & submit' : 'Continue'}
          </button>
        </footer>
      </section>

      <div className={styles.previewCol}>
        <AttestationPreviewCard form={form} />
      </div>
    </div>
  )
}
