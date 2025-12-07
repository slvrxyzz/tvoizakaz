'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

import styles from '@/components/admin/SupportPage.module.css'
import { useAuth } from '@/providers/AuthProvider'

interface ContactRequest {
  id: number
  name: string
  email: string
  message: string
  status: 'pending' | 'answered'
  created_at: string
}

export default function SupportPage() {
  const router = useRouter()
  const { user, isAuthenticated, loading: authLoading, logout } = useAuth()
  const [contactRequests, setContactRequests] = useState<ContactRequest[]>([])
  const [broadcastMessage, setBroadcastMessage] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (authLoading) {
      return
    }
    if (!isAuthenticated || !user?.admin_verified) {
      router.push('/admin/login')
      return
    }
    loadContactRequests().catch((error) => console.error('Error loading contact requests:', error))
  }, [authLoading, isAuthenticated, user, router])

  const loadContactRequests = async () => {
    try {
      const response = await fetch('/api/admin/support/requests', {
        credentials: 'include',
      })
      if (response.ok) {
        const data = await response.json()
        setContactRequests(Array.isArray(data?.data) ? data.data : [])
      }
    } catch (error) {
      console.error('Error loading contact requests:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCloseRequest = async (requestId: number) => {
    try {
      const response = await fetch(`/api/admin/support/requests/${requestId}/close`, {
        method: 'POST',
        credentials: 'include',
      })

      if (response.ok) {
        setContactRequests(prev =>
          prev.map(req =>
            req.id === requestId ? { ...req, status: 'answered' as const } : req
          )
        )
      }
    } catch (error) {
      console.error('Error closing request:', error)
    }
  }

  const handleBroadcast = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!broadcastMessage.trim()) return

    try {
      const response = await fetch('/api/admin/support/broadcast', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: broadcastMessage }),
        credentials: 'include',
      })

      if (response.ok) {
        alert('Сообщение отправлено всем пользователям!')
        setBroadcastMessage('')
      } else {
        alert('Ошибка при отправке сообщения')
      }
    } catch (error) {
      console.error('Error sending broadcast:', error)
      alert('Ошибка при отправке сообщения')
    }
  }

  if (isLoading) {
    return (
      <div className={styles.page}>
        <div className={styles.loading}>Загрузка…</div>
      </div>
    )
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>Служба поддержки</h1>
        <nav className={styles.nav}>
          <Link href="/admin" className={styles.navLink}>
            ← В админку
          </Link>
          <Link href="/admin/commission" className={styles.navLink}>
            Комиссии
          </Link>
          <Link href="/admin/content" className={styles.navLink}>
            Контент
          </Link>
          <button
            type="button"
            onClick={() => {
              void logout()
              router.push('/admin/login')
            }}
            className={styles.logoutButton}
          >
            Выйти
          </button>
        </nav>
      </header>

      <section className={styles.content}>
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Обращения пользователей</h2>
          <div className={styles.tableWrapper}>
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Имя</th>
                  <th>Email</th>
                  <th>Сообщение</th>
                  <th>Статус</th>
                  <th>Дата</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                {contactRequests.map((request) => (
                  <tr key={request.id}>
                    <td>{request.name}</td>
                    <td>{request.email}</td>
                    <td className={styles.messageCell}>{request.message}</td>
                    <td>
                      <span
                        className={`${styles.statusBadge} ${
                          request.status === 'answered' ? styles.statusAnswered : styles.statusPending
                        }`}
                      >
                        {request.status === 'answered' ? 'Ответ дан' : 'Ожидает ответа'}
                      </span>
                    </td>
                    <td>
                      {new Date(request.created_at).toLocaleDateString('ru-RU', {
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </td>
                    <td>
                      {request.status !== 'answered' && (
                        <button
                          type="button"
                          onClick={() => handleCloseRequest(request.id)}
                          className={styles.closeButton}
                        >
                          Закрыть
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Рассылка сообщения всем пользователям</h2>
          <form onSubmit={handleBroadcast} className={styles.broadcastForm}>
            <textarea
              className={styles.broadcastTextarea}
              value={broadcastMessage}
              onChange={(event) => setBroadcastMessage(event.target.value)}
              placeholder="Введите сообщение для рассылки…"
              required
              maxLength={1000}
              rows={4}
            />
            <div className={styles.charCount}>{broadcastMessage.length}/1000 символов</div>
            <button type="submit" className={styles.broadcastButton}>
              Отправить сообщение
            </button>
          </form>
        </section>
      </section>
    </div>
  )
}