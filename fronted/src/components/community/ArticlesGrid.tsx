import styles from './CommunityPage.module.css'
import type { ArticleItem } from './types'

interface ArticlesGridProps {
  items: ArticleItem[]
  loading: boolean
}

export function ArticlesGrid({ items, loading }: ArticlesGridProps) {
  if (loading) {
    return (
      <div className={styles.stateWrapper}>
        <div className={styles.stateMessage}>Загрузка статей…</div>
      </div>
    )
  }

  if (items.length === 0) {
    return (
      <div className={styles.stateWrapper}>
        <div className={styles.stateMessage}>Статьи не найдены</div>
      </div>
    )
  }

  return (
    <div className={styles.grid}>
      {items.map((article) => (
        <article key={article.id} className={styles.articleCard}>
          <div className={styles.articleHeader}>
            <span className={styles.articleCategory}>{article.category}</span>
            <span className={styles.readTime}>{article.readTime}</span>
          </div>
          <h3 className={styles.cardTitle}>{article.title}</h3>
          <p className={styles.cardExcerpt}>{article.excerpt}</p>
          <button type="button" className={styles.ctaButton}>
            Читать статью
          </button>
        </article>
      ))}
    </div>
  )
}
