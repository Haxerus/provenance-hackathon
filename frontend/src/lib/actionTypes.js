// Action-type metadata. Colour lives ONLY in the graph (swatch token + label).
export const ACTION_TYPES = {
  raw_material_supply: { label: 'RAW MATERIAL', short: 'Raw material', color: 'var(--type-raw)' },
  component_manufacture: { label: 'COMPONENT MFG', short: 'Component mfg', color: 'var(--type-component)' },
  subassembly: { label: 'SUBASSEMBLY', short: 'Subassembly', color: 'var(--type-subassembly)' },
  final_integration: { label: 'FINAL INTEGRATION', short: 'Final integration', color: 'var(--type-final)' },
}

export const ACTION_TYPE_ORDER = [
  'raw_material_supply',
  'component_manufacture',
  'subassembly',
  'final_integration',
]

export function actionTypeMeta(type) {
  return (
    ACTION_TYPES[type] ?? {
      label: String(type || 'UNKNOWN').replace(/_/g, ' ').toUpperCase(),
      short: type,
      color: 'var(--color-muted)',
    }
  )
}

export const TRANSFORMATIONS = ['component_manufacture', 'subassembly', 'final_integration']
export const isTransformation = (type) => TRANSFORMATIONS.includes(type)
