import { MouseEvent } from 'react'
import { useRouter } from 'next/navigation'

import styles from './OrdersPage.module.css'

interface OrdersHeaderProps {
  onCreate?: () => void
}

export function OrdersHeader({ onCreate }: OrdersHeaderProps) {
  const router = useRouter()

  const handleClick = (event: MouseEvent<HTMLButtonElement>) => {
    event.preventDefault()
    if (onCreate) {
      onCreate()
      return
    }
    router.push('/orders/create')
  }

  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <div className={styles.headerContent}>
          <h1 className={styles.title}>Найдите подходящий заказ</h1>
          <button type="button" className={styles.createButton} onClick={handleClick}>
            Разместить заказ
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 5v14M5 12h14" />
            </svg>
          </button>
        </div>
      </div>
    </header>
  )
}
