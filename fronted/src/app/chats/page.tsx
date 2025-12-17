'use client'

import dynamic from 'next/dynamic'
import { Suspense, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

import Footer from '@/components/layout/Footer'
import Header from '@/components/layout/Header'
import { ChatList } from '@/components/chats/ChatList'
import { ChatWindow } from '@/components/chats/ChatWindow'
import { ChatsLayout } from '@/components/chats/ChatsLayout'
import styles from '@/components/chats/ChatsPage.module.css'
import { ChatDTO, OrderDTO } from '@/dto'
import { useAuth } from '@/providers/AuthProvider'
import { useWebSocketContext } from '@/providers/WebSocketProvider'
import { apiClient } from '@/utils/apiClient'

const ChatsContent = () => {
  const [selectedChat, setSelectedChat] = useState<ChatDTO | null>(null)
  const [orderInfo, setOrderInfo] = useState<OrderDTO | null>(null)
  const [newMessage, setNewMessage] = useState('')

  const { user, isAuthenticated, loading: authLoading } = useAuth()
  const router = useRouter()

  const {
    isConnected,
    connectionStatus,
    chats,
    messages,
    unreadCount,
    sendChatMessage,
    getChatMessages,
    getChats,
    clearNotifications,
  } = useWebSocketContext()

  useEffect(() => {
    if (!authLoading && (!isAuthenticated || !user)) {
      router.push('/login')
    }
  }, [authLoading, isAuthenticated, user, router])

  useEffect(() => {
    if (isConnected) getChats()
  }, [isConnected, getChats])

  useEffect(() => {
    if (typeof window === 'undefined' || chats.length === 0) return
    const chatIdParam = new URLSearchParams(window.location.search).get('chat_id')
    if (!chatIdParam) return
    const chatId = Number(chatIdParam)
    const chat = chats.find((item) => item.id === chatId)
    if (chat) setSelectedChat(chat)
  }, [chats])

  useEffect(() => {
    if (selectedChat && isConnected) {
      getChatMessages(selectedChat.id)
    }
  }, [selectedChat, isConnected, getChatMessages])

  useEffect(() => {
    clearNotifications()
  }, [clearNotifications])

  const handleSendMessage = () => {
    if (!newMessage.trim() || !selectedChat || connectionStatus !== 'connected') return
    const success = sendChatMessage(selectedChat.id, newMessage)
    if (success) setNewMessage('')
  }

  const handleFetchOrderInfo = async (orderId: number) => {
    try {
      const order = await apiClient.get<OrderDTO>(`/orders/${orderId}`)
      setOrderInfo(order)
    } catch (error) {
      console.error('Error fetching order info:', error)
    }
  }

  if (authLoading) {
    return (
      <>
        <Header />
        <main className={styles.page}>
          <div className={styles.loadingPanel}>
            <div className={styles.loadingSpinner}></div>
            <p>Проверка авторизации...</p>
          </div>
        </main>
        <Footer />
      </>
    )
  }

  if (!isAuthenticated || !user) return null

  return (
    <>
      <Header />
      <ChatsLayout
        sidebar={
          <>
            <div className={styles.header}>
              <div className={styles.title}>
                <h2>Чаты</h2>
                <div className={styles.connectionStatus}>
                  {connectionStatus === 'connected' && <span>🟢</span>}
                  {connectionStatus === 'connecting' && <span>🟡</span>}
                  {connectionStatus === 'disconnected' && <span>🔴</span>}
                  {connectionStatus === 'error' && <span>🔴</span>}
                  {unreadCount > 0 && <span className={styles.unreadBadge}>{unreadCount}</span>}
                </div>
              </div>
              <button className={styles.newChatButton} type="button">
                + Новый чат
              </button>
            </div>

            <ChatList
              chats={chats}
              selectedChatId={selectedChat?.id ?? null}
              currentUserId={Number(user.id)}
              unreadCount={unreadCount}
              connectionStatus={connectionStatus}
              onSelect={(chat) => setSelectedChat(chat)}
              onRetryConnection={() => window.location.reload()}
            />
          </>
        }
      >
        <ChatWindow
          chat={selectedChat}
          messages={messages}
          orderInfo={orderInfo}
          connectionStatus={connectionStatus}
          newMessage={newMessage}
          onMessageChange={setNewMessage}
          onSend={handleSendMessage}
          onFetchOrder={handleFetchOrderInfo}
          onRefreshMessages={getChatMessages}
          currentUserId={Number(user.id)}
        />
      </ChatsLayout>
      <Footer />
    </>
  )
}

const ChatsPage = () => (
  <Suspense fallback={null}>
    <ChatsContent />
  </Suspense>
)

export default dynamic(() => Promise.resolve(ChatsPage), { ssr: false })
