'use client'

import { useCallback, useEffect, useMemo, useState } from 'react'
import Link from 'next/link'

import Footer from '@/components/layout/Footer'
import Header from '@/components/layout/Header'
import styles from '@/components/portfolio/PortfolioPage.module.css'
import { UserPublicProfileDTO, UsersListResponseDTO } from '@/dto'
import { apiClient } from '@/utils/apiClient'

const CATEGORY_OPTIONS: Array<{ value: string; label: string; specification?: string }> = [
  { value: 'all', label: 'Все категории' },
  { value: 'design', label: 'Дизайн', specification: 'дизайн' },
  { value: 'development', label: 'Программирование', specification: 'программирование' },
  { value: 'writing', label: 'Копирайтинг', specification: 'копирайтинг' },
  { value: 'marketing', label: 'Маркетинг', specification: 'маркетинг' },
  { value: 'video', label: 'Видео', specification: 'видео' },
  { value: 'photo', label: 'Фотографии', specification: 'фотограф' },
  { value: 'business', label: 'Бизнес', specification: 'бизнес' },
]

const PAGE_SIZE = 50

type RoleFilter = 'all' | 'EXECUTOR' | 'CUSTOMER'

const formatNickname = (nickname: string) => (nickname.length > 18 ? `${nickname.slice(0, 18)}…` : nickname)

export default function PortfolioPage() {
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [roleFilter, setRoleFilter] = useState<RoleFilter>('EXECUTOR')
  const [sortBy, setSortBy] = useState('rating')
  const [users, setUsers] = useState<UserPublicProfileDTO[]>([])
  const [totalExecutors, setTotalExecutors] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchUsers = useCallback(async () => {
    setLoading(true)
    setError(null)

    const category = CATEGORY_OPTIONS.find((option) => option.value === selectedCategory)
    const params: Record<string, string | number> = {
      page: 1,
      page_size: PAGE_SIZE,
      min_rating: 0,
    }
    if (category?.specification) {
      params.specification = category.specification
    }
    if (roleFilter !== 'all') {
      params.role = roleFilter
    }

    try {
      const response = await apiClient.get<UsersListResponseDTO>('/users', params)
      const fetchedUsers = response.users ?? []

      const sanitized = fetchedUsers.filter(
        (user) => (user.role ?? '').toUpperCase() !== 'SUPPORT' && user.nickname.toLowerCase() !== 'support',
      )

      const filteredByRole =
        roleFilter === 'all'
          ? sanitized
          : sanitized.filter((user) => (user.role ?? 'CUSTOMER').toUpperCase() === roleFilter)

      setUsers(filteredByRole)
      setTotalExecutors(filteredByRole.length)
    } catch (err) {
      console.warn('Failed to load portfolio users (backend unavailable)', err)
      setError('Не удалось загрузить портфолио исполнителей')
      setUsers([])
      setTotalExecutors(0)
    } finally {
      setLoading(false)
    }
  }, [selectedCategory, roleFilter])

  useEffect(() => {
    fetchUsers()
  }, [fetchUsers])

  const sortedUsers = useMemo(() => {
    const data = [...users]
    return data.sort((a, b) => {
      switch (sortBy) {
        case 'rating':
          return (b.executor_rating ?? 0) - (a.executor_rating ?? 0)
        case 'orders':
          return (b.done_count ?? 0) - (a.done_count ?? 0)
        case 'date':
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        default:
          return 0
      }
    })
  }, [users, sortBy])

  const totalOrders = useMemo(
    () => users.reduce((sum, user) => sum + (user.done_count ?? 0), 0),
    [users],
  )

  const maxRating = useMemo(() => {
    if (users.length === 0) {
      return 0
    }
    return Math.max(...users.map((user) => user.executor_rating ?? 0))
  }, [users])

  const profilesCount = totalExecutors
  const profilesLabel =
    roleFilter === 'EXECUTOR' ? 'исполнителей' : roleFilter === 'CUSTOMER' ? 'заказчиков' : 'пользователей'

  return (
    <>
      <Header />

      <main className={styles.page}>
        <div className={styles.pageHeader}>
          <div className={styles.container}>
            <section className={styles.header}>
            <h1 className={styles.title}>Портфолио исполнителей</h1>
            <p className={styles.subtitle}>Найдите исполнителя под свой проект или вдохновитесь работами коллег.</p>

            <div className={styles.filters}>
              <div className={styles.filterGroup}>
                <label htmlFor="portfolio-category">Категория</label>
                <select
                  id="portfolio-category"
                  className={styles.select}
                  value={selectedCategory}
                  onChange={(event) => setSelectedCategory(event.target.value)}
                >
                  {CATEGORY_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className={styles.filterGroup}>
                <label htmlFor="portfolio-sort">Сортировка</label>
                <select
                  id="portfolio-sort"
                  className={styles.select}
                  value={sortBy}
                  onChange={(event) => setSortBy(event.target.value)}
                >
                  <option value="rating">По рейтингу</option>
                  <option value="orders">По количеству работ</option>
                  <option value="date">По дате регистрации</option>
                </select>
              </div>

              <div className={styles.filterGroup}>
                <label htmlFor="portfolio-role">Тип профиля</label>
                <select
                  id="portfolio-role"
                  className={styles.select}
                  value={roleFilter}
                  onChange={(event) => setRoleFilter(event.target.value as RoleFilter)}
                >
                  <option value="all">Все пользователи</option>
                  <option value="EXECUTOR">Только исполнители</option>
                  <option value="CUSTOMER">Только заказчики</option>
                </select>
              </div>
            </div>
          </section>
          </div>
        </div>

        <div className={styles.container}>
          <section className={styles.stats}>
            <div className={styles.statCard}>
              <span className={styles.statNumber}>{profilesCount}</span>
              <span className={styles.statLabel}>{profilesLabel}</span>
            </div>
            <div className={styles.statCard}>
              <span className={styles.statNumber}>{totalOrders}</span>
              <span className={styles.statLabel}>выполненных заказов</span>
            </div>
            <div className={styles.statCard}>
              <span className={styles.statNumber}>{maxRating.toFixed(1)}</span>
              <span className={styles.statLabel}>максимальный рейтинг</span>
            </div>
          </section>

          {error && (
            <div className={styles.empty}>
              <h3>Не удалось загрузить список исполнителей</h3>
              <p>{error}</p>
            </div>
          )}

          {loading ? (
            <div className={styles.empty}>
              <h3>Загружаем портфолио</h3>
              <p>Пожалуйста, подождите несколько секунд…</p>
            </div>
          ) : sortedUsers.length === 0 && !error ? (
            <div className={styles.empty}>
              <h3>Исполнители не найдены</h3>
              <p>Попробуйте изменить фильтры или загляните позже — новые портфолио появляются каждый день.</p>
            </div>
          ) : (
            <section className={styles.cards}>
              {sortedUsers.map((user) => (
                <article key={user.id} className={styles.card}>
                  <header className={styles.cardHeader}>
                    <div className={styles.avatar}>{user.name.charAt(0)}</div>
                    <div className={styles.badges}>
                      <span className={`${styles.badge} ${styles.badgeRating}`}>Рейтинг: {user.executor_rating.toFixed(1)}</span>
                      {user.phone_verified && <span className={`${styles.badge} ${styles.badgeVerified}`}>Верифицирован</span>}
                    </div>
                  </header>

                  <div className={styles.cardBody}>
                    <div className={styles.nameRow}>
                      <h3 className={styles.name}>{user.name}</h3>
                      <span className={styles.nickname}>@{formatNickname(user.nickname)}</span>
                    </div>
                    <p className={styles.description}>{user.description}</p>

                    <div className={styles.metrics}>
                      <div className={styles.metric}>
                        <span>Специализация</span>
                        <span>{user.specification}</span>
                      </div>
                      <div className={styles.metric}>
                        <span>Выполнено</span>
                        <span>{user.done_count} заказов</span>
                      </div>
                      <div className={styles.metric}>
                        <span>В работе</span>
                        <span>{user.taken_count}</span>
                      </div>
                      <div className={styles.metric}>
                        <span>На платформе</span>
                        <span>{new Date(user.created_at).toLocaleDateString('ru-RU')}</span>
                      </div>
                    </div>
                  </div>

                  <footer className={styles.actions}>
                    <Link href={`/users/${user.nickname}`} className={styles.viewButton}>
                      Посмотреть профиль
                    </Link>
                    <span className={styles.dateLabel}>
                      Добавлен: {new Date(user.created_at).toLocaleDateString('ru-RU')}
                    </span>
                  </footer>
                </article>
              ))}
            </section>
          )}
        </div>
      </main>

      <Footer />
    </>
  )
}