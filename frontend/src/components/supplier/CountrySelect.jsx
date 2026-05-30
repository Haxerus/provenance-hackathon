import { Select } from 'radix-ui'
import styles from './CountrySelect.module.css'

const COUNTRIES = [
  { code: 'CA', name: 'Canada' },
  { code: 'US', name: 'United States' },
  { code: 'FR', name: 'France' },
  { code: 'GB', name: 'United Kingdom' },
  { code: 'DE', name: 'Germany' },
  { code: 'HK', name: 'Hong Kong' },
  { code: 'CN', name: 'China' },
  { code: 'VN', name: 'Vietnam' },
  { code: 'JP', name: 'Japan' },
  { code: 'MX', name: 'Mexico' },
]

export default function CountrySelect({ value, onChange, id }) {
  return (
    <Select.Root value={value || undefined} onValueChange={onChange}>
      <Select.Trigger className={styles.trigger} id={id} aria-label="Performed in country">
        <Select.Value placeholder="Select a country" />
        <Select.Icon className={styles.caret}>▾</Select.Icon>
      </Select.Trigger>
      <Select.Portal>
        <Select.Content className={styles.content} position="popper" sideOffset={6}>
          <Select.Viewport className={styles.viewport}>
            {COUNTRIES.map((c) => (
              <Select.Item key={c.code} value={c.code} className={styles.item}>
                <Select.ItemText>
                  <span className={`${styles.code} mono`}>{c.code}</span> {c.name}
                </Select.ItemText>
                <Select.ItemIndicator className={styles.indicator} />
              </Select.Item>
            ))}
          </Select.Viewport>
        </Select.Content>
      </Select.Portal>
    </Select.Root>
  )
}
