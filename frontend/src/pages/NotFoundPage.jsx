import { Link } from 'react-router-dom'
import styles from './ProductPage.module.css'

export default function NotFoundPage() {
  return (
    <div className={styles.centered}>
      <h1 className={styles.title}>Page not found</h1>
      <p className={styles.text}>That route doesn&apos;t exist.</p>
      <Link to="/" className={styles.link}>
        Back home
      </Link>
    </div>
  )
}
