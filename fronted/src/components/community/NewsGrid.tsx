import styles from './CommunityPage.module.css'
import type { NewsItem } from './types'

interface NewsGridProps {
  items: NewsItem[]
  loading: boolean
}

export function NewsGrid({ items, loading }: NewsGridProps) {
  if (loading) {
    return (
      <div className={styles.stateWrapper}>
        <div className={styles.stateMessage}>Загрузка новостей…</div>
      </div>
    )
  }

  if (items.length === 0) {
    return (
      <div className={styles.stateWrapper}>
        <div className={styles.stateMessage}>Новости не найдены</div>
      </div>
    )
  }

  return (
    <div className={styles.grid}>
      {items.map((news) => (
        <article key={news.id} className={styles.newsCard}>
          <span className={styles.cardCategory}>{news.category}</span>
          <h3 className={styles.cardTitle}>{news.title}</h3>
          <p className={styles.cardExcerpt}>{news.excerpt}</p>
          <div className={styles.newsMeta}>
            <span>{news.date}</span>
            <span>{news.author}</span>
          </div>
          <button type="button" className={styles.ctaButton}>
            Читать далее
          </button>
        </article>
      ))}
    </div>
  )
}
