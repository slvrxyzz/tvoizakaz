export interface SearchResultDTO {
  id: number
  title: string
  description: string
  price: number
  status: string
  created_at: string
  customer_id: number
  customer_name: string
  customer_nickname: string
  category_id?: number
}

export interface SearchResponseDTO {
  results: SearchResultDTO[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface UserSearchResultDTO {
  id: number
  name: string
  nickname: string
  specification: string
  description: string
  customer_rating: number
  executor_rating: number
  done_count: number
  taken_count: number
}

export interface UserSearchResponseDTO {
  results: UserSearchResultDTO[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface SearchSuggestionsDTO {
  suggestions: {
    orders: string[]
    users: string[]
  }
}



