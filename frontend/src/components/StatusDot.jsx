import styles from './StatusDot.module.css'

const DEFAULT_LABEL = {
  verified: 'Chain verified',
  invalid: 'Chain invalid',
  verifying: 'Verifying…',
}

// The one semantic colour outside the graph: a small green/red verdict dot
// (Vercel deployment-dot style). Text stays ink; only the dot carries colour.
export default function StatusDot({ state = 'verifying', children, showLabel = true }) {
  const label = children ?? DEFAULT_LABEL[state] ?? ''
  return (
    <span className={`${styles.wrap} ${styles[state]}`}>
      <span className={styles.dot} aria-hidden="true" />
      {showLabel && <span className={styles.label}>{label}</span>}
      {!showLabel && <span className="sr-only">{label}</span>}
    </span>
  )
}
