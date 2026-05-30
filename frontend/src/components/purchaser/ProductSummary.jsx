import StatusDot from '../StatusDot.jsx'
import DesignationBadge from '../DesignationBadge.jsx'
import CopyButton from '../CopyButton.jsx'
import { directCost, formatCAD, formatPercent, truncateMiddle } from '../../lib/format.js'
import styles from './ProductSummary.module.css'

// Product-level metadata, formatted like NodeDetailPanel (title + id, metadata below).
// Lives at the top of the sidebar so the page needs only one header (the nav).
export default function ProductSummary({ product, verification, chain }) {
  const atts = chain?.attestations ?? []
  const suppliers = new Set(atts.map((a) => a.supplier_id)).size
  const cost = atts.reduce((s, a) => s + directCost(a), 0)
  const anomalyCount = verification?.anomalies?.length ?? 0
  const valid = verification?.chain_valid

  return (
    <div className={styles.summary}>
      <header className={styles.header}>
        <span className={styles.eyebrow}>Product</span>
        <h2 className={styles.name}>{product?.name ?? 'Unknown product'}</h2>
        <div className={styles.idRow}>
          <span className="mono">{truncateMiddle(product?.id ?? '', 16, 6)}</span>
          <CopyButton value={product?.id} />
        </div>
        <StatusDot state={valid === false ? 'invalid' : 'verified'}>
          {valid === false ? 'Chain invalid' : 'Chain verified'}
        </StatusDot>
      </header>

      <section className={styles.hero}>
        <div className={styles.heroNum}>
          <span className={`${styles.percent} tabular`}>{formatPercent(verification?.canadian_content_percentage)}</span>
          <span className={styles.percentUnit}>%</span>
        </div>
        <div className={styles.heroMeta}>
          <span className={styles.heroLabel}>Canadian content</span>
          <DesignationBadge type={verification?.designation ?? 'none'} />
        </div>
      </section>

      <section className={styles.section}>
        <h3 className={styles.sectionTitle}>Chain</h3>
        <Row label="Nodes" value={atts.length} />
        <Row label="Suppliers" value={suppliers} />
        <Row label="Direct cost" value={formatCAD(cost)} />
        <Row label="Anomalies" value={anomalyCount} />
      </section>

      {anomalyCount > 0 && (
        <p className={styles.hint}>Flagged nodes are highlighted in the graph. Select one to see the issue.</p>
      )}
    </div>
  )
}

function Row({ label, value }) {
  return (
    <div className={styles.row}>
      <span className={styles.rowLabel}>{label}</span>
      <span className={`${styles.rowValue} tabular`}>{value}</span>
    </div>
  )
}
