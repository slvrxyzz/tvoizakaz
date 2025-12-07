"use client"

import { useCallback, useEffect, useMemo, useState } from 'react'

import Footer from '@/components/layout/Footer'
import Header from '@/components/layout/Header'
import { CategoriesSection } from '@/components/home/CategoriesSection'
import { HeroSection } from '@/components/home/HeroSection'
import { OrdersCarousel } from '@/components/home/OrdersCarousel'
import styles from '@/components/home/HomeSections.module.css'
import { CategoryDTO, OrderDTO, OrderListDTO } from '@/dto'
import { apiClient } from '@/utils/apiClient'

export default function HomePage() {
  const [categories, setCategories] = useState<CategoryDTO[]>([])
  const [orders, setOrders] = useState<OrderDTO[]>([])
  const [categoriesLoading, setCategoriesLoading] = useState(true)
  const [ordersLoading, setOrdersLoading] = useState(true)

  useEffect(() => {
    const loadCategories = async () => {
      try {
        const data = await apiClient.get<CategoryDTO[]>('/categories/')
        setCategories(data ?? [])
      } catch (error) {
        console.warn('Failed to load categories (backend unavailable)', error)
        setCategories([])
      } finally {
        setCategoriesLoading(false)
      }
    }

    const loadOrders = async () => {
      try {
        const data = await apiClient.get<OrderListDTO>('/orders/', { page: 1, page_size: 10 })
        setOrders((data.orders ?? []).slice(0, 5))
      } catch (error) {
        console.warn('Failed to load orders (backend unavailable)', error)
        setOrders([])
      } finally {
        setOrdersLoading(false)
      }
    }

    loadCategories()
    loadOrders()
  }, [])

  const renderCategoryEmoji = useCallback((category: CategoryDTO) => {
    const emojis: Record<string, string> = {
      'Дизайн': '🎨',
      'Копирайтинг': '✏️',
      'Программирование': '💻',
      'Соц сети и маркетинг': '📱',
      'Аудио и видео съёмка': '🎥',
      'Фотографии': '📷',
      'Помощь по бизнесу': '💡',
    }

    return emojis[category.name] || '⭐'
  }, [])

  const preparedOrders = useMemo(
    () =>
      orders.map((order) => ({
        id: order.id,
        title: order.title,
        description: order.description,
        price: order.price,
        currency: order.currency,
        term: order.term,
      })),
    [orders]
  )

  return (
    <>
      <Header />

      <main className={styles.page}>
        <div className={styles.pageHero}>
          <HeroSection
            title="Фриланс платформа для школьников и студентов"
            subtitle="Начни свою профессиональную карьеру уже сегодня!"
            ctaLabel="Присоединиться"
            ctaHref="/register"
          />
        </div>

        <CategoriesSection
          categories={categories}
          loading={categoriesLoading}
          renderEmoji={(category) => renderCategoryEmoji(category)}
        />

        <OrdersCarousel orders={preparedOrders} loading={ordersLoading} />
      </main>

      <Footer />
    </>
  )
}