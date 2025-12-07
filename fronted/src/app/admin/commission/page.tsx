'use client'
import { useCallback, useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

import styles from '@/components/admin/CommissionPage.module.css'
import { useAuth } from '@/providers/AuthProvider'

interface CommissionSettings {
  commission_withdraw: number
  commission_customer: number
  commission_executor: number
  commission_post_order: number
  commission_response_threshold: number
  commission_response_percent: number
}

export default function CommissionSettings() {
  const router = useRouter()
  const { user, isAuthenticated, loading: authLoading, logout } = useAuth()
  const [settings, setSettings] = useState<CommissionSettings>({
    commission_withdraw: 3,
    commission_customer: 10,
    commission_executor: 5,
    commission_post_order: 200,
    commission_response_threshold: 5000,
    commission_response_percent: 1,
  })
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)

  const loadSettings = useCallback(async () => {
    try {
      const response = await fetch('/api/admin/commission', {
        credentials: 'include',
      })
      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          router.push('/admin/login')
          return
        }
        throw new Error(`Failed to load commission settings: ${response.status}`)
      }

      const data: CommissionSettings = await response.json()
      setSettings(data)
    } catch (error) {
      console.error('Error loading settings:', error)
    } finally {
      setIsLoading(false)
    }
  }, [router])

  useEffect(() => {
    if (authLoading) {
      return
    }
    if (!isAuthenticated || !user?.admin_verified) {
      router.push('/admin/login')
      return
    }
    loadSettings().catch((error) => console.warn('Error loading settings:', error))
  }, [authLoading, isAuthenticated, user, router, loadSettings])

  const handleChange = (field: keyof CommissionSettings, value: string) => {
    setSettings((prev) => ({
      ...prev,
      [field]: field.includes('threshold') || field === 'commission_post_order' ? Number(value) || 0 : Number(value) || 0,
    }))
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setIsSaving(true)

    try {
      const response = await fetch('/api/admin/commission', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
        credentials: 'include',
      })

      if (response.ok) {
        alert('Настройки сохранены успешно!')
      } else if (response.status === 400) {
        const payload = await response.json()
        alert(payload.detail || 'Ошибка при сохранении настроек')
      } else if (response.status === 401 || response.status === 403) {
        router.push('/admin/login')
      } else {
        alert('Ошибка при сохранении настроек')
      }
    } catch (error) {
      console.error('Error saving settings:', error)
      alert('Ошибка при сохранении настроек')
    } finally {
      setIsSaving(false)
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
        <h1 className={styles.title}>Настройки комиссий</h1>
        <nav className={styles.nav}>
          <Link href="/admin" className={styles.navLink}>
            ← В админку
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
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.grid}>
            <div className={styles.field}>
              <label className={styles.label} htmlFor="commission_withdraw">
                Комиссия на вывод (%):
              </label>
              <input
                id="commission_withdraw"
                className={styles.input}
                type="number"
                step="0.01"
                min="0"
                max="100"
                value={settings.commission_withdraw}
                onChange={(event) => handleChange('commission_withdraw', event.target.value)}
                required
              />
            </div>

            <div className={styles.field}>
              <label className={styles.label} htmlFor="commission_customer">
                Комиссия для заказчика (%):
              </label>
              <input
                id="commission_customer"
                className={styles.input}
                type="number"
                step="0.01"
                min="0"
                max="100"
                value={settings.commission_customer}
                onChange={(event) => handleChange('commission_customer', event.target.value)}
                required
              />
            </div>

            <div className={styles.field}>
              <label className={styles.label} htmlFor="commission_executor">
                Комиссия для исполнителя (%):
              </label>
              <input
                id="commission_executor"
                className={styles.input}
                type="number"
                step="0.01"
                min="0"
                max="100"
                value={settings.commission_executor}
                onChange={(event) => handleChange('commission_executor', event.target.value)}
                required
              />
            </div>

            <div className={styles.field}>
              <label className={styles.label} htmlFor="commission_post_order">
                Плата за публикацию заказа (₽):
              </label>
              <input
                id="commission_post_order"
                className={styles.input}
                type="number"
                step="1"
                min="0"
                value={settings.commission_post_order}
                onChange={(event) => handleChange('commission_post_order', event.target.value)}
                required
              />
            </div>

            <div className={styles.field}>
              <label className={styles.label} htmlFor="commission_response_threshold">
                Порог для платного отклика (₽):
              </label>
              <input
                id="commission_response_threshold"
                className={styles.input}
                type="number"
                step="1"
                min="0"
                value={settings.commission_response_threshold}
                onChange={(event) => handleChange('commission_response_threshold', event.target.value)}
                required
              />
            </div>

            <div className={styles.field}>
              <label className={styles.label} htmlFor="commission_response_percent">
                Комиссия за отклик (%):
              </label>
              <input
                id="commission_response_percent"
                className={styles.input}
                type="number"
                step="0.01"
                min="0"
                max="100"
                value={settings.commission_response_percent}
                onChange={(event) => handleChange('commission_response_percent', event.target.value)}
                required
              />
            </div>
          </div>

          <button type="submit" className={styles.saveButton} disabled={isSaving}>
            {isSaving ? 'Сохранение…' : 'Сохранить'}
          </button>
        </form>
      </section>
    </div>
  )
}