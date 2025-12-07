'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

import styles from '@/components/admin/AdminLogin.module.css'
import { useAuth } from '@/providers/AuthProvider'

export default function AdminLogin() {
  const [login, setLogin] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const router = useRouter()
  const { login: loginUser, logout } = useAuth()

  const resolveEmail = (rawLogin: string) => {
    if (rawLogin.includes('@')) {
      return rawLogin
    }
    const domain =
      process.env.NEXT_PUBLIC_ADMIN_LOGIN_DOMAIN ||
      process.env.ADMIN_LOGIN_DOMAIN ||
      'teenfreelance.ru'
    return `${rawLogin}@${domain}`
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()

    try {
      const user = await loginUser(resolveEmail(login), password)
      if (!user?.admin_verified) {
        setError('У вас нет прав администратора')
        await logout()
        return
      }

      router.push('/admin')
    } catch (fetchError) {
      setError(fetchError instanceof Error ? fetchError.message : 'Ошибка входа')
    }
  }

  return (
    <main className={styles.page}>
      <div className={styles.card}>
        <h1 className={styles.title}>Вход в админку</h1>

        {error && <div className={styles.error}>{error}</div>}

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.formGroup}>
            <label className={styles.label} htmlFor="admin-login">
              Логин
            </label>
            <input
              className={styles.input}
              type="text"
              id="admin-login"
              value={login}
              onChange={(event) => setLogin(event.target.value)}
              required
            />
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label} htmlFor="admin-password">
              Пароль
            </label>
            <input
              className={styles.input}
              type="password"
              id="admin-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </div>

          <button type="submit" className={styles.submit}>
            Войти
          </button>
        </form>
      </div>
    </main>
  )
}