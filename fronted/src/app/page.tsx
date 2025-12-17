"use client"

import Link from 'next/link'
import { useCallback, useEffect, useMemo, useState } from 'react'

import Footer from '@/components/layout/Footer'
import Header from '@/components/layout/Header'
import { CategoriesSection } from '@/components/home/CategoriesSection'
import { HeroSection } from '@/components/home/HeroSection'
import { OrdersCarousel } from '@/components/home/OrdersCarousel'
import styles from '@/components/home/HomeSections.module.css'
import { CategoryDTO, OrderDTO, OrderListDTO } from '@/dto'
import { apiClient } from '@/utils/apiClient'

const mockCategories: CategoryDTO[] = [
  { id: 1, name: 'Дизайн', description: 'Логотипы и фирстиль', created_at: '', updated_at: '' },
  { id: 2, name: 'Копирайтинг', description: 'Тексты и сценарии', created_at: '', updated_at: '' },
  { id: 3, name: 'Программирование', description: 'Web и боты', created_at: '', updated_at: '' },
];

const placeholderOrders: OrderDTO[] = [
  {
    id: -1,
    title: 'Тут мог бы быть ваш заказ',
    description: 'Разместите задачу, и исполнители откликнутся за пару минут.',
    price: 0,
    currency: 'RUB',
    term: 1,
    customer_name: 'TeenFreelance',
    category_name: 'Размещение заказа',
    status: 'open',
    responses: 0,
    created_at: '',
    updated_at: '',
    customer_id: 0,
  },
  {
    id: -2,
    title: 'Тут тоже мог быть ваш заказ',
    description: 'Опишите задачу — дизайн, тексты, код — и получите предложения.',
    price: 0,
    currency: 'RUB',
    term: 1,
    customer_name: 'TeenFreelance',
    category_name: 'Размещение заказа',
    status: 'open',
    responses: 0,
    created_at: '',
    updated_at: '',
    customer_id: 0,
  },
  {
    id: -3,
    title: 'А тут мог быть проект, с которым вы бы справились',
    description: 'Создайте задачу — исполнители уже готовы взяться за работу.',
    price: 0,
    currency: 'RUB',
    term: 1,
    customer_name: 'TeenFreelance',
    category_name: 'Размещение заказа',
    status: 'open',
    responses: 0,
    created_at: '',
    updated_at: '',
    customer_id: 0,
  },
];

export default function HomePage() {
  const [categories, setCategories] = useState<CategoryDTO[]>(mockCategories)
  const [orders, setOrders] = useState<OrderDTO[]>(placeholderOrders)
  const [categoriesLoading, setCategoriesLoading] = useState(false)
  const [ordersLoading, setOrdersLoading] = useState(false)

  useEffect(() => {
    setCategoriesLoading(true)
    setOrdersLoading(true)

    const loadCategories = async () => {
      try {
        const data = await apiClient.get<CategoryDTO[]>('/categories/')
        const result = data ?? []
        setCategories(result.length ? result : mockCategories)
      } catch (error) {
        console.warn('Failed to load categories (backend unavailable)', error)
        setCategories(mockCategories)
      } finally {
        setCategoriesLoading(false)
      }
    }

    const loadOrders = async () => {
      try {
        const data = await apiClient.get<OrderListDTO>('/orders/', { page: 1, page_size: 10 })
        const result = (data.orders ?? []).slice(0, 5)
        if (result.length) {
          setOrders(result)
        } else {
          setOrders(placeholderOrders)
        }
      } catch (error) {
        console.warn('Failed to load orders (backend unavailable)', error)
        setOrders(placeholderOrders)
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

        <div className={`${styles.container} ${styles.categoriesMore}`}>
          <Link href="/orders" className={styles.categoriesMoreButton}>
            Больше категорий
          </Link>
        </div>

        <OrdersCarousel orders={preparedOrders} loading={ordersLoading} />
      </main>

      <Footer />
    </>
  )
}