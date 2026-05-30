import { useMemo, useState } from 'react'
import ChainGraph from '../components/graph/ChainGraph.jsx'
import ProductSummary from '../components/purchaser/ProductSummary.jsx'
import NodeDetailPanel from '../components/purchaser/NodeDetailPanel.jsx'
import { directCost } from '../lib/format.js'
import styles from './ChainView.module.css'

export default function ChainView({
  mode = 'purchaser',
  product,
  chain,
  verification,
  anomaliesByAtt = {},
  highlightId,
  banner,
}) {
  const [selectedId, setSelectedId] = useState(highlightId ?? null)

  const attById = useMemo(
    () => new Map((chain?.attestations ?? []).map((a) => [a.attestation_id, a])),
    [chain],
  )
  const totalCost = useMemo(
    () => (chain?.attestations ?? []).reduce((s, a) => s + directCost(a), 0),
    [chain],
  )

  const selected = selectedId ? attById.get(selectedId) : null
  const selectedAnoms = selectedId ? anomaliesByAtt[selectedId] ?? [] : []

  if (mode === 'supplier') {
    return (
      <div className={styles.supplier}>
        {banner}
        <ChainGraph
          chain={chain}
          anomaliesByAtt={anomaliesByAtt}
          productId={product?.id}
          highlightId={highlightId}
          selectedId={selectedId}
          onSelect={setSelectedId}
          showLegendAnomalies={false}
        />
      </div>
    )
  }

  return (
    <div className={styles.purchaser}>
      <div className={styles.split}>
        <ChainGraph
          chain={chain}
          anomaliesByAtt={anomaliesByAtt}
          productId={product?.id}
          selectedId={selectedId}
          onSelect={setSelectedId}
        />
        <aside className={styles.side}>
          <ProductSummary product={product} verification={verification} chain={chain} />
          <NodeDetailPanel
            key={selectedId || 'empty'}
            attestation={selected}
            anomalies={selectedAnoms}
            totalCost={totalCost}
          />
        </aside>
      </div>
    </div>
  )
}
