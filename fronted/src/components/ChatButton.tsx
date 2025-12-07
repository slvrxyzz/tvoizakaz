'use client'

import { useRouter } from 'next/navigation'
import { useAuth } from '@/providers/AuthProvider'

interface ChatButtonProps {
  userId: number
  userName?: string
}

export default function ChatButton({ userId, userName }: ChatButtonProps) {
  const router = useRouter()
  const { user, isAuthenticated } = useAuth()

  const handleClick = () => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }

    if (user?.id === userId) {
      return
    }

    router.push(`/chats/start/${userId}`)
  }

  if (!isAuthenticated || user?.id === userId) {
    return null
  }

  return (
    <button onClick={handleClick} className="chat-button">
      💬 Написать сообщение
    </button>
  )
}





