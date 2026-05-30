import StatusDot from './StatusDot.jsx'
import styles from './ChainValidityBadge.module.css'

// Ink text + a green/red verdict StatusDot. The dot is the only colour.
export default function ChainValidityBadge({ valid, anomalyCount = 0, verifying = false }) {
  if (verifying) {
    return (
      <span className={styles.badge}>
        <StatusDot state="verifying" />
      </span>
    )
  }
  return (
    <span className={styles.badge}>
      <StatusDot state={valid ? 'verified' : 'invalid'} />
      {anomalyCount > 0 && (
        <span className={styles.count}>
          {anomalyCount} {anomalyCount === 1 ? 'issue' : 'issues'}
        </span>
      )}
    </span>
  )
}
