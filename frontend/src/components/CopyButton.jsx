import { useEffect, useRef, useState } from 'react'
import styles from './CopyButton.module.css'

export default function CopyButton({ value, label = 'Copy' }) {
  const [copied, setCopied] = useState(false)
  const timer = useRef(null)

  useEffect(() => () => clearTimeout(timer.current), [])

  async function copy() {
    try {
      await navigator.clipboard.writeText(String(value))
      setCopied(true)
      clearTimeout(timer.current)
      timer.current = setTimeout(() => setCopied(false), 1500)
    } catch {
      /* clipboard unavailable — no-op */
    }
  }

  return (
    <button type="button" className={styles.btn} onClick={copy} aria-label={`${label} ${value}`}>
      {copied ? 'Copied' : label}
    </button>
  )
}
