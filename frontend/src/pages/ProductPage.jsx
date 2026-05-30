import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'

import ChainView from './ChainView.jsx'
import StatusDot from '../components/StatusDot.jsx'
import { getProduct } from '../data/products.js'
import styles from './ProductPage.module.css'

export default function ProductPage() {
  const { productId } = useParams()
  const product = getProduct(productId)
  // "verified once the simulated check for THIS product id has elapsed"
  const [verifiedId, setVerifiedId] = useState(null)
  const verifying = verifiedId !== productId

  useEffect(() => {
    const t = setTimeout(() => setVerifiedId(productId), 650)
    return () => clearTimeout(t)
  }, [productId])

  if (!product) {
    return (
      <div className={styles.centered}>
        <h1 className={styles.title}>Product not found</h1>
        <p className={styles.text}>
          No chain resolves to <span className="mono">{productId}</span>. It may be unanchored, or the id is wrong.
        </p>
        <Link to="/lookup" className={styles.link}>
          Back to lookup
        </Link>
      </div>
    )
  }

  if (verifying) {
    return (
      <div className={styles.centered}>
        <StatusDot state="verifying">Verifying chain…</StatusDot>
        <p className={styles.text}>Checking signatures, parent hashes, mass balance, and statistical fit.</p>
      </div>
    )
  }

  return (
    <ChainView
      mode="purchaser"
      product={product}
      chain={product.chain}
      verification={product.verification}
      anomaliesByAtt={product.anomaliesByAtt}
    />
  )
}
