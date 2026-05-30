import styles from './SeverityDot.module.css'

// Colour-independent severity cue: filled (critical) / half (warning) / hollow (subtle).
// Pairs with colour so meaning survives colour-blindness (DESIGN.md).
export default function SeverityDot({ severity = 'warning' }) {
  return <span className={`${styles.dot} ${styles[severity]}`} aria-hidden="true" />
}
