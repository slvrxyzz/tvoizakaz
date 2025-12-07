'use client'
import { useEffect, useMemo, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

import styles from '@/components/admin/AdminPage.module.css'
import { useAuth } from '@/providers/AuthProvider'
import { formatCurrency } from '@/utils/currency'

interface User {
  id: number
  name: string
  nickname: string
  email: string
  admin_verified: boolean
  balance: number
  rub_balance: number
  tf_balance: number
  role: string
  customer_rating: number
  executor_rating: number
  is_support: boolean
}

interface Order {
  id: number
  title: string
  description: string
  price: number
  currency: string
  status: string
  priority: string
  customer_id: number
  customer_name: string
  customer_nickname: string
  executor_id: number | null
  executor_name?: string | null
  executor_nickname?: string | null
}

interface Offer {
  id: number
  text: string
  order_id: number | null
  order_title?: string | null
  chat_id: number
  sender_id: number
  sender_nickname?: string | null
  created_at: string
}

type SqlResult = Record<string, unknown>

export default function AdminPanel() {
  const router = useRouter()
  const { user, loading, logout } = useAuth()
  const [activeTab, setActiveTab] = useState<'users' | 'orders' | 'offers' | 'sql'>('users')
  const [sqlQuery, setSqlQuery] = useState('')
  const [sqlResult, setSqlResult] = useState<SqlResult[] | null>(null)
  const [sqlError, setSqlError] = useState('')
  const [sqlRowsAffected, setSqlRowsAffected] = useState<number | null>(null)

const ROLE_OPTIONS = ['ADMIN', 'SUPPORT', 'EDITOR', 'CUSTOMER', 'EXECUTOR']
const ROLE_LABELS: Record<string, string> = {
  ADMIN: 'Админ',
  SUPPORT: 'Тех поддержка',
  EDITOR: 'Публикует статьи',
  CUSTOMER: 'Заказчик',
  EXECUTOR: 'Исполнитель',
}
  
  // Данные с пагинацией
  const [users, setUsers] = useState<User[]>([])
  const [orders, setOrders] = useState<Order[]>([])
  const [offers, setOffers] = useState<Offer[]>([])
  
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage] = useState(10)
  const [totalItems, setTotalItems] = useState(0)

  const isAdmin = user?.admin_verified

  useEffect(() => {
    if (loading) {
      return
    }
    if (!user) {
      router.push('/admin/login')
      return
    }
    if (!isAdmin) {
      router.push('/')
      return
    }
    void loadData()
  }, [loading, user, isAdmin, router, currentPage, activeTab])

  useEffect(() => {
    setCurrentPage(1)
  }, [activeTab])

  const loadData = async () => {
    try {
      const response = await fetch(`/api/admin/data?page=${currentPage}&limit=${itemsPerPage}&type=${activeTab}`, {
        credentials: 'include',
      })
      const data = await response.json().catch(() => null)

      if (!response.ok) {
        console.error('Failed to load admin data', data)
        return
      }

      const items = Array.isArray(data?.data) ? data.data : []
      const total = typeof data?.total === 'number' ? data.total : 0
      setTotalItems(total)

      switch (activeTab) {
        case 'users':
          setUsers(
            (items as User[]).map((userItem) => ({
              ...userItem,
              role: (userItem.role ?? 'CUSTOMER').toUpperCase(),
              rub_balance: userItem.rub_balance ?? userItem.balance ?? 0,
              tf_balance: userItem.tf_balance ?? 0,
            }))
          )
          break
        case 'orders':
          setOrders(
            (items as Order[]).map((orderItem) => ({
              ...orderItem,
              currency: (orderItem.currency ?? 'RUB').toUpperCase(),
            }))
          )
          break
        case 'offers':
          setOffers(items as Offer[])
          break
      }
    } catch (error) {
      console.error('Error loading data:', error)
    }
  }

  const executeSql = async () => {
    if (!sqlQuery.trim()) {
      setSqlError('Пожалуйста, введите SQL запрос')
      return
    }

    try {
      const response = await fetch('/api/admin/sql', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: sqlQuery }),
      })

      const data = await response.json().catch(() => null)

      if (response.ok && data) {
        const resultRows = Array.isArray(data.result) ? data.result : []
        setSqlResult(resultRows)
        setSqlRowsAffected(typeof data.rows_affected === 'number' ? data.rows_affected : null)
        setSqlError('')
      } else {
        setSqlError(data?.detail || 'Ошибка выполнения запроса')
        setSqlResult(null)
        setSqlRowsAffected(null)
      }
    } catch (error) {
      setSqlError('Ошибка сети: ' + (error as Error).message)
      setSqlResult(null)
      setSqlRowsAffected(null)
    }
  }

  const handleUserEdit = async (userId: number, payload: Partial<User>) => {
    if (!payload || Object.keys(payload).length === 0) {
      return
    }

    try {
      const response = await fetch(`/api/admin/users/${userId}`, {
        method: 'PUT',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (response.ok) {
        await loadData()
      }
    } catch (error) {
      console.error('Error updating user:', error)
    }
  }

  const handleUserDelete = async (userId: number) => {
    if (!confirm('Удалить пользователя?')) return

    try {
      const response = await fetch(`/api/admin/users/${userId}`, {
        method: 'DELETE',
        credentials: 'include',
      })

      if (response.ok) {
        await loadData()
      }
    } catch (error) {
      console.error('Error deleting user:', error)
    }
  }

  const handleOrderDelete = async (orderId: number) => {
    if (!confirm('Удалить заказ?')) return

    try {
      const response = await fetch(`/api/admin/orders/${orderId}`, {
        method: 'DELETE',
        credentials: 'include',
      })

      if (response.ok) {
        await loadData()
      }
    } catch (error) {
      console.error('Error deleting order:', error)
    }
  }

  const handleOfferDelete = async (offerId: number) => {
    if (!confirm('Удалить оффер?')) return

    try {
      const response = await fetch(`/api/admin/offers/${offerId}`, {
        method: 'DELETE',
        credentials: 'include',
      })

      if (response.ok) {
        await loadData()
      }
    } catch (error) {
      console.error('Error deleting offer:', error)
    }
  }

  const totalPages = useMemo(() => Math.max(1, Math.ceil(totalItems / itemsPerPage)), [totalItems, itemsPerPage])

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>Админ-панель</h1>
        <nav className={styles.nav}>
          <Link href="/admin/commission" className={styles.navLink}>
            Настройки комиссий
          </Link>
          <Link href="/admin/support" className={styles.navLink}>
            Поддержка
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
        <div className={styles.tabs}>
          <button
            type="button"
            className={`${styles.tabButton} ${activeTab === 'users' ? styles.tabActive : ''}`}
            onClick={() => setActiveTab('users')}
          >
            Пользователи
          </button>
          <button
            type="button"
            className={`${styles.tabButton} ${activeTab === 'orders' ? styles.tabActive : ''}`}
            onClick={() => setActiveTab('orders')}
          >
            Заказы
          </button>
          <button
            type="button"
            className={`${styles.tabButton} ${activeTab === 'offers' ? styles.tabActive : ''}`}
            onClick={() => setActiveTab('offers')}
          >
            Офферы
          </button>
          <button
            type="button"
            className={`${styles.tabButton} ${activeTab === 'sql' ? styles.tabActive : ''}`}
            onClick={() => setActiveTab('sql')}
          >
            SQL запросы
          </button>
        </div>

        <div>
          {activeTab === 'users' && (
            <div className={styles.tableWrapper}>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Имя</th>
                    <th>Ник</th>
                    <th>Email</th>
                    <th>Роль</th>
                    <th>Верификация</th>
                    <th>Баланс ₽</th>
                    <th>Баланс TF</th>
                    <th>Рейтинг</th>
                    <th>Действия</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td>{user.id}</td>
                      <td>
                        <input
                          className={styles.inlineInput}
                          type="text"
                          defaultValue={user.name}
                          onBlur={(event) => {
                            handleUserEdit(user.id, { name: event.target.value })
                          }}
                        />
                      </td>
                      <td>
                        <input
                          className={styles.inlineInput}
                          type="text"
                          defaultValue={user.nickname}
                          onBlur={(event) => {
                            handleUserEdit(user.id, { nickname: event.target.value })
                          }}
                        />
                      </td>
                      <td>
                        <input
                          className={styles.inlineInput}
                          type="email"
                          defaultValue={user.email}
                          onBlur={(event) => {
                            handleUserEdit(user.id, { email: event.target.value })
                          }}
                        />
                      </td>
                      <td>
                        <select
                          className={styles.inlineInput}
                          defaultValue={user.role}
                          onChange={(event) => handleUserEdit(user.id, { role: event.target.value })}
                        >
                          {ROLE_OPTIONS.map((role) => (
                            <option key={role} value={role}>
                              {ROLE_LABELS[role] ?? role}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td>
                        {!user.admin_verified ? (
                          <button
                            type="button"
                            className={styles.verifyButton}
                            onClick={() => handleUserEdit(user.id, { admin_verified: true })}
                          >
                            Подтвердить
                          </button>
                        ) : (
                          'Подтверждён'
                        )}
                      </td>
                      <td>
                        <input
                          className={styles.inlineInput}
                          type="number"
                          step="0.01"
                          defaultValue={user.rub_balance ?? user.balance}
                          onBlur={(event) => {
                            const raw = event.target.value.trim()
                            if (!raw) {
                              return
                            }
                            const value = Number(raw)
                            if (Number.isNaN(value)) {
                              return
                            }
                            handleUserEdit(user.id, { rub_balance: value })
                          }}
                        />
                      </td>
                      <td>
                        <input
                          className={styles.inlineInput}
                          type="number"
                          step="0.01"
                          defaultValue={user.tf_balance ?? 0}
                          onBlur={(event) => {
                            const raw = event.target.value.trim()
                            if (!raw) {
                              return
                            }
                            const value = Number(raw)
                            if (Number.isNaN(value)) {
                              return
                            }
                            handleUserEdit(user.id, { tf_balance: value })
                          }}
                        />
                      </td>
                      <td>
                        <input
                          className={styles.inlineInput}
                          type="number"
                          step="0.01"
                          defaultValue={user.customer_rating}
                          onBlur={(event) => {
                            const raw = event.target.value.trim()
                            if (!raw) {
                              return
                            }
                            const value = Number(raw)
                            if (Number.isNaN(value)) {
                              return
                            }
                            handleUserEdit(user.id, { customer_rating: value })
                          }}
                        />
                      </td>
                      <td>
                        <button
                          type="button"
                          className={styles.deleteButton}
                          onClick={() => handleUserDelete(user.id)}
                        >
                          Удалить
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'orders' && (
            <div className={styles.tableWrapper}>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Название</th>
                    <th>Описание</th>
                    <th>Цена</th>
                    <th>Статус</th>
                    <th>Приоритет</th>
                    <th>Заказчик</th>
                    <th>Исполнитель</th>
                    <th>Действия</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map((order) => (
                    <tr key={order.id}>
                      <td>{order.id}</td>
                      <td>{order.title}</td>
                      <td className={styles.messageCell}>{order.description}</td>
                      <td>{formatCurrency(order.price, order.currency)}</td>
                      <td>{order.status}</td>
                      <td>{order.priority}</td>
                      <td>
                        {order.customer_name} ({order.customer_nickname})
                      </td>
                      <td>
                        {order.executor_id
                          ? `${order.executor_name ?? order.executor_id} (${order.executor_nickname ?? '—'})`
                          : '—'}
                      </td>
                      <td>
                        <button
                          type="button"
                          className={styles.deleteButton}
                          onClick={() => handleOrderDelete(order.id)}
                        >
                          Удалить
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'offers' && (
            <div className={styles.tableWrapper}>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Текст</th>
                    <th>Заказ</th>
                    <th>ID чата</th>
                    <th>ID отправителя</th>
                    <th>Отправитель</th>
                    <th>Дата</th>
                    <th>Действия</th>
                  </tr>
                </thead>
                <tbody>
                  {offers.map((offer) => (
                    <tr key={offer.id}>
                      <td>{offer.id}</td>
                      <td className={styles.messageCell}>{offer.text}</td>
                      <td>{offer.order_title ?? offer.order_id ?? '—'}</td>
                      <td>{offer.chat_id}</td>
                      <td>{offer.sender_id}</td>
                      <td>{offer.sender_nickname ?? '—'}</td>
                      <td>{new Date(offer.created_at).toLocaleDateString('ru-RU')}</td>
                      <td>
                        <button
                          type="button"
                          className={styles.deleteButton}
                          onClick={() => handleOfferDelete(offer.id)}
                        >
                          Удалить
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'sql' && (
            <div className={styles.sqlWrapper}>
              <textarea
                className={styles.sqlEditor}
                value={sqlQuery}
                onChange={(event) => setSqlQuery(event.target.value)}
                placeholder="Введите SQL запрос…"
              />
              <button type="button" onClick={executeSql} className={styles.sqlExecute}>
                Выполнить
              </button>
              {sqlError && <div className={styles.sqlError}>{sqlError}</div>}
              {sqlResult && (
                <div className={styles.sqlResult}>
                  <h3>Результат</h3>
                  {sqlRowsAffected !== null && (
                    <div className={styles.sqlMeta}>Затронуто строк: {sqlRowsAffected}</div>
                  )}
                  {sqlResult.length === 0 ? (
                    <p>Запрос выполнен успешно. Результат отсутствует.</p>
                  ) : (
                    <div className={styles.resultTable}>
                      <table>
                        <thead>
                          <tr>
                            {Object.keys(sqlResult[0]).map((key) => (
                              <th key={key}>{key}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {sqlResult.map((row, index) => (
                            <tr key={index}>
                              {Object.values(row).map((value, cellIndex) => (
                                <td key={cellIndex}>{value !== null ? String(value) : 'NULL'}</td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {activeTab !== 'sql' && (
          <div className={styles.pagination}>
            <button
              type="button"
              onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
              className={styles.paginationButton}
            >
              ← Назад
            </button>
            <span className={styles.pageInfo}>
              Страница {currentPage} из {totalPages}
            </span>
            <button
              type="button"
              onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
              className={styles.paginationButton}
            >
              Вперёд →
            </button>
          </div>
        )}
      </section>
    </div>
  )
}