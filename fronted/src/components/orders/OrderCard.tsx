import { OrderDTO } from '@/dto'
import { formatCurrency } from '@/utils/currency'

import styles from './OrdersPage.module.css'

interface OrderCardProps {
  order: OrderDTO
}

export function OrderCard({ order }: OrderCardProps) {
  return (
    <article className={styles.orderCard}>
      <div className={styles.orderHeader}>
        <div className={styles.customerInfo}>
          <div className={styles.avatar}>{order.customer_name.charAt(0)}</div>
          <div className={styles.customerDetails}>
            <span className={styles.customerName}>{order.customer_name}</span>
            <span className={styles.category}>{order.category_name}</span>
          </div>
        </div>
        <div className={styles.orderPrice}>{formatCurrency(order.price, order.currency)}</div>
      </div>

      <div className={styles.orderBody}>
        <h3 className={styles.orderTitle}>{order.title}</h3>
        <p className={styles.orderDescription}>{order.description}</p>
      </div>

      <div className={styles.orderFooter}>
        <div className={styles.orderMeta}>
          <span>{order.responses} откликов</span>
          <span>Срок: {order.term} дней</span>
        </div>
        <button type="button" className={styles.respondButton}>
          Откликнуться
        </button>
      </div>
    </article>
  )
}
