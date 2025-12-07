'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

import Footer from '@/components/layout/Footer'
import Header from '@/components/layout/Header'
import styles from '@/components/auth/AuthPage.module.css'
import { useAuth } from '@/providers/AuthProvider'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const router = useRouter()
  const { login } = useAuth()

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setError('')

    if (!email || !password) {
      setError('Заполните все поля')
      return
    }

    try {
      const loggedInUser = await login(email, password)
      if (loggedInUser?.admin_verified) {
        router.push('/admin')
        return
      }
      router.push('/profile')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Ошибка входа'
      setError(message)
    }
  }

  return (
    <>
      <Header />

      <main className={styles.page}>
        <div className={styles.card}>
          <h1 className={styles.title}>Вход в аккаунт</h1>

          <form onSubmit={handleSubmit} className={styles.form}>
            <div className={styles.formGroup}>
              <label className={styles.label} htmlFor="login-email">
                Email
              </label>
              <input
                id="login-email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
                placeholder="Ваш email"
                className={styles.input}
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label} htmlFor="login-password">
                Пароль
              </label>
              <input
                id="login-password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
                placeholder="Ваш пароль"
                className={styles.input}
              />
            </div>

            {error && <div className={styles.error}>{error}</div>}

            <button type="submit" className={styles.submit}>
              Войти
            </button>

            <div className={styles.links}>
              <Link href="/forgot-password">Забыли пароль?</Link>
              <span>
                Нет аккаунта? <Link href="/register">Зарегистрируйтесь</Link>
              </span>
            </div>
          </form>
        </div>
      </main>

      <Footer />
    </>
  )
}