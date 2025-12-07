'use client'
import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

import styles from '@/components/admin/CommissionPage.module.css'
import { apiClient } from '@/utils/apiClient'
import { useAuth } from '@/providers/AuthProvider'

const CONTENT_TYPES = [
  { value: 'article', label: 'Статья' },
  { value: 'news', label: 'Новости' },
  { value: 'test', label: 'Тест' },
  { value: 'career', label: 'Карьера' },
]

export default function ContentManagementPage() {
  const router = useRouter()
  const { user, isAuthenticated, loading: authLoading } = useAuth()
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [type, setType] = useState('article')
  const [tags, setTags] = useState('')
  const [isPublished, setIsPublished] = useState(false)
  const [status, setStatus] = useState<{ kind: 'success' | 'error'; message: string } | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  if (authLoading) {
    return (
      <div className={styles.page}>
        <div className={styles.loading}>Загрузка…</div>
      </div>
    )
  }

  if (!isAuthenticated || !user || !['ADMIN', 'EDITOR'].includes((user.role ?? '').toUpperCase())) {
    router.push('/admin/login')
    return null
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setStatus(null)
    setIsSubmitting(true)
    try {
      await apiClient.post('/content/', {
        title: title.trim(),
        content: content.trim(),
        type,
        tags: tags
          .split(',')
          .map((tag) => tag.trim())
          .filter(Boolean),
        is_published: isPublished,
      })
      setStatus({ kind: 'success', message: 'Материал успешно создан' })
      setTitle('')
      setContent('')
      setTags('')
      setIsPublished(false)
    } catch (error) {
      console.error('Error creating content:', error)
      setStatus({ kind: 'error', message: error instanceof Error ? error.message : 'Не удалось создать материал' })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>Управление контентом</h1>
        <nav className={styles.nav}>
          <Link href="/admin" className={styles.navLink}>
            ← В админку
          </Link>
          <Link href="/admin/commission" className={styles.navLink}>
            Комиссии
          </Link>
          <Link href="/admin/support" className={styles.navLink}>
            Поддержка
          </Link>
        </nav>
      </header>

      <section className={styles.content}>
        <form onSubmit={handleSubmit} className={styles.form}>
          {status && (
            <div
              className={status.kind === 'success' ? styles.statusSuccess : styles.statusError}
              role="alert"
            >
              {status.message}
            </div>
          )}

          <div className={styles.field}>
            <label className={styles.label} htmlFor="title">
              Заголовок
            </label>
            <input
              id="title"
              className={styles.input}
              type="text"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              minLength={1}
              maxLength={200}
              required
              disabled={isSubmitting}
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label} htmlFor="type">
              Тип материала
            </label>
            <select
              id="type"
              className={styles.select}
              value={type}
              onChange={(event) => setType(event.target.value)}
              disabled={isSubmitting}
            >
              {CONTENT_TYPES.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className={styles.field}>
            <label className={styles.label} htmlFor="content">
              Содержимое
            </label>
            <textarea
              id="content"
              className={styles.textarea}
              value={content}
              onChange={(event) => setContent(event.target.value)}
              rows={10}
              minLength={10}
              required
              disabled={isSubmitting}
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label} htmlFor="tags">
              Теги (через запятую)
            </label>
            <input
              id="tags"
              className={styles.input}
              type="text"
              value={tags}
              onChange={(event) => setTags(event.target.value)}
              placeholder="например: дизайн, разработка"
              disabled={isSubmitting}
            />
          </div>

          <div className={styles.field}>
            <label className={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={isPublished}
                onChange={(event) => setIsPublished(event.target.checked)}
                disabled={isSubmitting}
              />
              Опубликовать сразу
            </label>
          </div>

          <button type="submit" className={styles.saveButton} disabled={isSubmitting}>
            {isSubmitting ? 'Сохранение…' : 'Создать материал'}
          </button>
        </form>
      </section>
    </div>
  )
}


