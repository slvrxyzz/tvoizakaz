import styles from './ProfilePage.module.css'

interface ProfileSidebarProps {
  balance: number
  tfBalance: number
  activeTab: 'info' | 'orders' | 'portfolio' | 'settings'
  onTabChange: (tab: ProfileSidebarProps['activeTab']) => void
}

const TABS: Array<{ key: ProfileSidebarProps['activeTab']; label: string; icon: string }> = [
  { key: 'info', label: 'Основная информация', icon: '📊' },
  { key: 'orders', label: 'Мои заказы', icon: '📋' },
  { key: 'portfolio', label: 'Портфолио', icon: '🎨' },
  { key: 'settings', label: 'Настройки', icon: '⚙️' },
]

export function ProfileSidebar({ balance, tfBalance, activeTab, onTabChange }: ProfileSidebarProps) {
  return (
    <aside className={styles.sidebar}>
      <div className={styles.balanceCard}>
        <h3>Баланс</h3>
        <div className={styles.balanceRow}>
          <span className={styles.balanceAmount}>{balance.toLocaleString('ru-RU')}</span>
          <span className={styles.balanceCurrency}>₽</span>
        </div>
        <div className={styles.balanceRow}>
          <span className={styles.balanceAmount}>{tfBalance.toLocaleString('ru-RU')}</span>
          <span className={styles.balanceCurrency}>TF</span>
        </div>
        <button type="button" className={styles.balanceAction}>
          Пополнить баланс
        </button>
      </div>

      <nav className={styles.navList}>
        {TABS.map((tab) => (
          <button
            key={tab.key}
            type="button"
            className={`${styles.navButton} ${activeTab === tab.key ? styles.navButtonActive : ''}`}
            onClick={() => onTabChange(tab.key)}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </nav>
    </aside>
  )
}
