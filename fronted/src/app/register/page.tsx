'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

import Footer from '@/components/layout/Footer'
import Header from '@/components/layout/Header'
import styles from '@/components/auth/RegisterPage.module.css'
import { useAuth } from '@/providers/AuthProvider'

const SPECIALIZATION_OPTIONS = [
  'Дизайн',
  'Копирайтинг',
  'Программирование',
  'Соц сети и маркетинг',
  'Аудио и видео съёмка',
  'Фотографии',
  'Помощь по бизнесу',
]

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    nickname: '',
    phone: '',
    password: '',
    passwordConfirm: '',
    specification: '',
    description: '',
    role: '',
  })
  const [agreeTerms, setAgreeTerms] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()
  const { register } = useAuth()

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setError('')

    if (formData.password !== formData.passwordConfirm) {
      setError('Пароли не совпадают')
      return
    }

    if (!agreeTerms) {
      setError('Необходимо принять условия пользовательского соглашения')
      return
    }

    if (!formData.role) {
      setError('Необходимо выбрать роль')
      return
    }

    try {
      await register(formData)
      router.push('/profile')
    } catch (err: any) {
      setError(err.message || 'Ошибка регистрации')
    }
  }

  const handleChange = (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>,
  ) => {
    const { name, value } = event.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const isExecutor = formData.role === 'executor'
  const cardClassName = [styles.card, isExecutor ? styles.cardExpanded : ''].filter(Boolean).join(' ')

  return (
    <>
      <Header />

      <main className={styles.page}>
        <div className={cardClassName}>
          <h1 className={styles.title}>Создать аккаунт</h1>

          {error && <div className={styles.error}>{error}</div>}

          <form onSubmit={handleSubmit} className={styles.form}>
            <div className={styles.formLayout}>
              <div className={styles.mainFields}>
                <div className={styles.formRow}>
                  <div className={styles.fieldGroup}>
                    <label className={styles.label} htmlFor="name">
                      Имя *
                    </label>
                    <input
                      className={styles.input}
                      type="text"
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleChange}
                      required
                      minLength={2}
                      maxLength={15}
                      placeholder="Ваше имя"
                    />
                  </div>

                  <div className={styles.fieldGroup}>
                    <label className={styles.label} htmlFor="email">
                      Email *
                    </label>
                    <input
                      className={styles.input}
                      type="email"
                      id="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      required
                      placeholder="your@email.com"
                    />
                  </div>
                </div>

                <div className={styles.formRow}>
                  <div className={styles.fieldGroup}>
                    <label className={styles.label} htmlFor="nickname">
                      Имя пользователя
                    </label>
                    <input
                      className={styles.input}
                      type="text"
                      id="nickname"
                      name="nickname"
                      value={formData.nickname}
                      onChange={handleChange}
                      required
                      minLength={4}
                      maxLength={10}
                      pattern="^[a-zA-Z0-9_]+$"
                      placeholder="username"
                    />
                  </div>

                  <div className={styles.fieldGroup}>
                    <label className={styles.label} htmlFor="phone">
                      Телефон
                    </label>
                    <input
                      className={styles.input}
                      type="tel"
                      id="phone"
                      name="phone"
                      value={formData.phone}
                      onChange={handleChange}
                      placeholder="+7 (123) 456-78-90"
                      pattern="^\+?[1-9]\d{1,14}$"
                    />
                  </div>
                </div>

                <div className={styles.formRow}>
                  <div className={styles.fieldGroup}>
                    <label className={styles.label} htmlFor="password">
                      Пароль *
                    </label>
                    <input
                      className={styles.input}
                      type="password"
                      id="password"
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      required
                      placeholder="••••••••"
                    />
                  </div>

                  <div className={styles.fieldGroup}>
                    <label className={styles.label} htmlFor="passwordConfirm">
                      Подтверждение *
                    </label>
                    <input
                      className={styles.input}
                      type="password"
                      id="passwordConfirm"
                      name="passwordConfirm"
                      value={formData.passwordConfirm}
                      onChange={handleChange}
                      required
                      placeholder="••••••••"
                    />
                  </div>
                </div>

                <div className={`${styles.fieldGroup} ${styles.roleGroup}`}>
                  <span className={styles.roleLabel}>Выберите роль *</span>
                  <div className={styles.roleSelector}>
                    <button
                      type="button"
                      className={[styles.roleOption, formData.role === 'customer' ? styles.roleOptionSelected : '']
                        .filter(Boolean)
                        .join(' ')}
                      onClick={() => setFormData((prev) => ({ ...prev, role: 'customer' }))}
                    >
                      <div className={styles.roleIcon}>👤</div>
                      <div className={styles.roleInfo}>
                        <div className={styles.roleTitle}>Заказчик</div>
                        <div className={styles.roleDesc}>Ищу исполнителей для проектов</div>
                      </div>
                      <div className={styles.roleCheck}>✓</div>
                    </button>

                    <button
                      type="button"
                      className={[styles.roleOption, formData.role === 'executor' ? styles.roleOptionSelected : '']
                        .filter(Boolean)
                        .join(' ')}
                      onClick={() => setFormData((prev) => ({ ...prev, role: 'executor' }))}
                    >
                      <div className={styles.roleIcon}>⚡</div>
                      <div className={styles.roleInfo}>
                        <div className={styles.roleTitle}>Исполнитель</div>
                        <div className={styles.roleDesc}>Выполняю проекты и задачи</div>
                      </div>
                      <div className={styles.roleCheck}>✓</div>
                    </button>
                  </div>
                </div>
              </div>

              {isExecutor && (
                <div className={styles.executorColumn}>
                  <div className={styles.executorSection}>
                    <h3>Информация исполнителя</h3>
                    <div className={styles.fieldGroup}>
                      <label className={styles.label} htmlFor="specification">
                        Специализация *
                      </label>
                      <select
                        className={styles.select}
                        id="specification"
                        name="specification"
                        value={formData.specification}
                        onChange={handleChange}
                        required
                      >
                        <option value="" disabled>
                          Выберите специализацию
                        </option>
                        {SPECIALIZATION_OPTIONS.map((option) => (
                          <option key={option} value={option}>
                            {option}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className={styles.fieldGroup}>
                      <label className={styles.label} htmlFor="description">
                        О себе
                        <span className={styles.charCount}>{formData.description.length}/500</span>
                      </label>
                      <textarea
                        className={styles.textarea}
                        id="description"
                        name="description"
                        value={formData.description}
                        onChange={handleChange}
                        rows={4}
                        maxLength={500}
                        placeholder="Расскажите о своих навыках и опыте..."
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className={styles.formFooter}>
              <div className={styles.checkboxRow}>
                <input
                  type="checkbox"
                  id="terms"
                  checked={agreeTerms}
                  onChange={(event) => setAgreeTerms(event.target.checked)}
                  required
                />
                <label htmlFor="terms">Я принимаю условия пользовательского соглашения</label>
              </div>

              <button type="submit" className={styles.submit}>
                Зарегистрироваться
              </button>

              <div className={styles.links}>
                <span>
                  Уже есть аккаунт? <Link href="/login">Войдите</Link>
                </span>
              </div>
            </div>
          </form>
        </div>
      </main>

      <Footer />
    </>
  )
}