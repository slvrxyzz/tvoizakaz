"use client"

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useParams } from 'next/navigation'

import Footer from '@/components/layout/Footer'
import Header from '@/components/layout/Header'
import styles from '@/components/users/UserProfilePage.module.css'
import { ReviewDTO, UserPublicProfileDTO } from '@/dto'
import { useAuth } from '@/providers/AuthProvider'
import { apiClient } from '@/utils/apiClient'
import { portfolioApi, PortfolioItem } from '@/utils/portfolioApi'

export default function UserProfilePage() {
  const params = useParams()
  const nickname = params.nickname as string
  const { user: currentUser, isAuthenticated } = useAuth()

  const [profile, setProfile] = useState<UserPublicProfileDTO | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [portfolioItems, setPortfolioItems] = useState<PortfolioItem[]>([])
  const [achievements, setAchievements] = useState<Array<{ id: number; title: string; description?: string; icon?: string }>>([])

  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        setLoading(true)
        setError(null)
        const userData = await apiClient.get<UserPublicProfileDTO>(`/users/${nickname}`)
        setProfile(userData)
        const [portfolioData, rewardsData] = await Promise.all([
          portfolioApi.listUser(userData.id),
          apiClient
            .get<{ achievements: Array<{ id: number; title: string; description?: string; icon?: string }> }>(
              `/rewards/users/${userData.id}`
            )
            .catch(() => ({ achievements: [] }))
        ])
        setPortfolioItems(portfolioData)
        setAchievements(rewardsData.achievements ?? [])
      } catch (err) {
        console.error('Error fetching user profile:', err)
        setError('Пользователь не найден')
      } finally {
        setLoading(false)
      }
    }

    fetchUserProfile()
  }, [nickname])

  const formatDate = (dateString: string) =>
    new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })

  const renderStars = (rating: number) => {
    const stars: JSX.Element[] = []
    const fullStars = Math.floor(rating)
    const hasHalfStar = rating % 1 >= 0.5

    for (let i = 0; i < fullStars; i += 1) {
      stars.push(
        <span key={`full-${i}`} className={`${styles.star} ${styles.starFilled}`}>
          ★
        </span>,
      )
    }

    if (hasHalfStar) {
      stars.push(
        <span key="half" className={`${styles.star} ${styles.starHalf}`}>
          ★
        </span>,
      )
    }

    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0)
    for (let i = 0; i < emptyStars; i += 1) {
      stars.push(
        <span key={`empty-${i}`} className={styles.star}>
          ☆
        </span>,
      )
    }

    return stars
  }

  if (loading) {
    return (
      <>
        <Header />
        <main className={styles.page}>
          <div className={styles.container}>
            <div className={styles.loading}>
              <div className={styles.spinner} />
              <p>Загрузка профиля…</p>
            </div>
          </div>
        </main>
        <Footer />
      </>
    )
  }

  if (error || !profile) {
    return (
      <>
        <Header />
        <main className={styles.page}>
          <div className={styles.container}>
            <div className={styles.error}>
              <h1>Пользователь не найден</h1>
              <p>Возможно, профиль был удалён или ссылка указана неверно.</p>
              <Link href="/" className={styles.backButton}>
                Вернуться на главную
              </Link>
            </div>
          </div>
        </main>
        <Footer />
      </>
    )
  }

  const isOwnProfile = currentUser?.nickname === profile.nickname
  const bestRating = Math.max(profile.customer_rating ?? 0, profile.executor_rating ?? 0)
  const isVerified = Boolean(profile.admin_verified || profile.phone_verified)

  return (
    <>
      <Header />

      <main className={styles.page}>
        <div className={styles.container}>
          <header className={styles.profileHeader}>
            <div className={styles.avatar}>
              {profile.photo ? (
                <img src={profile.photo} alt={profile.name} className={styles.avatarImage} />
              ) : (
                <span>{profile.name.charAt(0).toUpperCase()}</span>
              )}
            </div>

            <div className={styles.info}>
              <div className={styles.nameRow}>
                <h1 className={styles.name}>{profile.name}</h1>
                {isVerified && <span className={styles.verified}>✓</span>}
              </div>
              <p className={styles.nickname}>@{profile.nickname}</p>
              {profile.description && <p className={styles.bio}>{profile.description}</p>}

              <div className={styles.stats}>
                <div className={styles.stat}>
                  <span className={styles.statLabel}>Рейтинг</span>
                  <span className={styles.statValue}>{bestRating.toFixed(1)}</span>
                  <div className={styles.stars}>{renderStars(bestRating)}</div>
                </div>
                <div className={styles.stat}>
                  <span className={styles.statLabel}>Заказов выполнено</span>
                  <span className={styles.statValue}>{profile.done_count}</span>
                </div>
                <div className={styles.stat}>
                  <span className={styles.statLabel}>На платформе с</span>
                  <span className={styles.statValue}>{formatDate(profile.created_at)}</span>
                </div>
              </div>
            </div>

            {!isOwnProfile && isAuthenticated && (
              <div className={styles.actions}>
                <Link href={`/chats/start/${profile.id}`} className={styles.actionButton}>
                  Написать сообщение
                </Link>
              </div>
            )}
          </header>

          <section className={styles.content}>
            {profile.specification && (
              <article className={styles.section}>
                <h2 className={styles.sectionTitle}>Специализация</h2>
                <div className={styles.skills}>
                  <span className={styles.skillTag}>{profile.specification}</span>
                </div>
              </article>
            )}

            {portfolioItems.length > 0 && (
              <article className={styles.section}>
                <h2 className={styles.sectionTitle}>Работы</h2>
                <div className={styles.portfolioGrid}>
                  {portfolioItems.map((item) => (
                    <article key={item.id} className={styles.portfolioCard}>
                      {item.media_url ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={item.media_url} alt={item.title} className={styles.portfolioPreview} />
                      ) : (
                        <div className={styles.portfolioPlaceholder}>🖼️</div>
                      )}
                      <div className={styles.portfolioInfo}>
                        <h3 className={styles.portfolioTitle}>{item.title}</h3>
                        {item.description && <p className={styles.portfolioDescription}>{item.description}</p>}
                        <div className={styles.portfolioMeta}>
                          <span>
                            {item.created_at
                              ? new Date(item.created_at).toLocaleDateString('ru-RU')
                              : 'Дата не указана'}
                          </span>
                          {item.tags && <span className={styles.portfolioTags}>{item.tags}</span>}
                        </div>
                        {item.attachment_url && (
                          <a
                            href={item.attachment_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className={styles.outlineButton}
                          >
                            Смотреть проект
                          </a>
                        )}
                      </div>
                    </article>
                  ))}
                </div>
              </article>
            )}

            {achievements.length > 0 && (
              <article className={styles.section}>
                <h2 className={styles.sectionTitle}>Достижения</h2>
                <ul className={styles.achievementsList}>
                  {achievements.map((item) => (
                    <li key={item.id} className={styles.achievementItem}>
                      <span className={styles.achievementIcon}>{item.icon ?? '🏆'}</span>
                      <div className={styles.achievementContent}>
                        <p className={styles.achievementTitle}>{item.title}</p>
                        {item.description && <p className={styles.achievementDescription}>{item.description}</p>}
                      </div>
                    </li>
                  ))}
                </ul>
              </article>
            )}

            {profile.reviews && profile.reviews.length > 0 && (
              <article className={styles.section}>
                <h2 className={styles.sectionTitle}>Отзывы ({profile.reviews.length})</h2>
                <div className={styles.reviews}>
                  {profile.reviews.map((review: ReviewDTO) => (
                    <div key={review.id} className={styles.reviewCard}>
                      <div className={styles.reviewHeader}>
                        <div className={styles.reviewerInfo}>
                          <span className={styles.reviewerName}>{review.reviewer_name || 'Пользователь'}</span>
                          <span className={styles.reviewerNickname}>@{review.reviewer_nickname || 'user'}</span>
                        </div>
                        <div className={styles.reviewRating}>{renderStars(review.rate)}</div>
                      </div>
                      <p className={styles.reviewComment}>{review.text}</p>
                      <span className={styles.reviewDate}>{formatDate(review.created_at)}</span>
                    </div>
                  ))}
                </div>
              </article>
            )}
          </section>
        </div>
      </main>

      <Footer />
    </>
  )
}
