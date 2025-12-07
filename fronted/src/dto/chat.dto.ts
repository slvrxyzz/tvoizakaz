import { MessageDTO } from './message.dto'

export interface ChatDTO {
  id: number
  customer_id: number
  executor_id: number
  customer_name: string
  customer_nickname: string
  executor_name: string
  executor_nickname: string
  created_at: string
  last_message?: MessageDTO
}

export interface ChatListDTO {
  chats: ChatDTO[]
}

export type ChatSocketInboundEvent =
  | { type: 'connection_established'; user_id: number; timestamp: string }
  | { type: 'chats'; chats: ChatDTO[] }
  | { type: 'messages'; chat_id: number; messages: MessageDTO[] }
  | { type: 'new_message'; chat_id: number; message: MessageDTO }
  | { type: 'notification'; [key: string]: unknown }
  | { type: 'moderation'; message: string; sanitized?: string; [key: string]: unknown }
  | { type: 'error'; message: string }
  | { type: 'pong'; timestamp: string }
  | { type: string; [key: string]: unknown }

export type ChatSocketOutboundEvent =
  | { type: 'joinChat'; chat_id: number }
  | { type: 'leaveChat'; chat_id: number }
  | { type: 'sendMessage'; chat_id: number; message: string }
  | { type: 'getChats' }
  | { type: 'getMessages'; chat_id: number; after_id?: number }
  | { type: 'user_message'; user_id: number; message: string }
  | { type: 'ping' }



