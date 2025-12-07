import { useEffect, useMemo, useState } from 'react'

import styles from './ProfilePage.module.css'
import { portfolioApi, PortfolioItem } from '@/utils/portfolioApi'

interface FormState {
  title: string
  description: string
  tags: string
  mediaFile: File | null
  attachmentFile: File | null
  mediaUrl: string
  attachmentUrl: string
  is_featured: boolean
}

const initialForm: FormState = {
  title: '',
  description: '',
  tags: '',
  mediaFile: null,
  attachmentFile: null,
  mediaUrl: '',
  attachmentUrl: '',
  is_featured: false
}

export function ProfilePortfolioTab() {
  const [items, setItems] = useState<PortfolioItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isAdding, setIsAdding] = useState(false)
  const [form, setForm] = useState<FormState>(initialForm)
  const [achievements, setAchievements] = useState<Array<{ id: number; title: string; description?: string; icon?: string; awarded_at: string }>>([])

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await portfolioApi.listMine()
        setItems(data)
      } catch (err) {
        console.error(err)
        setError('Не удалось загрузить портфолио')
      } finally {
        setLoading(false)
      }
    }

    const fetchAchievements = async () => {
      try {
        const data = await portfolioApi.achievementsBoard()
        setAchievements(data.items ?? [])
      } catch (err) {
        console.warn('Не удалось загрузить достижения', err)
      }
    }

    fetchData()
    fetchAchievements()
  }, [])

  const resetForm = () => {
    setForm(initialForm)
    setIsAdding(false)
  }

  const handleUpload = async (file: File | null) => {
    if (!file) {
      return undefined
    }
    const response = await portfolioApi.upload(file)
    return response
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setError(null)

    try {
      let mediaUrl = form.mediaUrl
      let attachmentUrl = form.attachmentUrl

      if (form.mediaFile) {
        mediaUrl = await handleUpload(form.mediaFile) ?? mediaUrl
      }
      if (form.attachmentFile) {
        attachmentUrl = await handleUpload(form.attachmentFile) ?? attachmentUrl
      }

      const payload = {
        title: form.title,
        description: form.description || undefined,
        tags: form.tags || undefined,
        media_url: mediaUrl || undefined,
        attachment_url: attachmentUrl || undefined,
        is_featured: form.is_featured
      }

      const created = await portfolioApi.create(payload)
      setItems((prev) => [created, ...prev])
      resetForm()
    } catch (err) {
      console.error(err)
      setError('Не удалось сохранить работу. Попробуйте ещё раз.')
    }
  }

  const handleDelete = async (id: number) => {
    if (!window.confirm('Удалить работу из портфолио?')) {
      return
    }
    try {
      await portfolioApi.remove(id)
      setItems((prev) => prev.filter((item) => item.id !== id))
    } catch (err) {
      console.error(err)
      setError('Не удалось удалить работу.')
    }
  }

  const featuredItems = useMemo(() => items.filter((item) => item.is_featured), [items])

  return (
    <section>
      <div className={styles.tabHeader}>
        <h2 className={styles.tabTitle}>Моё портфолио</h2>
        <div className={styles.tabActions}>
          <button type="button" className={styles.primaryAction} onClick={() => setIsAdding((state) => !state)}>
            {isAdding ? 'Отменить' : 'Добавить работу'}
          </button>
        </div>
      </div>

      {error && <div className={styles.formError}>{error}</div>}

      {isAdding && (
        <form className={styles.portfolioForm} onSubmit={handleSubmit}>
          <div className={styles.formRow}>
            <label className={styles.formLabel} htmlFor="portfolio-title">
              Название работы
            </label>
            <input
              id="portfolio-title"
              className={styles.infoInput}
              type="text"
              value={form.title}
              onChange={(event) => setForm((prev) => ({ ...prev, title: event.target.value }))}
              required
            />
          </div>

          <div className={styles.formRow}>
            <label className={styles.formLabel} htmlFor="portfolio-description">
              Описание
            </label>
            <textarea
              id="portfolio-description"
              className={styles.infoTextarea}
              value={form.description}
              onChange={(event) => setForm((prev) => ({ ...prev, description: event.target.value }))}
              placeholder="Расскажите о задаче, подходе и результате"
            />
          </div>

          <div className={styles.formRow}>
            <label className={styles.formLabel} htmlFor="portfolio-tags">
              Теги
            </label>
            <input
              id="portfolio-tags"
              className={styles.infoInput}
              value={form.tags}
              onChange={(event) => setForm((prev) => ({ ...prev, tags: event.target.value }))}
              placeholder="например: дизайн, веб, презентация"
            />
          </div>

          <div className={styles.formUploads}>
            <div className={styles.uploadField}>
              <label className={styles.formLabel} htmlFor="portfolio-media">
                Изображение (превью)
              </label>
              <input
                id="portfolio-media"
                type="file"
                accept="image/*"
                onChange={(event) => setForm((prev) => ({ ...prev, mediaFile: event.target.files?.[0] ?? null }))}
              />
              <input
                type="url"
                className={styles.infoInput}
                placeholder="или вставьте ссылку"
                value={form.mediaUrl}
                onChange={(event) => setForm((prev) => ({ ...prev, mediaUrl: event.target.value }))}
              />
            </div>

            <div className={styles.uploadField}>
              <label className={styles.formLabel} htmlFor="portfolio-attachment">
                Файл (результат)
              </label>
              <input
                id="portfolio-attachment"
                type="file"
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, attachmentFile: event.target.files?.[0] ?? null }))
                }
              />
              <input
                type="url"
                className={styles.infoInput}
                placeholder="или вставьте ссылку на файл"
                value={form.attachmentUrl}
                onChange={(event) => setForm((prev) => ({ ...prev, attachmentUrl: event.target.value }))}
              />
            </div>
          </div>

          <div className={styles.formFooter}>
            <label className={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={form.is_featured}
                onChange={(event) => setForm((prev) => ({ ...prev, is_featured: event.target.checked }))}
              />
              Показывать в избранных работах
            </label>

            <div className={styles.tabActions}>
              <button type="submit" className={styles.primaryAction}>
                Сохранить работу
              </button>
              <button type="button" className={styles.secondaryAction} onClick={resetForm}>
                Отмена
              </button>
            </div>
          </div>
        </form>
      )}

      {loading ? (
        <div className={styles.emptyState}>
          <p>Загружаем портфолио…</p>
        </div>
      ) : items.length === 0 ? (
        <div className={styles.emptyState}>
          <p>Здесь пока нет работ. Добавьте первую работу, чтобы клиенты могли оценить ваши навыки.</p>
        </div>
      ) : (
        <div className={styles.portfolioGrid}>
          {items.map((item) => (
            <article key={item.id} className={styles.portfolioCard}>
              {item.media_url && (
                <div className={styles.portfolioMedia}>
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={item.media_url} alt={item.title} />
                </div>
              )}
              <div className={styles.portfolioBody}>
                <header className={styles.portfolioHeader}>
                  <h3>{item.title}</h3>
                  {item.is_featured && <span className={styles.featuredBadge}>Избранное</span>}
                </header>
                {item.description && <p className={styles.portfolioDescription}>{item.description}</p>}
                <footer className={styles.portfolioFooter}>
                  <div className={styles.portfolioMeta}>
                    <span>{new Date(item.created_at).toLocaleDateString('ru-RU')}</span>
                    {item.tags && <span className={styles.portfolioTags}>{item.tags}</span>}
                  </div>
                  <div className={styles.portfolioActions}>
                    {item.attachment_url && (
                      <a href={item.attachment_url} target="_blank" rel="noopener noreferrer" className={styles.secondaryAction}>
                        Скачать
                      </a>
                    )}
                    <button type="button" className={styles.secondaryAction} onClick={() => handleDelete(item.id)}>
                      Удалить
                    </button>
                  </div>
                </footer>
              </div>
            </article>
          ))}
        </div>
      )}

      {featuredItems.length > 0 && (
        <div className={styles.highlightSection}>
          <h3>Избранные работы</h3>
          <div className={styles.highlightGrid}>
            {featuredItems.map((item) => (
              <div key={`featured-${item.id}`} className={styles.highlightCard}>
                <strong>{item.title}</strong>
                {item.media_url && (
                  /* eslint-disable-next-line @next/next/no-img-element */
                  <img src={item.media_url} alt={item.title} />
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {achievements.length > 0 && (
        <aside className={styles.achievementsBoard}>
          <h3>Достижения</h3>
          <ul>
            {achievements.map((item) => (
              <li key={item.id}>
                <span className={styles.achievementIcon}>{item.icon ?? '🏆'}</span>
                <div>
                  <p className={styles.achievementTitle}>{item.title}</p>
                  {item.description && <p className={styles.achievementDescription}>{item.description}</p>}
                </div>
              </li>
            ))}
          </ul>
        </aside>
      )}
    </section>
  )
}
