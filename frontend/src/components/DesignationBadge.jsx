import styles from './DesignationBadge.module.css'

const LABELS = {
  product_of_canada: 'Product of Canada',
  made_in_canada: 'Made in Canada',
  none: 'No designation',
}

// Always a plain gray pill — never green/gold (DESIGN.md).
export default function DesignationBadge({ type = 'none' }) {
  return <span className={styles.badge}>{LABELS[type] ?? LABELS.none}</span>
}
