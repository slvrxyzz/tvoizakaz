import styles from './CommunityPage.module.css'
import type { TestItem } from './types'

interface TestsGridProps {
  items: TestItem[]
  loading: boolean
}

export function TestsGrid({ items, loading }: TestsGridProps) {
  if (loading) {
    return (
      <div className={styles.stateWrapper}>
        <div className={styles.stateMessage}>Загрузка тестов…</div>
      </div>
    )
  }

  if (items.length === 0) {
    return (
      <div className={styles.stateWrapper}>
        <div className={styles.stateMessage}>Тесты не найдены</div>
      </div>
    )
  }

  return (
    <div className={styles.testsGrid}>
      {items.map((test) => (
        <article key={test.id} className={styles.testCard}>
          <h3 className={styles.cardTitle}>{test.title}</h3>
          <p className={styles.cardExcerpt}>{test.description}</p>
          <div className={styles.testMeta}>
            <span>{test.questionsCount} вопросов</span>
            <span>{test.completionTime}</span>
          </div>
          <button type="button" className={styles.secondaryButton}>
            Начать тест
          </button>
        </article>
      ))}
    </div>
  )
}
