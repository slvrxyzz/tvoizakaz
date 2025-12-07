'use client'

import { useState } from 'react'
import styles from './OrdersPage.module.css'

interface OrdersFiltersSidebarProps {
  onClear?: () => void
}

export function OrdersFiltersSidebar({ onClear }: OrdersFiltersSidebarProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <aside className={`${styles.filters} ${isExpanded ? styles.filtersExpanded : ''}`}>
      <div className={styles.filtersHeader}>
        <h3 className={styles.filtersTitle}>Фильтры</h3>
        <div className={styles.filtersHeaderActions}>
          <button type="button" className={styles.clearButton} onClick={onClear}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 6h18M7 12h10M5 18h14" />
            </svg>
            <span className={styles.clearButtonText}>Сбросить всё</span>
          </button>
          <button 
            type="button" 
            className={styles.filtersToggle}
            onClick={() => setIsExpanded(!isExpanded)}
            aria-expanded={isExpanded}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d={isExpanded ? "M18 15l-6-6-6 6" : "M6 9l6 6 6-6"} />
            </svg>
          </button>
        </div>
      </div>

      <div className={styles.filtersBody}>
        <div className={styles.filterSection}>
          <h4 className={styles.filterTitle}>Категория</h4>
          <div className={styles.filterOptions}>
            {['Все категории', 'Дизайн', 'Разработка', 'Копирайтинг', 'Маркетинг', 'Фото/Видео'].map((label) => (
              <label key={label} className={styles.checkbox}>
                <input type="checkbox" defaultChecked={label === 'Все категории'} />
                <span>{label}</span>
              </label>
            ))}
          </div>
        </div>

        <div className={styles.filterSection}>
          <h4 className={styles.filterTitle}>Бюджет</h4>
          <div className={styles.priceInputs}>
            <input type="number" placeholder="От" className={styles.priceInput} />
            <input type="number" placeholder="До" className={styles.priceInput} />
          </div>
          <input type="range" min="0" max="50000" step="1000" className={styles.rangeSlider} />
        </div>

        <div className={styles.filterSection}>
          <h4 className={styles.filterTitle}>Срок выполнения</h4>
          <select className={styles.select} defaultValue="">
            <option value="">Любой срок</option>
            <option value="1">До 1 дня</option>
            <option value="3">До 3 дней</option>
            <option value="7">До 7 дней</option>
            <option value="14">До 14 дней</option>
          </select>
        </div>

        <button type="button" className={styles.applyButton}>
          Применить фильтры
        </button>
      </div>
    </aside>
  )
}
