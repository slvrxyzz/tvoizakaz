'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

import Footer from '@/components/layout/Footer'
import Header from '@/components/layout/Header'
import authStyles from '@/components/auth/AuthPage.module.css'
import resetStyles from '@/components/auth/ResetPassword.module.css'
import { apiClient } from '@/utils/apiClient'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [resetToken, setResetToken] = useState<string | null>(null)
  const router = useRouter()

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setError('')
    setIsLoading(true)

    if (!email) {
      setError('Введите ваш email')
      setIsLoading(false)
      return
    }

    if (!/\S+@\S+\.\S+/.test(email)) {
      setError('Введите корректный email')
      setIsLoading(false)
      return
    }

    try {
      const response = await apiClient.post<{ success: boolean; message?: string; token?: string }>(
        '/auth/forgot-password',
        { email },
      )

      if (response.token) {
        setResetToken(response.token)
        console.info('Password reset token:', response.token)
      }

      if (response.success) {
        setIsSubmitted(true)
      } else {
        setError(response.message || 'Ошибка при отправке email. Попробуйте еще раз.')
      }
    } catch (err) {
      setError('Произошла ошибка. Попробуйте еще раз.')
      console.error('Password reset error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const resetLink = resetToken
    ? `${window.location.origin}/reset-password?token=${resetToken}${email ? `&email=${encodeURIComponent(email)}` : ''}`
    : null

  return (
    <>
      <Header />

      <main className={authStyles.page}>
        <div className={authStyles.card}>
          {!isSubmitted ? (
            <>
              <h1 className={authStyles.title}>Восстановление пароля</h1>
              <p className={resetStyles.description}>
                Введите ваш email, и мы вышлем ссылку для создания нового пароля
              </p>

              <form onSubmit={handleSubmit} className={authStyles.form}>
                <div className={authStyles.formGroup}>
                  <label className={authStyles.label} htmlFor="forgot-email">
                    Email
                  </label>
                  <input
                    id="forgot-email"
                    className={authStyles.input}
                    type="email"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    required
                    placeholder="Ваш email"
                    disabled={isLoading}
                  />
                </div>

                {error && <div className={authStyles.error}>{error}</div>}

                <button type="submit" className={authStyles.submit} disabled={isLoading}>
                  {isLoading ? 'Отправка...' : 'Отправить ссылку'}
                </button>

                <div className={authStyles.links}>
                  <span>
                    Вспомнили пароль? <Link href="/login">Войдите в аккаунт</Link>
                  </span>
                </div>
              </form>
            </>
          ) : (
            <div className={resetStyles.successContainer}>
              <div className={resetStyles.successIcon}>✓</div>
              <h1 className={authStyles.title}>Письмо отправлено!</h1>
              <p className={resetStyles.successMessage}>
                Мы отправили ссылку для восстановления пароля на email: <strong>{email}</strong>
              </p>

              <div className={resetStyles.successInfo}>
                <p>📧 <strong>В демо-режиме:</strong></p>
                <p>Ссылка действительна <strong>1 час</strong></p>
                {resetLink && (
                  <p>
                    Скопируйте ссылку: <br />
                    <code>{resetLink}</code>
                  </p>
                )}
              </div>

              <div className={resetStyles.successActions}>
                <button type="button" onClick={() => router.push('/login')} className={authStyles.submit}>
                  Вернуться к входу
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setIsSubmitted(false)
                    setEmail('')
                    setResetToken(null)
                  }}
                  className={resetStyles.secondaryButton}
                >
                  Отправить еще раз
                </button>
              </div>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </>
  )
}