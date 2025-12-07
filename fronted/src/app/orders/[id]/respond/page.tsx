'use client'

import { useEffect, useMemo, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'

import Footer from '@/components/layout/Footer'
import Header from '@/components/layout/Header'
import styles from '@/components/orders/RespondOrderPage.module.css'
import { ChatDTO, MessageDTO, OrderDTO } from '@/dto'
import { useAuth } from '@/providers/AuthProvider'
import { useWebSocketContext } from '@/providers/WebSocketProvider'
import { apiClient } from '@/utils/apiClient'
import { formatCurrency, getCurrencySymbol } from '@/utils/currency'

const MESSAGE_LIMIT = 1000

export default function RespondToOrderPage() {
  const params = useParams()
  const router = useRouter()
  const rawOrderId = params.id

  const { isAuthenticated, user, loading: authLoading } = useAuth()
  const { getChats } = useWebSocketContext()

  const [order, setOrder] = useState<OrderDTO | null>(null)
  const [formData, setFormData] = useState({ message: '', price: '' })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const [errorMessage, setErrorMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [hasExistingResponse, setHasExistingResponse] = useState(false)

  useEffect(() => {
    if (!authLoading && (!isAuthenticated || !user)) {
      router.push('/login')
      return
    }

    const parsedId = Number(rawOrderId)
    if (!Number.isFinite(parsedId) || parsedId <= 0) {
      setLoading(false)
      setOrder(null)
      setErrorMessage('Неверный ID заказа')
      return
    }

    const fetchOrder = async (targetId: number) => {
      try {
        setLoading(true)
        const orderData = await apiClient.get<OrderDTO>(`/orders/${targetId}`)
        setOrder(orderData)

        try {
          const chatsData = await apiClient.get<{ chats: ChatDTO[] } | ChatDTO[]>('/chats/')
          const chats = Array.isArray(chatsData) ? chatsData : chatsData.chats || []
          const existingChat = chats.find(
            (chat) => chat.customer_id === orderData.customer_id && chat.executor_id === Number(user?.id),
          )

          if (existingChat) {
            try {
              const messages = await apiClient.get<MessageDTO[]>(`/chats/${existingChat.id}/messages?after_id=0`)
              const hasOffer = messages.some((msg) => msg.type === 'offer' && msg.order_id === targetId)
              if (hasOffer) {
                setHasExistingResponse(true)
              }
            } catch {
              setHasExistingResponse(true)
            }
          }
        } catch (chatError) {
          console.log('Could not verify existing responses:', chatError)
        }
      } catch (fetchError) {
        console.error('Error fetching order:', fetchError)
        setOrder(null)
        setErrorMessage('Ошибка загрузки заказа')
      } finally {
        setLoading(false)
      }
    }

    if (isAuthenticated && user) {
      fetchOrder(parsedId)
    }
  }, [authLoading, isAuthenticated, rawOrderId, router, user])

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = event.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()

    if (!isAuthenticated) {
      router.push('/login')
      return
    }

    setIsSubmitting(true)
    setSubmitStatus('idle')
    setErrorMessage('')

    try {
      const response = await apiClient.post<{ success: boolean; chat_id: number }>(
        `/orders/${Number(rawOrderId)}/respond`,
        {
          message: formData.message,
          price: parseFloat(formData.price),
        },
      )

      setSubmitStatus('success')
      setTimeout(() => {
        getChats()
      }, 500)

      setTimeout(() => {
        router.push(response.chat_id ? `/chats?chat_id=${response.chat_id}` : '/chats')
      }, 2000)
    } catch (submitError: unknown) {
      setSubmitStatus('error')
      if (submitError instanceof Error) {
        setErrorMessage(submitError.message)
      } else if (typeof submitError === 'string') {
        setErrorMessage(submitError)
      } else {
        setErrorMessage('Ошибка отправки отклика')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCancel = () => {
    const parsedId = Number(rawOrderId)
    router.push(Number.isFinite(parsedId) && parsedId > 0 ? `/orders/${parsedId}` : '/orders')
  }

  if (loading || authLoading) {
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

  if (!order) {
    return (
      <>
        <Header />
        <main className={styles.page}>
          <div className={styles.container}>
            <div className={styles.error}>
              <h1>Заказ не найден</h1>
              <p>Возможно, заказ удалён или у вас нет доступа.</p>
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
            <button type="button" onClick={() => router.push(`/orders/${Number(rawOrderId)}`)} className={styles.backButton}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M19 12H5M12 19l-7-7 7-7" />
              </svg>
              Назад к заказу
            </button>
            <h1 className={styles.title}>Отклик на заказ</h1>
            <p className={styles.subtitle}>Опишите предложение и укажите цену за выполнение задачи</p>
          </header>

          {hasExistingResponse && (
            <section className={styles.warning}>
              <div className={styles.warningIcon}>⚠️</div>
              <div>
                <h3 className={styles.sectionTitle}>Вы уже откликались на этот заказ</h3>
                <p>Можно проверить чат с заказчиком или вернуться к карточке заказа.</p>
                <div className={styles.warningActions}>
                  <button type="button" onClick={() => router.push('/chats')} className={styles.primaryButton}>
                    Перейти к чатам
                  </button>
                  <button type="button" onClick={() => router.push(`/orders/${Number(rawOrderId)}`)} className={styles.secondaryButton}>
                    Вернуться к заказу
                  </button>
                </div>
              </div>
            </section>
          )}

          <section className={styles.layout}>
            <div className={styles.summary}>
              <article className={styles.summaryCard}>
                <h3 className={styles.summaryTitle}>Информация о заказе</h3>
                <p className={styles.summaryDescription}>{order.description}</p>
                <div className={styles.summaryDetails}>
                  <div className={styles.summaryItem}>
                    <span className={styles.summaryLabel}>Название</span>
                    <span className={styles.summaryValue}>{order.title}</span>
                  </div>
                  <div className={styles.summaryItem}>
                    <span className={styles.summaryLabel}>Бюджет</span>
                    <span className={styles.summaryValue}>{formatCurrency(order.price, order.currency)}</span>
                  </div>
                  <div className={styles.summaryItem}>
                    <span className={styles.summaryLabel}>Срок</span>
                    <span className={styles.summaryValue}>{order.term} дней</span>
                  </div>
                  <div className={styles.summaryItem}>
                    <span className={styles.summaryLabel}>Категория</span>
                    <span className={styles.summaryValue}>{order.category_name}</span>
                  </div>
                  <div className={styles.summaryItem}>
                    <span className={styles.summaryLabel}>Заказчик</span>
                    <span className={styles.summaryValue}>{order.customer_name}</span>
                  </div>
                </div>
              </article>
            </div>

            <div className={styles.sidebar}>
              <div className={styles.tipsCard}>
                <h4>💡 Советы для отклика</h4>
                <ul className={styles.tipsList}>
                  <li>Опишите релевантный опыт и проекты</li>
                  <li>Укажите шаги решения и сроки</li>
                  <li>Предложите разумную цену и условия</li>
                  <li>Формулируйте вежливо и профессионально</li>
                  <li>Задайте уточняющие вопросы, если нужно</li>
                </ul>
              </div>

              <div className={styles.commissionCard}>
                <h4>💰 Комиссия платформы</h4>
                <p>С заказчика: 5% от суммы заказа</p>
                <p>С исполнителя: 5% от суммы заказа</p>
                <p className={styles.note}>Комиссия списывается только после успешного завершения проекта</p>
              </div>
            </div>
          </section>

          <section className={styles.formWrapper}>
            {submitStatus === 'success' && (
              <div className={`${styles.statusMessage} ${styles.statusSuccess}`}>
                ✅ Отклик отправлен! Скоро перенаправим вас в чат.
              </div>
            )}
            {submitStatus === 'error' && (
              <div className={`${styles.statusMessage} ${styles.statusError}`}>❌ {errorMessage}</div>
            )}

            <form onSubmit={handleSubmit} className={styles.formSection}>
              <div className={styles.field}>
                <label className={styles.label} htmlFor="message">
                  Сообщение заказчику *
                </label>
                <textarea
                  id="message"
                  name="message"
                  className={styles.textarea}
                  value={formData.message}
                  onChange={handleInputChange}
                  placeholder="Опишите ваш подход, опыт и почему вы подходите для проекта"
                  rows={6}
                  maxLength={MESSAGE_LIMIT}
                  required
                  disabled={isSubmitting}
                />
                <span className={styles.charCount}>
                  {formData.message.length}/{MESSAGE_LIMIT}
                </span>
              </div>

              <div className={styles.field}>
                <label className={styles.label} htmlFor="price">
                  Ваша цена ({getCurrencySymbol(order.currency)}) *
                </label>
                <input
                  id="price"
                  name="price"
                  type="number"
                  className={styles.input}
                  value={formData.price}
                  onChange={handleInputChange}
                  placeholder="Введите вашу стоимость"
                  min={1}
                  required
                  disabled={isSubmitting}
                />
                <span className={styles.hint}>Комиссия платформы: 5% от суммы заказа</span>
              </div>

              <div className={styles.actions}>
                <button
                  type="button"
                  onClick={handleCancel}
                  className={styles.cancelButton}
                  disabled={isSubmitting}
                >
                  Отмена
                </button>
                <button type="submit" className={styles.submitButton} disabled={isSubmitting}>
                  <span>{isSubmitting ? 'Отправка…' : 'Отправить отклик'}</span>
                  {!isSubmitting && (
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M5 12h14M12 5l7 7-7 7" />
                    </svg>
                  )}
                </button>
              </div>
            </form>
          </section>
        </div>
      </main>

      <Footer />
    </>
  )
}
