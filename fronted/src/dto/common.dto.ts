export enum OrderStatus {
  OPEN = 'OPEN',
  WORK = 'WORK',
  REVIEW = 'REVIEW',
  CLOSE = 'CLOSE'
}

export enum OrderPriority {
  LOW = 'LOW',
  NORMAL = 'NORMAL',
  HIGH = 'HIGH',
  URGENT = 'URGENT'
}

export enum OrderType {
  REGULAR = 'REGULAR',
  PREMIUM = 'PREMIUM',
  NEW = 'NEW'
}

export enum CurrencyType {
  RUB = 'RUB',
  TF = 'TF'
}

export enum MessageType {
  TEXT = 'text',
  FILE = 'file',
  IMAGE = 'image',
  AUDIO = 'audio',
  VIDEO = 'video'
}

export interface PaginationResponse<T> {
  total: number
  page: number
  page_size: number
  total_pages: number
  items?: T[]
}



