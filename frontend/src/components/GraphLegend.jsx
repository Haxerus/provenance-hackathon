import { ACTION_TYPE_ORDER, actionTypeMeta } from '../lib/actionTypes.js'
import SeverityDot from './SeverityDot.jsx'
import styles from './GraphLegend.module.css'

// Always visible: comprehension of the colour-coded graph depends on it (DESIGN.md).
export default function GraphLegend({ showAnomalies = true }) {
  return (
    <div className={styles.legend} aria-label="Graph legend">
      <div className={styles.group}>
        <span className={styles.heading}>Type</span>
        <div className={styles.items}>
          {ACTION_TYPE_ORDER.map((t) => {
            const m = actionTypeMeta(t)
            return (
              <span key={t} className={styles.item}>
                <span className={styles.swatch} style={{ background: m.color }} />
                {m.short}
              </span>
            )
          })}
        </div>
      </div>

      {showAnomalies && (
        <div className={styles.group}>
          <span className={styles.heading}>Status</span>
          <div className={styles.items}>
            <span className={styles.item}>
              <SeverityDot severity="critical" /> Critical
            </span>
            <span className={styles.item}>
              <SeverityDot severity="warning" /> Warning
            </span>
            <span className={styles.item}>
              <SeverityDot severity="subtle" /> Statistical
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
