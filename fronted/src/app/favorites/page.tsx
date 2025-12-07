'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

import Footer from '@/components/layout/Footer'
import Header from '@/components/layout/Header'
import styles from '@/components/favorites/FavoritesPage.module.css'
import { useFavorites } from '@/hooks/useFavorites'
import { useAuth } from '@/providers/AuthProvider'
import { formatCurrency } from '@/utils/currency'

const STATUS_MAP: Record<string, { text: string; className: string }> = {
  OPEN: { text: 'Открыт', className: styles.statusOpen },
  WORK: { text: 'В работе', className: styles.statusWork },
  REVIEW: { text: 'На проверке', className: styles.statusReview },
  CLOSE: { text: 'Закрыт', className: styles.statusClose },
}

const PRIORITY_MAP: Record<string, { text: string; className: string }> = {
  LOW: { text: 'Низкий', className: styles.priorityBase },
  NORMAL: { text: 'Обычный', className: styles.priorityBase },
  HIGH: { text: 'Высокий', className: styles.priorityPremium },
  URGENT: { text: 'Срочный', className: styles.priorityExpress },
}

export default function FavoritesPage() {
  const router = useRouter()
  const { user, isAuthenticated, loading: authLoading } = useAuth()
  const { favorites, loading, error, total, page, totalPages, fetchFavorites, removeFromFavorites } = useFavorites()

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, authLoading, router])

  useEffect(() => {
    if (isAuthenticated) {
      fetchFavorites()
    }
  }, [isAuthenticated, fetchFavorites])

  const handleRemoveFavorite = async (orderId: number) => {
    const success = await removeFromFavorites(orderId)
    if (success) {
      fetchFavorites(page)
    }
  }

  const formatDate = (dateString: string) => new Date(dateString).toLocaleDateString('ru-RU')

  const renderStatusBadge = (status: string) => {
    const config = STATUS_MAP[status] || { text: status, className: styles.statusDefault }
    return <span className={`${styles.statusBadge} ${config.className}`}>{config.text}</span>
  }

  const renderPriorityBadge = (priority: string) => {
    const config = PRIORITY_MAP[priority] || { text: priority, className: styles.priorityDefault }
    return <span className={`${styles.priorityBadge} ${config.className}`}>{config.text}</span>
  }

  if (authLoading) {
    return (
      <>
        <Header />
        <main className={styles.page}>
          <div className={styles.container}>
            <div className={styles.loading}>
              <div className={styles.spinner} />
              <p>Загрузка...</p>
            </div>
          </div>
        </main>
        <Footer />
      </>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <>
      <Header />

      <main className={styles.page}>
        <div className={styles.container}>
          <header className={styles.header}>
            <h1 className={styles.title}>Избранные заказы</h1>
            <p className={styles.subtitle}>Здесь собраны все заказы, которые вы отметили как избранные.</p>
          </header>

          {loading ? (
            <div className={styles.loading}>
              <div className={styles.spinner} />
              <p>Загрузка избранных заказов...</p>
            </div>
          ) : error ? (
            <div className={styles.error}>
              <h3 className={styles.errorTitle}>Не удалось загрузить избранное</h3>
              <p>{error}</p>
              <button type="button" onClick={() => fetchFavorites()} className={styles.retryButton}>
                Попробовать снова
              </button>
            </div>
          ) : favorites.length > 0 ? (
            <>
              <div className={styles.stats}>
                <span>Найдено заказов: {total}</span>
                <span>Страница {page} из {totalPages}</span>
              </div>

              <div className={styles.grid}>
                {favorites.map((favorite) => (
                  <article key={favorite.id} className={styles.card}>
                    <header className={styles.cardHeader}>
                      <div className={styles.badges}>
                        {renderStatusBadge(favorite.status)}
                        {renderPriorityBadge(favorite.priority)}
                      </div>
                      <button
                        type="button"
                        className={styles.removeButton}
                        onClick={() => handleRemoveFavorite(favorite.order_id)}
                        aria-label="Удалить из избранного"
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
                        </svg>
                      </button>
                    </header>

                    <div className={styles.cardContent}>
                      <h3>{favorite.title}</h3>
                      <p className={styles.description}>{favorite.description}</p>

                      <div className={styles.details}>
                        <div className={styles.detailItem}>
                          <span className={styles.detailLabel}>Цена</span>
                          <span>{formatCurrency(favorite.price, favorite.currency)}</span>
                        </div>
                        <div className={styles.detailItem}>
                          <span className={styles.detailLabel}>Срок</span>
                          <span>{favorite.term} дней</span>
                        </div>
                        <div className={styles.detailItem}>
                          <span className={styles.detailLabel}>Категория</span>
                          <span>{favorite.category_name}</span>
                        </div>
                        <div className={styles.detailItem}>
                          <span className={styles.detailLabel}>Откликов</span>
                          <span>{favorite.responses}</span>
                        </div>
                      </div>
                    </div>

                    <footer className={styles.cardFooter}>
                      <div className={styles.author}>
                        <div className={styles.avatar}>{favorite.customer_name.charAt(0)}</div>
                        <div className={styles.authorDetails}>
                          <h4>{favorite.customer_name}</h4>
                          <p>@{favorite.customer_nickname}</p>
                        </div>
                      </div>
                      <div className={styles.actions}>
                        <Link href={`/orders/${favorite.order_id}`} className={styles.viewButton}>
                          Посмотреть заказ
                        </Link>
                        <span className={styles.favoritedDate}>
                          Добавлено: {formatDate(favorite.favorited_at as unknown as string)}
                        </span>
                      </div>
                    </footer>
                  </article>
                ))}
              </div>

              {totalPages > 1 && (
                <nav className={styles.pagination}>
                  <button
                    type="button"
                    className={styles.pageButton}
                    onClick={() => fetchFavorites(page - 1)}
                    disabled={page <= 1}
                  >
                    Назад
                  </button>
                  <span className={styles.pageInfo}>
                    Страница {page} из {totalPages}
                  </span>
                  <button
                    type="button"
                    className={styles.pageButton}
                    onClick={() => fetchFavorites(page + 1)}
                    disabled={page >= totalPages}
                  >
                    Дальше
                  </button>
                </nav>
              )}
            </>
          ) : (
            <div className={styles.empty}>
              <h3>Избранных заказов пока нет</h3>
              <p>Добавляйте интересные проекты в избранное, чтобы вернуться к ним позже.</p>
              <Link href="/orders" className={styles.viewButton}>
                Перейти к заказам
              </Link>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </>
  )
}
