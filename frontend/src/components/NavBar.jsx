import { useEffect, useState } from 'react'
import { NavLink } from 'react-router-dom'
import styles from './NavBar.module.css'

function tabClass({ isActive }) {
  return isActive ? `${styles.tab} ${styles.active}` : styles.tab
}

export default function NavBar() {
  // Sticky bar at the top; detaches into a floating pill once you scroll past it.
  const [scrolled, setScrolled] = useState(() => typeof window !== 'undefined' && window.scrollY > 8)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <header className={`${styles.nav} ${scrolled ? styles.scrolled : ''}`}>
      <nav className={styles.pill} aria-label="Primary">
        <NavLink to="/supplier" className={tabClass}>
          Supplier
        </NavLink>
        <NavLink to="/lookup" className={tabClass}>
          Lookup
        </NavLink>
      </nav>
    </header>
  )
}
