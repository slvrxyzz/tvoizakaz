import { MessageType } from './common.dto'

export interface MessageDTO {
  id: number
  chat_id?: number
  text: string
  sender_id: number
  sender_name: string
  sender_nickname: string
  created_at: string
  type?: string
  order_id?: number
  offer_price?: number
  offer_currency?: string
  message_type?: MessageType
  file_name?: string
  file_size?: number
  is_edited?: boolean
  is_deleted?: boolean
  edited_at?: string
}

export interface MessageListDTO {
  messages: MessageDTO[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface MessageCreateDTO {
  text: string
  message_type?: MessageType
  file_name?: string
  file_size?: number
}

