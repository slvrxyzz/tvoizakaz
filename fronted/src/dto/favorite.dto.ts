export interface FavoriteDTO {
  id: number
  order_id: number
  title: string
  description: string
  price: number
  currency: string
  term: number
  status: string
  priority: string
  responses: number
  created_at: string
  customer_id: number
  category_id: number
  category_name: string
  customer_name: string
  customer_nickname: string
  favorited_at: string
}

export interface FavoriteListDTO {
  favorites: FavoriteDTO[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface FavoriteStatusDTO {
  is_favorite: boolean
  favorite_count: number
}

