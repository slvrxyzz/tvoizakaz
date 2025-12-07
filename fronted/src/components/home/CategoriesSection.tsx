import { ReactNode } from 'react'

import styles from './HomeSections.module.css'

interface CategoryItem {
  id: number
  name: string
  active_orders_count?: number
}

interface CategoriesSectionProps {
  categories: CategoryItem[]
  loading: boolean
  renderEmoji: (category: CategoryItem) => ReactNode
}

export function CategoriesSection({ categories, loading, renderEmoji }: CategoriesSectionProps) {
  return (
    <section className={styles.sectionCompact}>
      <div className={styles.container}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>Категории услуг</h2>
          <p className={styles.sectionSubtitle}>Выбери направление по душе и начни зарабатывать</p>
        </div>

        {loading ? (
          <div className={styles.loadingState}>Загрузка категорий…</div>
        ) : categories.length === 0 ? (
          <div className={styles.emptyState}>Категории не найдены</div>
        ) : (
          <div className={styles.categoriesGrid}>
            {categories.map((category) => (
              <div key={category.id} className={styles.categoryCard}>
                <div className={styles.categoryEmoji}>{renderEmoji(category)}</div>
                <div className={styles.categoryTitle}>{category.name}</div>
                <div className={styles.categoryMeta}>
                  {category.active_orders_count ?? 0} активных заказов
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  )
}

