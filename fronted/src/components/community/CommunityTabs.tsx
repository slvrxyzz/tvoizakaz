import styles from './CommunityPage.module.css'
import type { TabKey } from './types'

interface CommunityTabsProps {
  activeTab: TabKey
  onChange: (tab: TabKey) => void
}

const tabs: Array<{ key: TabKey; label: string; icon: string }> = [
  { key: 'news', label: 'Новости', icon: '📰' },
  { key: 'articles', label: 'Статьи', icon: '📚' },
  { key: 'tests', label: 'Тесты', icon: '🧪' },
  { key: 'career', label: 'Профориентация', icon: '💼' },
]

export function CommunityTabs({ activeTab, onChange }: CommunityTabsProps) {
  return (
    <nav className={styles.tabs}>
      {tabs.map((tab) => (
        <button
          key={tab.key}
          type="button"
          className={`${styles.tabButton} ${activeTab === tab.key ? styles.tabButtonActive : ''}`}
          onClick={() => onChange(tab.key)}
        >
          <span aria-hidden>{tab.icon}</span> {tab.label}
        </button>
      ))}
    </nav>
  )
}
