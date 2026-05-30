import { Routes, Route } from 'react-router-dom'

import NavBar from './components/NavBar.jsx'
import HomePage from './pages/HomePage.jsx'
import SupplierPage from './pages/SupplierPage.jsx'
import LookupPage from './pages/LookupPage.jsx'
import ProductPage from './pages/ProductPage.jsx'
import NotFoundPage from './pages/NotFoundPage.jsx'

import styles from './App.module.css'

export default function App() {
  return (
    <div className={styles.app}>
      <NavBar />
      <main className={styles.main}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/supplier" element={<SupplierPage />} />
          <Route path="/lookup" element={<LookupPage />} />
          <Route path="/product/:productId" element={<ProductPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </main>
    </div>
  )
}
