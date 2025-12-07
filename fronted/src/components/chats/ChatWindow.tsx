import Link from 'next/link'
import { useEffect, useMemo, useRef } from 'react'

import OfferMessage from '@/components/OfferMessage'
import { ChatDTO, MessageDTO, OrderDTO } from '@/dto'
import { formatTime } from '@/utils/timeUtils'

import styles from './ChatsPage.module.css'

interface ChatWindowProps {
  chat: ChatDTO | null
  messages: Record<number, MessageDTO[]>
  orderInfo: OrderDTO | null
  connectionStatus: 'connected' | 'connecting' | 'disconnected' | 'error'
  newMessage: string
  onMessageChange: (value: string) => void
  onSend: () => void
  onFetchOrder: (orderId: number) => void
  onRefreshMessages: (chatId: number) => void
  currentUserId: number
}

export function ChatWindow({
  chat,
  messages,
  orderInfo,
  connectionStatus,
  newMessage,
  onMessageChange,
  onSend,
  onFetchOrder,
  onRefreshMessages,
  currentUserId,
}: ChatWindowProps) {
  const messagesEndRef = useRef<HTMLDivElement | null>(null)

  const currentMessages = chat ? messages[chat.id] ?? [] : []
  const otherUserName = chat ? (chat.customer_id === currentUserId ? chat.executor_name : chat.customer_name) : ''
  const otherUserNickname = chat ? (chat.customer_id === currentUserId ? chat.executor_nickname : chat.customer_nickname) : ''

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, chat])

  const handleOfferAction = () => {
    if (chat) {
      onRefreshMessages(chat.id)
    }
  }

  const renderedMessages = useMemo(() => {
    return currentMessages.map((message) => {
      const isOwnMessage = message.sender_id === currentUserId

      if (message.type === 'offer' && message.offer_price) {
        if (message.order_id && !orderInfo) {
          onFetchOrder(message.order_id)
        }

        return (
          <OfferMessage
            key={message.id}
            message={message}
            isOwnMessage={isOwnMessage}
            isOrderOwner={!isOwnMessage}
            isExecutor={isOwnMessage}
            orderStatus={orderInfo?.status}
            onCancel={handleOfferAction}
            onAccept={handleOfferAction}
            onSubmitForReview={handleOfferAction}
          />
        )
      }

      return (
        <div
          key={message.id}
          className={`${styles.messageRow} ${isOwnMessage ? styles.messageSent : styles.messageReceived}`}
        >
          <div className={styles.messageBubble}>
            <div>{message.text}</div>
            <div className={styles.messageTime}>{formatTime(message.created_at)}</div>
          </div>
        </div>
      )
    })
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentMessages, currentUserId, orderInfo, onFetchOrder])

  if (!chat) {
    return (
      <div className={styles.emptyPanel}>
        <h3>Выберите чат</h3>
        <p>Выберите чат из списка слева, чтобы начать общение</p>
      </div>
    )
  }

  return (
    <div className={styles.main}>
      <header className={styles.mainHeader}>
        <Link href={`/users/${otherUserNickname}`} className={styles.userLink}>
          <div className={styles.headerUser}>
            <div className={styles.headerAvatar}>{otherUserName.charAt(0)}</div>
            <div className={styles.headerInfo}>
              <h3>{otherUserName}</h3>
              <p>@{otherUserNickname}</p>
            </div>
          </div>
        </Link>
      </header>

      <div className={styles.messages}>
        {renderedMessages}
        <div ref={messagesEndRef} />
      </div>

      <div className={styles.inputBar}>
        {connectionStatus !== 'connected' && (
          <span style={{ color: '#aa0000', fontSize: '0.9rem' }}>Нет соединения с сервером</span>
        )}
        <input
          className={styles.inputField}
          type="text"
          placeholder={connectionStatus === 'connected' ? 'Введите сообщение...' : 'Нет соединения'}
          value={newMessage}
          onChange={(event) => onMessageChange(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter') {
              onSend()
            }
          }}
          disabled={connectionStatus !== 'connected'}
        />
        <button
          className={styles.sendButton}
          onClick={onSend}
          disabled={!newMessage.trim() || connectionStatus !== 'connected'}
        >
          Отправить
        </button>
      </div>
    </div>
  )
}
