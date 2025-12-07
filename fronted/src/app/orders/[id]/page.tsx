'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'

import ChatButton from '@/components/ChatButton'
import Footer from '@/components/layout/Footer'
import Header from '@/components/layout/Header'
import styles from '@/components/orders/OrderPage.module.css'
import { OrderDTO, OrderPriority, OrderStatus } from '@/dto'
import { useFavoriteStatus } from '@/hooks/useFavorites'
import { apiClient } from '@/utils/apiClient'
import { formatCurrency } from '@/utils/currency'

const STATUS_STYLES: Record<OrderStatus, { text: string; className: string }> = {
  [OrderStatus.OPEN]: { text: 'Открыт', className: styles.statusOpen },
  [OrderStatus.WORK]: { text: 'В работе', className: styles.statusWork },
  [OrderStatus.REVIEW]: { text: 'На проверке', className: styles.statusReview },
  [OrderStatus.CLOSE]: { text: 'Закрыт', className: styles.statusClose },
}

const PRIORITY_STYLES: Record<OrderPriority, { text: string; className: string }> = {
  [OrderPriority.LOW]: { text: 'Низкий', className: styles.priorityBase },
  [OrderPriority.NORMAL]: { text: 'Обычный', className: styles.priorityBase },
  [OrderPriority.HIGH]: { text: 'Высокий', className: styles.priorityPremium },
  [OrderPriority.URGENT]: { text: 'Срочный', className: styles.priorityExpress },
}

export default function OrderPage() {
  const params = useParams()
  const router = useRouter()
  const [order, setOrder] = useState<OrderDTO | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const { isFavorite, favoriteCount, loading: favoriteLoading, toggleFavorite } = useFavoriteStatus(order?.id || -1)

  useEffect(() => {
    const fetchOrder = async (targetId: number) => {
      try {
        setLoading(true)
        setError(null)
        const orderData = await apiClient.get<OrderDTO>(`/orders/${targetId}`)
        setOrder(orderData)
      } catch (fetchError) {
        console.error('Error fetching order:', fetchError)
        setError('Ошибка загрузки заказа')
      } finally {
        setLoading(false)
      }
    }

    if (!params.id) {
      setLoading(false)
      setError('Неверный ID заказа')
      return
    }

    const idStr = String(params.id)
    if (idStr.startsWith('create')) {
      router.push('/orders/create')
      return
    }

    const parsedId = Number(idStr)
    if (!Number.isFinite(parsedId) || parsedId <= 0) {
      setLoading(false)
      setError('Неверный ID заказа')
      return
    }

    fetchOrder(parsedId)
  }, [params.id, router])

  const formatDate = (dateString: string) => new Date(dateString).toLocaleDateString('ru-RU')

  const renderStatusBadge = (status: OrderStatus) => {
    const config = STATUS_STYLES[status] ?? { text: status, className: styles.statusDefault }
    return <span className={`${styles.statusBadge} ${config.className}`}>{config.text}</span>
  }

  const renderPriorityBadge = (priority: OrderPriority) => {
    const config = PRIORITY_STYLES[priority] ?? { text: priority, className: styles.priorityDefault }
    return <span className={`${styles.priorityBadge} ${config.className}`}>{config.text}</span>
  }

  if (loading) {
    return (
      <>
        <Header />
        <main className={styles.page}>
          <div className={styles.container}>
            <div className={styles.loading}>
              <div className={styles.spinner} />
              <p>Загрузка заказа…</p>
            </div>
          </div>
        </main>
        <Footer />
      </>
    )
  }

  if (error || !order) {
    return (
      <>
        <Header />
        <main className={styles.page}>
          <div className={styles.container}>
            <div className={styles.error}>
              <h3>Ошибка загрузки</h3>
              <p>{error || 'Заказ не найден'}</p>
              <button type="button" onClick={() => router.push('/orders')} className={styles.retryButton}>
                Вернуться к заказам
              </button>
            </div>
          </div>
        </main>
        <Footer />
      </>
    )
  }

  return (
    <>
      <Header />

      <main className={styles.page}>
        <div className={styles.container}>
          <header className={styles.header}>
            <button type="button" onClick={() => router.back()} className={styles.backButton}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M19 12H5M12 19l-7-7 7-7" />
              </svg>
              Назад
            </button>

            <div className={styles.badges}>
              {renderStatusBadge(order.status)}
              {renderPriorityBadge(order.priority)}
            </div>
          </header>

          <section className={styles.content}>
            <article className={styles.mainCard}>
              <div className={styles.cardHeader}>
                <h1 className={styles.title}>{order.title}</h1>
                <span className={styles.price}>{formatCurrency(order.price, order.currency)}</span>
              </div>

              <div className={styles.cardContent}>
                <section>
                  <h2 className={styles.sectionTitle}>Описание заказа</h2>
                  <p className={styles.description}>{order.description}</p>
                </section>

                <section>
                  <h2 className={styles.sectionTitle}>Детали</h2>
                  <div className={styles.details}>
                    <div className={styles.detailItem}>
                      <span className={styles.detailLabel}>Срок выполнения</span>
                      <span className={styles.detailValue}>{order.term} дней</span>
                    </div>
                    <div className={styles.detailItem}>
                      <span className={styles.detailLabel}>Категория</span>
                      <span className={styles.detailValue}>{order.category_name}</span>
                    </div>
                    <div className={styles.detailItem}>
                      <span className={styles.detailLabel}>Откликов</span>
                      <span className={styles.detailValue}>{order.responses}</span>
                    </div>
                    <div className={styles.detailItem}>
                      <span className={styles.detailLabel}>Дата создания</span>
                      <span className={styles.detailValue}>{formatDate(order.created_at)}</span>
                    </div>
                  </div>
                </section>
              </div>

              <footer className={styles.cardFooter}>
                <div className={styles.authorRow}>
                  <div className={styles.authorInfo}>
                    <div className={styles.authorAvatar}>{order.customer_name.charAt(0)}</div>
                    <div className={styles.authorDetails}>
                      <h4>{order.customer_name}</h4>
                      <p>@{order.customer_nickname}</p>
                    </div>
                  </div>
                  <span className={styles.authorRating}>⭐ 4.8</span>
                </div>
              </footer>
            </article>

            <aside className={styles.sidebar}>
              <div className={styles.sidebarCard}>
                <h3 className={styles.sidebarTitle}>Действия</h3>
                <div className={styles.actionList}>
                  {order.status === OrderStatus.OPEN && (
                    <button
                      type="button"
                      className={`${styles.actionButton} ${styles.actionPrimary}`}
                      onClick={() => router.push(`/orders/${order.id}/respond`)}
                    >
                      Откликнуться на заказ
                    </button>
                  )}

                  <ChatButton
                    orderId={order.id}
                    customerId={order.customer_id}
                    customerName={order.customer_name}
                    customerNickname={order.customer_nickname}
                    className={`${styles.actionButton} ${styles.actionChat}`}
                  />

                  <button
                    type="button"
                    className={`${styles.actionButton} ${isFavorite ? styles.actionFavorite : styles.actionSecondary}`}
                    onClick={toggleFavorite}
                    disabled={favoriteLoading}
                  >
                    {favoriteLoading ? (
                      <>
                        <div className={styles.spinnerSmall} />
                        <span>Загрузка…</span>
                      </>
                    ) : (
                      <>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
                        </svg>
                        <span>{isFavorite ? 'В избранном' : 'Добавить в избранное'}</span>
                      </>
                    )}
                  </button>
                  {favoriteCount > 0 && (
                    <span className={styles.detailLabel}>В избранном у {favoriteCount} пользователей</span>
                  )}
                </div>
              </div>

              <div className={styles.sidebarCard}>
                <h3 className={styles.sidebarTitle}>Информация о заказчике</h3>
                <div className={styles.customerInfo}>
                  <div className={styles.customerAvatar}>{order.customer_name.charAt(0)}</div>
                  <div className={styles.customerDetails}>
                    <h4>{order.customer_name}</h4>
                    <p>@{order.customer_nickname}</p>
                    <div className={styles.customerStats}>
                      <span>Рейтинг: 4.8</span>
                      <span>Заказов: 15</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className={styles.sidebarCard}>
                <h3 className={styles.sidebarTitle}>Безопасность</h3>
                <div className={styles.securityList}>
                  <div className={styles.securityItem}>
                    <span className={styles.securityIcon}>🛡️</span>
                    <span>Безопасная сделка</span>
                  </div>
                  <div className={styles.securityItem}>
                    <span className={styles.securityIcon}>💰</span>
                    <span>Гарантия возврата</span>
                  </div>
                  <div className={styles.securityItem}>
                    <span className={styles.securityIcon}>⚖️</span>
                    <span>Арбитраж споров</span>
                  </div>
                </div>
              </div>
            </aside>
          </section>
        </div>
      </main>

      <Footer />
    </>
  )
}

