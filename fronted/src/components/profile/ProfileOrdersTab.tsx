import Link from 'next/link'

import { OrderDTO, OrderStatus } from '@/dto'
import { formatCurrency } from '@/utils/currency'

import styles from './ProfilePage.module.css'

interface ProfileOrdersTabProps {
  activeOrders: OrderDTO[]
  completedOrders: OrderDTO[]
}

const STATUS_CONFIG: Record<OrderStatus, { text: string; color: string }> = {
  [OrderStatus.OPEN]: { text: 'Открыт', color: '#1ed760' },
  [OrderStatus.WORK]: { text: 'В работе', color: '#ffb347' },
  [OrderStatus.REVIEW]: { text: 'На проверке', color: '#4d88ff' },
  [OrderStatus.CLOSE]: { text: 'Завершен', color: '#888888' },
}

export function ProfileOrdersTab({ activeOrders, completedOrders }: ProfileOrdersTabProps) {
  const renderStatusBadge = (status: OrderStatus) => {
    const config = STATUS_CONFIG[status]
    return (
      <span className={styles.statusBadge} style={{ backgroundColor: config.color }}>
        {config.text}
      </span>
    )
  }

  const renderOrderCard = (order: OrderDTO) => (
    <div key={order.id} className={styles.orderCard}>
      <div className={styles.orderHeader}>
        <div>
          <h3>{order.title}</h3>
          <p>{order.description}</p>
        </div>
        <div className={styles.orderActions}>{renderStatusBadge(order.status as OrderStatus)}</div>
      </div>
      <div className={styles.orderMeta}>
        <span className={styles.orderPrice}>{formatCurrency(order.price, order.currency)}</span>
        <span>Срок: {order.term} дней</span>
      </div>
      <Link href={`/orders/${order.id}`} className={styles.orderActionButton}>
        Перейти к заказу
      </Link>
    </div>
  )

  return (
    <section className={styles.ordersSections}>
      <div>
        <h2 className={styles.tabTitle}>Активные заказы</h2>
        {activeOrders.length > 0 ? (
          <div className={styles.ordersList}>{activeOrders.map(renderOrderCard)}</div>
        ) : (
          <div className={styles.emptyState}>
            <p>Нет активных заказов</p>
            <Link href="/orders">Найти заказы</Link>
          </div>
        )}
      </div>

      <div>
        <h2 className={styles.tabTitle}>История заказов</h2>
        {completedOrders.length > 0 ? (
          <div className={styles.ordersList}>{completedOrders.map(renderOrderCard)}</div>
        ) : (
          <div className={styles.emptyState}>
            <p>Нет завершенных заказов</p>
          </div>
        )}
      </div>
    </section>
  )
}
