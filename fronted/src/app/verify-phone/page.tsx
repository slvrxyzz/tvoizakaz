
'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

import Footer from '@/components/layout/Footer'
import Header from '@/components/layout/Header'
import verifyStyles from '@/components/verify/VerifyPhonePage.module.css'
import { apiClient } from '@/utils/apiClient'
import { useAuth } from '@/providers/AuthProvider'

interface VerificationStatus {
  phone_verified: boolean
  admin_verified: boolean
  phone_number?: string | null
  verification_level: string
}

export default function VerifyPhonePage() {
  const router = useRouter()
  const { user, loading: authLoading, isAuthenticated, refreshUser } = useAuth()

  const [status, setStatus] = useState<VerificationStatus | null>(null)
  const [code, setCode] = useState(['', '', '', ''])
  const [isLoading, setIsLoading] = useState(false)
  const [countdown, setCountdown] = useState(0)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const phoneNumber = status?.phone_number || user?.phone_number || ''

  useEffect(() => {
    if (authLoading) {
      return
    }

    if (!isAuthenticated) {
      router.push('/login')
      return
    }

    loadStatus()
  }, [authLoading, isAuthenticated])

  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown((prev) => prev - 1), 1000)
      return () => clearTimeout(timer)
    }
  }, [countdown])

  const loadStatus = async () => {
    try {
      const data = await apiClient.get<VerificationStatus>('/verification/status')
      setStatus(data)

      if (data.phone_verified) {
        await refreshUser()
        router.push('/profile')
      }
    } catch (err) {
      console.error('Failed to load verification status:', err)
      setError('Не удалось получить статус подтверждения. Попробуйте позже.')
    }
  }

  const handleCodeChange = (index: number, value: string) => {
    if (value.length <= 1 && /^\d*$/.test(value)) {
      const newCode = [...code]
      newCode[index] = value
      setCode(newCode)

      if (value && index < 3) {
        const nextInput = document.getElementById(`code-${index + 1}`)
        nextInput?.focus()
      }
    }
  }

  const handleKeyDown = (index: number, event: React.KeyboardEvent) => {
    if (event.key === 'Backspace' && !code[index] && index > 0) {
      const prevInput = document.getElementById(`code-${index - 1}`)
      prevInput?.focus()
    }
  }

  const handleSendCode = async () => {
    if (!phoneNumber) {
      setError('Телефон не указан. Измените номер в профиле.')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      await apiClient.post('/verification/phone/send', { phone: phoneNumber })
      setCountdown(60)
      setSuccess(`Код подтверждения отправлен на номер ${phoneNumber}`)
      setCode(['', '', '', ''])
    } catch (err) {
      console.error('Send code error:', err)
      setError('Ошибка при отправке кода. Попробуйте позже.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleVerify = async () => {
    const verificationCode = code.join('')

    if (verificationCode.length !== 4) {
      setError('Введите полный код из 4 цифр')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      await apiClient.post('/verification/phone/confirm', {
        phone: phoneNumber,
        code: verificationCode,
      })

      await refreshUser()
      setSuccess('Телефон успешно подтвержден!')
      setStatus((prev) => (prev ? { ...prev, phone_verified: true } : prev))

      setTimeout(() => {
        router.push('/profile')
      }, 1500)
    } catch (err) {
      console.error('Verify code error:', err)
      setError('Ошибка при проверке кода. Попробуйте позже.')
    } finally {
      setIsLoading(false)
    }
  }

  if (authLoading || !isAuthenticated || !status) {
    return (
      <div className={verifyStyles.loading}>
        <div className={verifyStyles.spinner} />
        <p>Загрузка...</p>
      </div>
    )
  }

  if (status.phone_verified) {
    return null
  }

  return (
    <>
      <Header />

      <main className={verifyStyles.page}>
        <div className={verifyStyles.container}>
          <div className={verifyStyles.card}>
            <div className={verifyStyles.header}>
              <h1>Подтверждение телефона</h1>
              <p>Для завершения регистрации подтвердите ваш номер телефона</p>
            </div>

            <div className={verifyStyles.phoneInfo}>
              <div className={verifyStyles.phoneNumber}>📱 {phoneNumber || 'Номер не указан'}</div>
              <Link href="/profile" className={verifyStyles.changePhoneLink}>
                Изменить номер
              </Link>
            </div>

            <div className={verifyStyles.codeSection}>
              <label>Введите код из SMS</label>
              <div className={verifyStyles.codeInputs}>
                {code.map((digit, index) => (
                  <input
                    key={index}
                    id={`code-${index}`}
                    type="text"
                    inputMode="numeric"
                    maxLength={1}
                    value={digit}
                    onChange={(event) => handleCodeChange(index, event.target.value)}
                    onKeyDown={(event) => handleKeyDown(index, event)}
                    className={verifyStyles.codeInput}
                    disabled={isLoading}
                  />
                ))}
              </div>
            </div>

            {error && <div className={verifyStyles.errorMessage}>{error}</div>}
            {success && <div className={verifyStyles.successMessage}>{success}</div>}

            <div className={verifyStyles.actions}>
              <button
                type="button"
                onClick={handleVerify}
                disabled={isLoading || code.join('').length !== 4 || !phoneNumber}
                className={verifyStyles.verifyButton}
              >
                {isLoading ? 'Проверка...' : 'Подтвердить телефон'}
              </button>

              <div className={verifyStyles.resend}>
                <p>Не получили код?</p>
                <button
                  type="button"
                  onClick={handleSendCode}
                  disabled={isLoading || countdown > 0 || !phoneNumber}
                  className={verifyStyles.resendButton}
                >
                  {countdown > 0 ? `Отправить повторно (${countdown}с)` : 'Отправить код повторно'}
                </button>
              </div>
            </div>

            <div className={verifyStyles.helpText}>
              <p>Если вы не получаете SMS, проверьте правильность номера телефона или обратитесь в поддержку.</p>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </>
  )
}   