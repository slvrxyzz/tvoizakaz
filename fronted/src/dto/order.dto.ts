import { OrderStatus, OrderPriority, OrderType, CurrencyType } from './common.dto'

export interface OrderDTO {
  id: number
  title: string
  description: string
  price: number
  currency: CurrencyType
  term: number
  status: OrderStatus
  priority: OrderPriority
  order_type: OrderType
  responses: number
  created_at: string
  customer_id: number
  executor_id?: number
  category_id: number
  category_name: string
  customer_name: string
  customer_nickname: string
  customer_rating?: number
  customer_orders_count?: number
}

export interface OrderListDTO {
  orders: OrderDTO[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface OrderCreateDTO {
  title: string
  description: string
  price: number
  currency?: CurrencyType
  term: number
  category: string
  priority?: OrderPriority
  order_type?: OrderType
}

export interface OrderUpdateDTO {
  title?: string
  description?: string
  price?: number
  term?: number
}

export interface OrderRespondDTO {
  message: string
  price: number
}



