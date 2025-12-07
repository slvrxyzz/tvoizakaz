'use client'

import { useCallback, useEffect, useMemo, useState } from 'react'
import { useRouter } from 'next/navigation'

import Footer from '@/components/layout/Footer'
import Header from '@/components/layout/Header'
import { ProfileHeaderSection } from '@/components/profile/ProfileHeaderSection'
import { ProfileInfoTab } from '@/components/profile/ProfileInfoTab'
import { ProfileLoadingState } from '@/components/profile/ProfileLoadingState'
import { ProfileOrdersTab } from '@/components/profile/ProfileOrdersTab'
import { ProfilePortfolioTab } from '@/components/profile/ProfilePortfolioTab'
import { ProfileSettingsTab } from '@/components/profile/ProfileSettingsTab'
import { ProfileSidebar } from '@/components/profile/ProfileSidebar'
import styles from '@/components/profile/ProfilePage.module.css'
import { OrderDTO, OrderListDTO, OrderStatus, UserProfileResponseDTO } from '@/dto'
import { useAuth } from '@/providers/AuthProvider'
import { apiClient } from '@/utils/apiClient'

type ProfileTab = 'info' | 'orders' | 'portfolio' | 'settings'

export default function ProfilePage() {
  const router = useRouter()
  const { user: currentUser, isAuthenticated, loading: authLoading, refreshUser } = useAuth()

  const [user, setUser] = useState<UserProfileResponseDTO | null>(null)
  const [activeOrders, setActiveOrders] = useState<OrderDTO[]>([])
  const [completedOrders, setCompletedOrders] = useState<OrderDTO[]>([])
  const [activeTab, setActiveTab] = useState<ProfileTab>('info')
  const [isEditing, setIsEditing] = useState(false)
  const [editForm, setEditForm] = useState<Partial<UserProfileResponseDTO>>({})
  const [loading, setLoading] = useState(true)
  const [initialized, setInitialized] = useState(false)

  const fetchUserProfile = useCallback(async () => {
    try {
      setLoading(true)
      const data = await apiClient.get<UserProfileResponseDTO>('/users/me')
      setUser(data)
      setEditForm(data)
    } catch (error) {
      console.error('Error loading user data:', error)
      router.push('/login')
    } finally {
      setLoading(false)
    }
  }, [router])

  const fetchUserOrders = useCallback(async () => {
    try {
      const data = await apiClient.get<OrderListDTO>('/orders/my')
      const orders = data.orders ?? []
      setActiveOrders(orders.filter((order) => [OrderStatus.OPEN, OrderStatus.WORK, OrderStatus.REVIEW].includes(order.status as OrderStatus)))
      setCompletedOrders(orders.filter((order) => order.status === OrderStatus.CLOSE))
    } catch (error) {
      console.error('Error fetching orders:', error)
      setActiveOrders([])
      setCompletedOrders([])
    }
  }, [])

  useEffect(() => {
    if (authLoading) {
      return
    }

    if (!isAuthenticated || !currentUser) {
      router.push('/login')
      return
    }

    if (initialized) {
      return
    }

    const loadData = async () => {
      try {
        await Promise.all([fetchUserProfile(), fetchUserOrders()])
      } finally {
        setInitialized(true)
      }
    }

    loadData().catch((error) => console.error(error))
  }, [
    authLoading,
    isAuthenticated,
    currentUser,
    router,
    initialized,
    fetchUserProfile,
    fetchUserOrders,
  ])

  const handleEditChange = (field: keyof UserProfileResponseDTO, value: string) => {
    setEditForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleSaveProfile = async () => {
    if (!user) {
      return
    }

    try {
      const updated = await apiClient.put<UserProfileResponseDTO>('/users/me', editForm)
      setUser(updated)
      setEditForm(updated)
      setIsEditing(false)
      await refreshUser().catch(() => undefined)
    } catch (error) {
      console.error('Error saving profile:', error)
    }
  }

  const handleCancelEdit = () => {
    if (user) {
      setEditForm(user)
    }
    setIsEditing(false)
  }

  const balance = useMemo(
    () => Number(user?.balance ?? currentUser?.balance ?? 0),
    [user, currentUser]
  )
  const tfBalance = useMemo(
    () => Number(currentUser?.tf_balance ?? (user as { tf_balance?: number })?.tf_balance ?? 0),
    [user, currentUser]
  )

  if (loading || !user) {
    return (
      <>
        <Header />
        <main className={styles.page}>
          <ProfileLoadingState />
        </main>
        <Footer />
      </>
    )
  }

  return (
    <>
      <Header />

      <main className={styles.page}>
        <ProfileHeaderSection user={user} />

        <div className={styles.container}>
          <div className={styles.contentLayout}>
            <ProfileSidebar
              balance={balance}
              tfBalance={tfBalance}
              activeTab={activeTab}
              onTabChange={setActiveTab}
            />

            <section className={styles.main}>
              {activeTab === 'info' && (
                <ProfileInfoTab
                  user={user}
                  editForm={editForm}
                  isEditing={isEditing}
                  onEditToggle={setIsEditing}
                  onChange={handleEditChange}
                  onSave={handleSaveProfile}
                  onCancel={handleCancelEdit}
                />
              )}

              {activeTab === 'orders' && (
                <ProfileOrdersTab activeOrders={activeOrders} completedOrders={completedOrders} />
              )}

              {activeTab === 'portfolio' && <ProfilePortfolioTab />}

              {activeTab === 'settings' && <ProfileSettingsTab />}
            </section>
          </div>
        </div>
      </main>

      <Footer />
    </>
  )
}