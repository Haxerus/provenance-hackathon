import { Link } from 'react-router-dom'
import { listProducts } from '../data/products.js'
import styles from './HomePage.module.css'

export default function HomePage() {
  const products = listProducts()
  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <h1 className={styles.title}>Provenance you can verify, not just trust.</h1>
        <p className={styles.lede}>
          Every supplier contribution is a signed attestation. Attestations link into a tamper-evident chain that
          computes a product&apos;s Canadian-content designation and surfaces forgery, tampering, and replay.
        </p>
      </section>

      <div className={styles.cards}>
        <Link to="/supplier" className={styles.card}>
          <span className={styles.cardKicker}>Supplier</span>
          <span className={styles.cardTitle}>Issue an attestation</span>
          <span className={styles.cardText}>
            Record your contribution (materials, labour, location), then link it into the product chain.
          </span>
          <span className={styles.cardCta}>Start →</span>
        </Link>

        <Link to="/lookup" className={styles.card}>
          <span className={styles.cardKicker}>Purchaser</span>
          <span className={styles.cardTitle}>Look up a product</span>
          <span className={styles.cardText}>
            Enter a chain hash or product id to see its provenance, Canadian content, and verification status.
          </span>
          <span className={styles.cardCta}>Look up →</span>
        </Link>
      </div>

      <section className={styles.samples}>
        <span className={styles.samplesLabel}>Sample products</span>
        <ul className={styles.sampleList}>
          {products.map((p) => (
            <li key={p.id}>
              <Link to={`/product/${p.id}`} className={styles.sample}>
                <span className={styles.sampleName}>{p.name}</span>
                <span className={`${styles.sampleId} mono`}>{p.id}</span>
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
