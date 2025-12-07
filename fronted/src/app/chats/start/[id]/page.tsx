'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'

import Footer from '@/components/layout/Footer'
import Header from '@/components/layout/Header'
import styles from '@/components/chats/StartChatPage.module.css'
import { useAuth } from '@/providers/AuthProvider'
import { useWebSocketContext } from '@/providers/WebSocketProvider'

export default function StartChatPage() {
  const params = useParams()
  const router = useRouter()
  const { user, isAuthenticated, loading: authLoading } = useAuth()
  const { sendUserMessage } = useWebSocketContext()
  const [newMessage, setNewMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const targetUserId = Number(params.id)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, authLoading, router])

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !user || !Number.isFinite(targetUserId) || targetUserId <= 0) {
      return
    }

    try {
      setLoading(true)
      setError(null)

      const success = sendUserMessage(targetUserId, newMessage)
      if (success) {
        setNewMessage('')
        router.push('/chats')
      } else {
        setError('Не удалось отправить сообщение')
      }
    } catch (sendError) {
      console.error('Error sending message:', sendError)
      setError('Ошибка при отправке сообщения')
    } finally {
      setLoading(false)
    }
  }

  if (authLoading) {
    return (
      <>
        <Header />
        <main className={styles.page}>
          <div className={styles.loading}>
            <div className={styles.spinner} />
            <p>Загрузка…</p>
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
        <div className={styles.card}>
          <header className={styles.header}>
            <h1 className={styles.title}>Написать сообщение</h1>
            <p className={styles.subtitle}>Начните общение с участником платформы</p>
          </header>

          <div className={styles.form}>
            <div className={styles.field}>
              <label htmlFor="message" className={styles.label}>
                Ваше сообщение:
              </label>
              <textarea
                id="message"
                className={styles.textarea}
                value={newMessage}
                onChange={(event) => setNewMessage(event.target.value)}
                placeholder="Введите текст сообщения…"
                rows={4}
                disabled={loading}
              />
            </div>

            {error && <div className={styles.error}>{error}</div>}

            <div className={styles.actions}>
              <button type="button" onClick={() => router.back()} className={styles.buttonSecondary} disabled={loading}>
                Назад
              </button>
              <button
                type="button"
                onClick={handleSendMessage}
                className={styles.buttonPrimary}
                disabled={!newMessage.trim() || loading}
              >
                {loading ? 'Отправка…' : 'Отправить сообщение'}
              </button>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </>
  )
}
