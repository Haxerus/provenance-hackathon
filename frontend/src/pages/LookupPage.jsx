import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { resolveByHash, listProducts } from '../data/products.js'
import styles from './LookupPage.module.css'

export default function LookupPage() {
  const [value, setValue] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const samples = listProducts()

  function submit(e) {
    e.preventDefault()
    const id = resolveByHash(value)
    if (id) {
      navigate(`/product/${id}`)
    } else {
      setError('No chain matches that id or hash. Check the value and try again.')
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <h1 className={styles.title}>Look up a product</h1>
        <p className={styles.sub}>Enter a chain hash or product attestation id to verify its provenance.</p>

        <form onSubmit={submit} className={styles.form}>
          <input
            className={styles.input}
            value={value}
            onChange={(e) => {
              setValue(e.target.value)
              setError('')
            }}
            placeholder="att-anchor-0012  ·  content hash  ·  DRONE-12"
            aria-label="Chain hash or product id"
            autoComplete="off"
            spellCheck="false"
          />
          <button type="submit" className={styles.primary}>
            Verify
          </button>
        </form>

        {error && (
          <p className={styles.error} role="alert">
            {error}
          </p>
        )}

        <div className={styles.scanRow}>
          <button type="button" className={styles.scan} disabled>
            Scan QR code
          </button>
          <span className={styles.soon}>Coming soon</span>
        </div>
      </div>

      <div className={styles.samples}>
        <span className={styles.samplesLabel}>Try a sample</span>
        <ul className={styles.sampleList}>
          {samples.map((p) => (
            <li key={p.id}>
              <Link to={`/product/${p.id}`} className={styles.sample}>
                <span className={styles.sampleName}>{p.name}</span>
                <span className={`${styles.sampleId} mono`}>{p.id}</span>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
