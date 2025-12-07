import { useState } from 'react'

import styles from './OrdersPage.module.css'

interface OrdersSortProps {
  selected: string
  onChange: (value: string) => void
}

const SORT_OPTIONS = [
  { value: 'newest', label: 'Сначала новые' },
  { value: 'price_high', label: 'Дорогие заказы' },
  { value: 'price_low', label: 'Дешевые заказы' },
  { value: 'deadline', label: 'Срочные заказы' },
]

export function OrdersSort({ selected, onChange }: OrdersSortProps) {
  const [open, setOpen] = useState(false)

  const handleSelect = (value: string) => {
    onChange(value)
    setOpen(false)
  }

  const label = SORT_OPTIONS.find((option) => option.value === selected)?.label ?? SORT_OPTIONS[0].label

  return (
    <div className={styles.sortContainer}>
      <button type="button" className={styles.sortTrigger} onClick={() => setOpen((prev) => !prev)}>
        {label}
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="m6 9 6 6 6-6" />
        </svg>
      </button>

      {open && (
        <div className={styles.sortDropdown}>
          {SORT_OPTIONS.map((option) => (
            <button
              key={option.value}
              type="button"
              className={`${styles.sortOption} ${selected === option.value ? styles.sortOptionActive : ''}`}
              onClick={() => handleSelect(option.value)}
            >
              {option.label}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
