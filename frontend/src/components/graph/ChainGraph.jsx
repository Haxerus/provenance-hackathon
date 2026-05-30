import { useMemo, useCallback } from 'react'
import { ReactFlow, Background, Controls, Panel, MarkerType } from '@xyflow/react'
import '@xyflow/react/dist/style.css'

import ProvenanceNode from './ProvenanceNode.jsx'
import GraphLegend from '../GraphLegend.jsx'
import { layoutChain } from '../../lib/graphLayout.js'
import styles from './ChainGraph.module.css'

const nodeTypes = { provenance: ProvenanceNode }

// Literal hex (mirror of tokens) — SVG marker/stroke colours don't resolve CSS vars.
const EDGE = '#c8cade'
const EDGE_TAMPERED = '#c8202c'

export default function ChainGraph({
  chain,
  anomaliesByAtt = {},
  productId,
  highlightId,
  selectedId,
  onSelect,
  showLegendAnomalies = true,
}) {
  const { nodes, edges } = useMemo(() => {
    const laid = layoutChain(chain, { anomaliesByAtt, productId, highlightId })
    const styledEdges = laid.edges.map((e) => {
      const tampered = e.data?.tampered
      return {
        ...e,
        type: 'default',
        markerEnd: {
          type: MarkerType.ArrowClosed,
          width: 16,
          height: 16,
          color: tampered ? EDGE_TAMPERED : EDGE,
        },
        style: tampered
          ? { stroke: EDGE_TAMPERED, strokeWidth: 1.5, strokeDasharray: '5 4' }
          : { stroke: EDGE, strokeWidth: 1.5 },
      }
    })
    const withSelection = laid.nodes.map((n) => ({ ...n, selected: n.id === selectedId }))
    return { nodes: withSelection, edges: styledEdges }
  }, [chain, anomaliesByAtt, productId, highlightId, selectedId])

  const handleNodeClick = useCallback((_, node) => onSelect?.(node.id), [onSelect])
  const handlePaneClick = useCallback(() => onSelect?.(null), [onSelect])

  return (
    <div className={styles.wrap}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodeClick={handleNodeClick}
        onPaneClick={handlePaneClick}
        fitView
        fitViewOptions={{ padding: 0.22 }}
        minZoom={0.2}
        maxZoom={1.75}
        nodesDraggable={false}
        nodesConnectable={false}
        edgesFocusable={false}
        elementsSelectable
      >
        <Background color="#e2e4ed" gap={22} size={1} />
        <Controls showInteractive={false} position="bottom-right" />
        <Panel position="top-left">
          <GraphLegend showAnomalies={showLegendAnomalies} />
        </Panel>
      </ReactFlow>
    </div>
  )
}
