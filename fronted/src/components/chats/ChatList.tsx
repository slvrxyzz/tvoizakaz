import { ChatDTO } from '@/dto'

import styles from './ChatsPage.module.css'

interface ChatListProps {
  chats: ChatDTO[]
  selectedChatId: number | null
  currentUserId: number
  unreadCount: number
  connectionStatus: 'connected' | 'connecting' | 'disconnected' | 'error'
  onSelect: (chat: ChatDTO) => void
  onRetryConnection: () => void
}

const getParticipantName = (chat: ChatDTO, currentUserId: number) => {
  return chat.customer_id === currentUserId ? chat.executor_name : chat.customer_name
}

const getParticipantInitial = (chat: ChatDTO, currentUserId: number) => {
  return getParticipantName(chat, currentUserId).charAt(0).toUpperCase()
}

export function ChatList({ chats, selectedChatId, currentUserId, connectionStatus, onSelect, onRetryConnection }: ChatListProps) {
  if (connectionStatus === 'connecting') {
    return (
      <div className={styles.loadingPanel}>
        <div className={styles.loadingSpinner}></div>
        <p>Подключение к чатам…</p>
      </div>
    )
  }

  if (connectionStatus === 'error') {
    return (
      <div className={styles.errorPanel}>
        <p>Ошибка подключения к чатам</p>
        <button className={styles.retryButton} onClick={onRetryConnection}>
          Переподключиться
        </button>
      </div>
    )
  }

  if (chats.length === 0) {
    return (
      <div className={styles.emptyPanel}>
        <p>У вас пока нет чатов</p>
      </div>
    )
  }

  return (
    <div className={styles.list}>
      {chats.map((chat) => {
        const participantName = getParticipantName(chat, currentUserId)
        const isActive = selectedChatId === chat.id

        return (
          <button
            key={chat.id}
            type="button"
            className={`${styles.chatItemContainer} ${isActive ? styles.chatItemActive : ''}`}
            onClick={() => onSelect(chat)}
          >
            <div className={styles.chatAvatar}>{getParticipantInitial(chat, currentUserId)}</div>
            <div className={styles.chatDetails}>
              <div className={styles.chatName}>{participantName}</div>
              <div className={styles.chatPreview}>{chat.last_message?.text || 'Нет сообщений'}</div>
            </div>
            <div className={styles.chatTime}>
              {chat.last_message ? new Date(chat.last_message.created_at).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }) : ''}
            </div>
          </button>
        )
      })}
    </div>
  )
}
