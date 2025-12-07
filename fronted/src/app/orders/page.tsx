'use client'

import { useEffect, useState } from 'react'

import Footer from '@/components/layout/Footer'
import Header from '@/components/layout/Header'
import { OrderDTO, OrderListDTO } from '@/dto'
import { OrdersFiltersSidebar } from '@/components/orders/OrdersFiltersSidebar'
import { OrdersHeader } from '@/components/orders/OrdersHeader'
import { OrdersList } from '@/components/orders/OrdersList'
import { OrdersSort } from '@/components/orders/OrdersSort'
import styles from '@/components/orders/OrdersPage.module.css'
import { apiClient } from '@/utils/apiClient'

export default function OrdersPage() {
  const [selectedSort, setSelectedSort] = useState('newest')
  const [orders, setOrders] = useState<OrderDTO[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchOrders()
  }, [])

  const fetchOrders = async () => {
    try {
      setLoading(true)
      const data = await apiClient.get<OrderListDTO>('/orders/', { page: 1, page_size: 50 })
      setOrders(data.orders || [])
    } catch (error) {
      console.warn('Error fetching orders (backend unavailable):', error)
      setOrders([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Header />

      <main className={styles.page}>
        <div className={styles.pageHeader}>
          <OrdersHeader />
        </div>

        <div className={styles.container}>
          <div className={styles.contentLayout}>
            <OrdersFiltersSidebar />

            <section className={styles.ordersContent}>
              <div className={styles.stats}>
                <span>{loading ? 'Загрузка заказов…' : `Найдено ${orders.length} заказов`}</span>
                <OrdersSort selected={selectedSort} onChange={setSelectedSort} />
              </div>

              <OrdersList orders={orders} loading={loading} />
            </section>
          </div>
        </div>
      </main>

      <Footer />
    </>
  )
}