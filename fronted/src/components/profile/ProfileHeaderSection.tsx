import { UserProfileResponseDTO } from '@/dto'

import styles from './ProfilePage.module.css'

interface ProfileHeaderSectionProps {
  user: UserProfileResponseDTO
}

export function ProfileHeaderSection({ user }: ProfileHeaderSectionProps) {
  const initials = user.name ? user.name.charAt(0).toUpperCase() : user.nickname?.charAt(0).toUpperCase() || '?'

  return (
    <section className={styles.headerSection}>
      <div className={styles.container}>
        <div className={styles.headerContent}>
          <div className={styles.avatar}>
            <div className={styles.avatarPlaceholder}>{initials}</div>
            <div className={styles.headerInfo}>
              <h1>{user.name}</h1>
              <p className={styles.username}>@{user.nickname}</p>
              {user.admin_verified && <span className={styles.supportBadge}>Поддержка ✅</span>}
            </div>
          </div>

          <div className={styles.statsGrid}>
            <div className={styles.statCard}>
              <div className={styles.statValue}>{user.customer_rating}</div>
              <div className={styles.statLabel}>Рейтинг заказчика</div>
            </div>
            <div className={styles.statCard}>
              <div className={styles.statValue}>{user.executor_rating}</div>
              <div className={styles.statLabel}>Рейтинг исполнителя</div>
            </div>
            <div className={styles.statCard}>
              <div className={styles.statValue}>{user.done_count}</div>
              <div className={styles.statLabel}>Завершено заказов</div>
            </div>
            <div className={styles.statCard}>
              <div className={styles.statValue}>
                {new Date(user.created_at).toLocaleDateString('ru-RU')}
              </div>
              <div className={styles.statLabel}>С нами с</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
