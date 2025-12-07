import { ReactNode } from 'react'

import styles from './ChatsPage.module.css'

interface ChatsLayoutProps {
  sidebar: ReactNode
  children: ReactNode
}

export function ChatsLayout({ sidebar, children }: ChatsLayoutProps) {
  return (
    <main className={styles.page}>
      <div className={styles.container}>
        <aside className={styles.sidebar}>{sidebar}</aside>
        {children}
      </div>
    </main>
  )
}
