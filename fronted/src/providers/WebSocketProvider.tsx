'use client'

import { createContext, useContext, ReactNode, useRef, useEffect, useState, useCallback } from 'react'

import { ChatDTO, ChatSocketInboundEvent, ChatSocketOutboundEvent, MessageDTO } from '@/dto'

interface WebSocketContextType {
  isConnected: boolean
  connectionStatus: 'connected' | 'connecting' | 'disconnected' | 'error'
  reconnect: () => void
  send: (event: ChatSocketOutboundEvent) => boolean
  chats: ChatDTO[]
  messages: Record<number, MessageDTO[]>
  notifications: any[]
  unreadCount: number
  sendChatMessage: (chatId: number, message: string) => boolean
  getChatMessages: (chatId: number) => void
  getChats: () => void
  clearNotifications: () => void
  sendUserMessage: (userId: number, message: string) => boolean
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined)

export const WebSocketProvider = ({ children }: { children: ReactNode }) => {
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'connecting' | 'disconnected' | 'error'>('disconnected')
  const [chats, setChats] = useState<ChatDTO[]>([])
  const [messages, setMessages] = useState<Record<number, MessageDTO[]>>({})
  const [notifications, setNotifications] = useState<any[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  
  const wsRef = useRef<WebSocket | null>(null)

  const handleInboundEvent = useCallback((payload: ChatSocketInboundEvent) => {
    switch (payload.type) {
      case 'connection_established':
        setConnectionStatus('connected')
        break
      case 'chats':
        setChats(Array.isArray(payload.chats) ? payload.chats : [])
        break
      case 'messages': {
        const chatId = Number(payload.chat_id || payload.chatId || 0)
        if (!chatId) {
          return
        }
        setMessages((prev) => ({
          ...prev,
          [chatId]: Array.isArray(payload.messages) ? payload.messages : [],
        }))
        break
      }
      case 'new_message': {
        const chatId = Number(payload.chat_id || payload.chatId || 0)
        if (!chatId || !payload.message) {
          return
        }
        setMessages((prev) => ({
          ...prev,
          [chatId]: [...(prev[chatId] || []), payload.message],
        }))
        break
      }
      case 'notification':
        setNotifications((prev) => [...prev, payload])
        setUnreadCount((prev) => prev + 1)
        break
      case 'moderation':
        setNotifications((prev) => [...prev, payload])
        break
      case 'error':
        // eslint-disable-next-line no-console
        console.warn('WebSocket error event', payload)
        setConnectionStatus('error')
        break
      default:
        if (process.env.NODE_ENV === 'development') {
          // eslint-disable-next-line no-console
          console.debug('Unhandled WebSocket event', payload)
        }
    }
  }, [])

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    setConnectionStatus('connecting')
    
    // Получаем токен из localStorage или cookies
    let token: string | null = null
    if (typeof window !== 'undefined') {
      // Сначала пытаемся получить из localStorage
      token = localStorage.getItem('access_token')
      
      // Если нет в localStorage, пытаемся получить из cookie
      if (!token) {
        const cookies = document.cookie.split(';')
        const accessTokenCookie = cookies.find(c => c.trim().startsWith('access_token='))
        if (accessTokenCookie) {
          token = accessTokenCookie.split('=')[1]
        }
      }
    }
    
    // Используем базовый URL
    const wsBaseUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'
    const baseUrl = wsBaseUrl.replace(/\/ws$/, '')
    // Передаем токен через query параметр, если он есть
    const wsUrl = token 
      ? `${baseUrl}/api/v1/ws/chat?token=${encodeURIComponent(token)}`
      : `${baseUrl}/api/v1/ws/chat`
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      setConnectionStatus('connected')
    }

    ws.onmessage = (event) => {
      try {
        const parsed: ChatSocketInboundEvent = JSON.parse(event.data)
        handleInboundEvent(parsed)
      } catch (error) {
        if (process.env.NODE_ENV === 'development') {
          // eslint-disable-next-line no-console
          console.error('WebSocket payload parse error', error)
        }
      }
    }

    ws.onclose = () => {
      setConnectionStatus('disconnected')
    }

    ws.onerror = () => {
      setConnectionStatus('error')
    }

    wsRef.current = ws
  }, [handleInboundEvent])

  const reconnect = () => {
    if (wsRef.current) {
      wsRef.current.close()
    }
    connect()
  }

  const send = useCallback((event: ChatSocketOutboundEvent) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(event))
      return true
    }
    return false
  }, [])

  const sendChatMessage = useCallback((chatId: number, message: string) => {
    return send({ type: 'sendMessage', chat_id: chatId, message })
  }, [send])

  const sendUserMessage = useCallback((userId: number, message: string) => {
    return send({ type: 'user_message', user_id: userId, message })
  }, [send])

  const getChatMessages = useCallback((chatId: number) => {
    send({ type: 'getMessages', chat_id: chatId })
  }, [send])

  const getChats = useCallback(() => {
    send({ type: 'getChats' })
  }, [send])

  const clearNotifications = useCallback(() => {
    setNotifications([])
    setUnreadCount(0)
  }, [])

  useEffect(() => {
    // Подключаемся только если есть доступ к window (клиентская сторона)
    if (typeof window !== 'undefined') {
      connect()
      return () => {
        if (wsRef.current) {
          wsRef.current.close()
        }
      }
    }
  }, [connect])

  useEffect(() => {
    if (connectionStatus === 'connected') {
      getChats()
    }
  }, [connectionStatus, getChats])

  return (
    <WebSocketContext.Provider value={{ 
      isConnected: connectionStatus === 'connected',
      connectionStatus,
      reconnect,
      send,
      chats,
      messages,
      notifications,
      unreadCount,
      sendChatMessage,
      getChatMessages,
      getChats,
      clearNotifications,
      sendUserMessage
    }}>
      {children}
    </WebSocketContext.Provider>
  )
}

export const useWebSocketContext = () => {
  const context = useContext(WebSocketContext)
  if (!context) {
    throw new Error('useWebSocketContext must be used within WebSocketProvider')
  }
  return context
}
