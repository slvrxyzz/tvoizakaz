"use client"

import { useEffect, useMemo, useState } from 'react'
import Link from 'next/link'

import styles from './HomeSections.module.css'
import { formatCurrency } from '@/utils/currency'

interface OrderItem {
  id: number
  title: string
  description: string
  price: number
  currency: string
  term: number
}

interface OrdersCarouselProps {
  orders: OrderItem[]
  loading: boolean
}

const AUTO_SWITCH_INTERVAL = 5000

export function OrdersCarousel({ orders, loading }: OrdersCarouselProps) {
  const [current, setCurrent] = useState(0)
  const [touchStart, setTouchStart] = useState(0)
  const [touchEnd, setTouchEnd] = useState(0)

  useEffect(() => {
    if (orders.length === 0) {
      return
    }

    const timer = window.setInterval(() => {
      setCurrent((prev) => (prev === orders.length - 1 ? 0 : prev + 1))
    }, AUTO_SWITCH_INTERVAL)

    return () => window.clearInterval(timer)
  }, [orders.length])

  useEffect(() => {
    setCurrent(0)
  }, [orders.length])

  const handleTouchStart = (event: React.TouchEvent<HTMLDivElement>) => {
    setTouchStart(event.touches[0].clientX)
  }

  const handleTouchMove = (event: React.TouchEvent<HTMLDivElement>) => {
    setTouchEnd(event.touches[0].clientX)
  }

  const handleTouchEnd = () => {
    if (touchStart - touchEnd > 50) {
      setCurrent((prev) => (prev === orders.length - 1 ? 0 : prev + 1))
    }
    if (touchStart - touchEnd < -50) {
      setCurrent((prev) => (prev === 0 ? orders.length - 1 : prev - 1))
    }
  }

  const renderedOrders = useMemo(() => {
    return orders.map((order, index) => {
      const prev = (current - 1 + orders.length) % orders.length
      const next = (current + 1) % orders.length

      let transform = 'translateX(-50%) scale(0.85)'
      let opacity = 0
      let zIndex = 1

      if (index === current) {
        transform = 'translateX(-50%) scale(1)'
        opacity = 1
        zIndex = 3
      } else if (index === prev) {
        transform = 'translateX(calc(-50% - 260px)) scale(0.9)'
        opacity = 0.5
        zIndex = 2
      } else if (index === next) {
        transform = 'translateX(calc(-50% + 260px)) scale(0.9)'
        opacity = 0.5
        zIndex = 2
      }

      return (
        <div
          key={order.id}
          className={styles.orderCard}
          style={{ transform, opacity, zIndex }}
        >
          <span className={styles.orderBadge}>Новый заказ</span>
          <h3>{order.title}</h3>
          <p>{order.description}</p>
          <div className={styles.orderMeta}>
            <span className={styles.orderPrice}>{formatCurrency(order.price, order.currency)}</span>
            <span>Срок: {order.term} дн.</span>
          </div>
          <Link href={`/orders/${order.id}`} className={styles.orderAction}>
            Откликнуться
          </Link>
        </div>
      )
    })
  }, [orders, current])

  if (loading) {
    return (
      <section className={styles.section}>
        <div className={styles.container}>
          <div className={styles.sectionHeader}>
            <h2 className={styles.sectionTitle}>Популярные заказы</h2>
            <p className={styles.sectionSubtitle}>Самые интересные проекты ждут своих исполнителей</p>
          </div>
          <div className={styles.loadingState}>Загрузка популярных заказов…</div>
        </div>
      </section>
    )
  }

  if (orders.length === 0) {
    return (
      <section className={styles.section}>
        <div className={styles.container}>
          <div className={styles.sectionHeader}>
            <h2 className={styles.sectionTitle}>Популярные заказы</h2>
            <p className={styles.sectionSubtitle}>Самые интересные проекты ждут своих исполнителей</p>
          </div>
          <div className={styles.emptyState}>Популярные заказы не найдены</div>
        </div>
      </section>
    )
  }

  return (
    <section className={styles.section}>
      <div className={styles.container}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>Популярные заказы</h2>
          <p className={styles.sectionSubtitle}>Самые интересные проекты ждут своих исполнителей</p>
        </div>

        <div
          className={`${styles.carousel} ${styles.carouselViewport}`}
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
        >
          <button
            type="button"
            className={`${styles.carouselButton} ${styles.carouselButtonPrev}`}
            onClick={() => setCurrent((prev) => (prev === 0 ? orders.length - 1 : prev - 1))}
            aria-label="Предыдущий заказ"
          >
            ‹
          </button>

          <div className={styles.carouselTrack}>{renderedOrders}</div>

          <button
            type="button"
            className={`${styles.carouselButton} ${styles.carouselButtonNext}`}
            onClick={() => setCurrent((prev) => (prev === orders.length - 1 ? 0 : prev + 1))}
            aria-label="Следующий заказ"
          >
            ›
          </button>
        </div>

        <div className={styles.carouselDots}>
          {orders.map((order, index) => (
            <button
              key={order.id}
              type="button"
              className={`${styles.carouselDot} ${index === current ? styles.carouselDotActive : ''}`}
              onClick={() => setCurrent(index)}
              aria-label={`Показать заказ ${order.title}`}
            />
          ))}
        </div>
      </div>
    </section>
  )
}

