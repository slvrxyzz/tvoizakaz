import { OrderDTO } from '@/dto'

import styles from './OrdersPage.module.css'
import { OrderCard } from './OrderCard'

interface OrdersListProps {
  orders: OrderDTO[]
  loading: boolean
}

export function OrdersList({ orders, loading }: OrdersListProps) {
  if (loading) {
    return (
      <div className={styles.loading}>
        <div className={styles.loadingSpinner} />
        <p>Загрузка заказов…</p>
      </div>
    )
  }

  if (orders.length === 0) {
    return <div className={styles.emptyState}>Заказы не найдены</div>
  }

  return (
    <div className={styles.ordersGrid}>
      {orders.map((order) => (
        <OrderCard key={order.id} order={order} />
      ))}
    </div>
  )
}
