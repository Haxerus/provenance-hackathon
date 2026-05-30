import { useState } from 'react'
import { Link } from 'react-router-dom'

import AttestationForm from '../components/supplier/AttestationForm.jsx'
import ChainView from './ChainView.jsx'
import { recoveryDroneChain } from '../data/chains.js'
import { PRODUCTS } from '../data/products.js'
import { truncateMiddle } from '../lib/format.js'
import styles from './SupplierPage.module.css'

const TARGET = PRODUCTS['att-anchor-0012']

export default function SupplierPage() {
  const [result, setResult] = useState(null)

  function handleSubmit(attestation) {
    const chain = {
      product_attestation_id: recoveryDroneChain.product_attestation_id,
      attestations: [...recoveryDroneChain.attestations, attestation],
    }
    setResult({ chain, attestation })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  if (result) {
    const banner = (
      <div className={styles.banner}>
        <div className={styles.bannerText}>
          <span className={styles.bannerTitle}>Attestation signed and linked</span>
          <span className={styles.bannerSub}>
            <span className="mono">{truncateMiddle(result.attestation.attestation_id, 18, 6)}</span> is now part of{' '}
            {TARGET.name}.
          </span>
        </div>
        <div className={styles.bannerActions}>
          <button type="button" className={styles.secondary} onClick={() => setResult(null)}>
            Add another
          </button>
          <Link to={`/product/${TARGET.id}`} className={styles.primary}>
            Open purchaser view
          </Link>
        </div>
      </div>
    )

    return (
      <ChainView
        mode="supplier"
        product={TARGET}
        chain={result.chain}
        anomaliesByAtt={{}}
        highlightId={result.attestation.attestation_id}
        banner={banner}
      />
    )
  }

  return (
    <div className={styles.page}>
      <header className={styles.head}>
        <h1 className={styles.title}>Issue an attestation</h1>
        <p className={styles.sub}>
          Contributing to <strong>{TARGET.name}</strong>. Record this step; it links into the product chain on submit.
        </p>
      </header>
      <AttestationForm options={recoveryDroneChain.attestations} onSubmit={handleSubmit} />
    </div>
  )
}
