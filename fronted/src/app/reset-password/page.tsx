'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'

import Footer from '@/components/layout/Footer'
import Header from '@/components/layout/Header'
import authStyles from '@/components/auth/AuthPage.module.css'
import resetStyles from '@/components/auth/ResetPassword.module.css'
import { apiClient } from '@/utils/apiClient'

export default function ResetPasswordPage() {
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isValidToken, setIsValidToken] = useState<boolean | null>(null)
  const [email, setEmail] = useState('')
  const [token, setToken] = useState('')

  const router = useRouter()
  const searchParams = useSearchParams()

  useEffect(() => {
    const tokenParam = searchParams.get('token')
    const emailFromUrl = searchParams.get('email')

    if (!tokenParam) {
      setError('Недействительная ссылка для сброса пароля')
      setIsValidToken(false)
      return
    }

    setToken(tokenParam)
    if (emailFromUrl) {
      setEmail(decodeURIComponent(emailFromUrl))
    }

    const validateToken = async () => {
      try {
        await apiClient.get(`/auth/reset-password/${tokenParam}/validate`)
        setIsValidToken(true)
      } catch (err) {
        console.error('Reset token validation error:', err)
        setError('Ссылка устарела или недействительна. Запросите новую ссылку.')
        setIsValidToken(false)
      }
    }

    validateToken()
  }, [searchParams])

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setError('')
    setIsLoading(true)

    if (!password || !confirmPassword) {
      setError('Заполните все поля')
      setIsLoading(false)
      return
    }

    if (password !== confirmPassword) {
      setError('Пароли не совпадают')
      setIsLoading(false)
      return
    }

    if (password.length < 6) {
      setError('Пароль должен содержать минимум 6 символов')
      setIsLoading(false)
      return
    }

    try {
      await apiClient.post('/auth/reset-password', {
        token,
        password,
        password_confirm: confirmPassword,
      })

      router.push('/login?message=password_reset_success')
    } catch (err) {
      setError('Произошла ошибка при сбросе пароля')
      console.error('Reset password error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  if (isValidToken === null) {
    return (
      <>
        <Header />
        <main className={authStyles.page}>
          <div className={authStyles.card}>
            <div className={resetStyles.loading}>Проверка ссылки...</div>
          </div>
        </main>
        <Footer />
      </>
    )
  }

  if (!isValidToken) {
    return (
      <>
        <Header />
        <main className={authStyles.page}>
          <div className={authStyles.card}>
            <div className={resetStyles.errorContainer}>
              <div className={resetStyles.errorIcon}>⚠️</div>
              <h2 className={authStyles.title}>Недействительная ссылка</h2>
              <p className={authStyles.error}>{error}</p>
              <button type="button" onClick={() => router.push('/forgot-password')} className={authStyles.submit}>
                Запросить новую ссылку
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
      <main className={authStyles.page}>
        <div className={authStyles.card}>
          <h1 className={authStyles.title}>Создание нового пароля</h1>
          <p className={resetStyles.description}>
            Введите новый пароль{email ? ` для аккаунта ${email}` : ''}
          </p>

          <form onSubmit={handleSubmit} className={authStyles.form}>
            <div className={authStyles.formGroup}>
              <label className={authStyles.label} htmlFor="reset-password">
                Новый пароль
              </label>
              <input
                id="reset-password"
                className={authStyles.input}
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
                placeholder="Введите новый пароль"
                disabled={isLoading}
                minLength={6}
              />
            </div>

            <div className={authStyles.formGroup}>
              <label className={authStyles.label} htmlFor="reset-password-confirm">
                Подтвердите пароль
              </label>
              <input
                id="reset-password-confirm"
                className={authStyles.input}
                type="password"
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                required
                placeholder="Повторите новый пароль"
                disabled={isLoading}
                minLength={6}
              />
            </div>

            {error && <div className={authStyles.error}>{error}</div>}

            <button type="submit" className={authStyles.submit} disabled={isLoading}>
              {isLoading ? 'Сохранение...' : 'Сохранить новый пароль'}
            </button>
          </form>
        </div>
      </main>
      <Footer />
    </>
  )
}