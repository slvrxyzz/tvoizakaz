'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

import Footer from '@/components/layout/Footer'
import Header from '@/components/layout/Header'
import styles from '@/components/orders/CreateOrderPage.module.css'
import { useAuth } from '@/providers/AuthProvider'
import { apiClient } from '@/utils/apiClient'
import { CurrencyType } from '@/dto/common.dto'
import { getCurrencySymbol } from '@/utils/currency'

const CATEGORY_OPTIONS = [
  { value: '', label: 'Выберите категорию' },
  { value: 'web-development', label: 'Веб-разработка' },
  { value: 'design', label: 'Дизайн' },
  { value: 'copywriting', label: 'Копирайтинг' },
  { value: 'programming', label: 'Программирование' },
  { value: 'marketing', label: 'Маркетинг' },
  { value: 'other', label: 'Другое' },
]

export default function CreateOrderPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuth()
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    price: '',
    deadline: '',
    category: '',
    currency: CurrencyType.RUB,
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = event.target
    if (name === 'currency') {
      setFormData((prev) => ({ ...prev, currency: value as CurrencyType }))
      return
    }
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setIsSubmitting(true)
    setError('')

    if (!isAuthenticated) {
      setError('Необходимо войти в систему для создания заказа')
      setIsSubmitting(false)
      return
    }

    try {
      if (!formData.title || formData.title.length < 1 || formData.title.length > 30) {
        throw new Error('Название должно содержать от 1 до 30 символов')
      }
      if (!formData.description || formData.description.length < 1 || formData.description.length > 250) {
        throw new Error('Описание должно содержать от 1 до 250 символов')
      }
      const price = Number(formData.price)
      if (!price || price < 400 || price > 400000) {
        throw new Error('Цена должна быть от 400 до 400000 рублей')
      }
      const deadline = Number(formData.deadline)
      if (!deadline || deadline < 1 || deadline > 30) {
        throw new Error('Срок должен быть от 1 до 30 дней')
      }
      if (!formData.category || formData.category.length > 50) {
        throw new Error('Категория должна быть выбрана и содержать не более 50 символов')
      }

      await apiClient.post('/orders/', {
        title: formData.title.trim(),
        description: formData.description.trim(),
        price,
        currency: formData.currency,
        term: deadline,
        category: formData.category.trim(),
        priority: 'NORMAL',
        order_type: 'REGULAR',
      })

      router.push('/orders')
    } catch (submitError: unknown) {
      if (submitError instanceof Error) {
        setError(submitError.message)
      } else if (typeof submitError === 'string') {
        setError(submitError)
      } else {
        setError('Ошибка создания заказа')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  const currencySymbol = getCurrencySymbol(formData.currency)

  return (
    <>
      <Header />
      <main className={styles.page}>
        <div className={styles.pageHeader}>
          <header className={styles.header}>
            <h1 className={styles.title}>Создать заказ</h1>
            <p className={styles.subtitle}>Опишите проект, чтобы исполнители могли откликнуться</p>
          </header>
        </div>
        <div className={styles.container}>
          <form onSubmit={handleSubmit} className={styles.form}>
            <div className={styles.group}>
              <label className={styles.label} htmlFor="title">
                Название заказа
                <span className={styles.charCount}>{formData.title.length}/30</span>
              </label>
              <input
                className={styles.input}
                type="text"
                id="title"
                name="title"
                value={formData.title}
                onChange={handleChange}
                maxLength={30}
                required
                disabled={isSubmitting}
                placeholder="Кратко опишите, что нужно сделать"
              />
            </div>

            <div className={styles.group}>
              <label className={styles.label} htmlFor="description">
                Описание
                <span className={styles.charCount}>{formData.description.length}/250</span>
              </label>
              <textarea
                className={styles.textarea}
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                maxLength={250}
                required
                disabled={isSubmitting}
                placeholder="Расскажите подробнее о проекте, ожидаемом результате и требованиях"
              />
            </div>

            <div className={styles.row}>
              <div className={styles.group}>
              <label className={styles.label}>Валюта</label>
              <div className={styles.inlineOptions}>
                <label className={styles.radioOption}>
                  <input
                    type="radio"
                    name="currency"
                    value={CurrencyType.RUB}
                    checked={formData.currency === CurrencyType.RUB}
                    onChange={handleChange}
                    disabled={isSubmitting}
                  />
                  <span>₽ Рубли</span>
                </label>
                <label className={styles.radioOption}>
                  <input
                    type="radio"
                    name="currency"
                    value={CurrencyType.TF}
                    checked={formData.currency === CurrencyType.TF}
                    onChange={handleChange}
                    disabled={isSubmitting}
                  />
                  <span>TF монеты</span>
                </label>
              </div>
            </div>

            <div className={styles.group}>
                <label className={styles.label} htmlFor="price">
                  Бюджет ({currencySymbol})
                </label>
                <input
                  className={styles.input}
                  type="number"
                  id="price"
                  name="price"
                  value={formData.price}
                  onChange={handleChange}
                  min={400}
                  max={400000}
                  required
                  disabled={isSubmitting}
                  placeholder="400"
                />
              </div>

              <div className={styles.group}>
                <label className={styles.label} htmlFor="deadline">
                  Срок (дни)
                </label>
                <input
                  className={styles.input}
                  type="number"
                  id="deadline"
                  name="deadline"
                  value={formData.deadline}
                  onChange={handleChange}
                  min={1}
                  max={30}
                  required
                  disabled={isSubmitting}
                  placeholder="7"
                />
              </div>
            </div>

            <div className={styles.group}>
              <label className={styles.label} htmlFor="category">
                Категория
              </label>
              <select
                className={styles.select}
                id="category"
                name="category"
                value={formData.category}
                onChange={handleChange}
                required
                disabled={isSubmitting}
              >
                {CATEGORY_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            {error && (
              <div className={styles.error}>
                <p>{error}</p>
              </div>
            )}

            <div className={styles.actions}>
              <button type="button" onClick={() => router.back()} className={styles.btnSecondary} disabled={isSubmitting}>
                Отмена
              </button>
              <button type="submit" className={styles.btnPrimary} disabled={isSubmitting}>
                {isSubmitting ? 'Создание…' : 'Создать заказ'}
              </button>
            </div>
          </form>
        </div>
      </main>
      <Footer />
    </>
  )
}