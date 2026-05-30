import styles from './Field.module.css'

export function Field({ label, hint, error, htmlFor, children }) {
  return (
    <div className={styles.field}>
      {label && (
        <label className={styles.label} htmlFor={htmlFor}>
          {label}
        </label>
      )}
      {children}
      {error ? (
        <p className={styles.error} role="alert">
          {error}
        </p>
      ) : hint ? (
        <p className={styles.hint}>{hint}</p>
      ) : null}
    </div>
  )
}

export function TextInput({ invalid, className = '', ...props }) {
  return <input className={`${styles.input} ${invalid ? styles.invalid : ''} ${className}`} {...props} />
}

export function NumberInput({ invalid, className = '', ...props }) {
  return (
    <input
      type="number"
      inputMode="decimal"
      className={`${styles.input} tabular ${invalid ? styles.invalid : ''} ${className}`}
      {...props}
    />
  )
}
