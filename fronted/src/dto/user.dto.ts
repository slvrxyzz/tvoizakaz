import { ReviewDTO } from './review.dto'

export interface UserDTO {
  id: string
  name: string
  nickname: string
  email: string
  balance?: number
  tf_balance?: number
  customer_rating?: number
  executor_rating?: number
  admin_verified?: boolean
  phone_verified?: boolean
  phone_number?: string
  role?: string
}

export interface UserPublicProfileDTO {
  id: number
  name: string
  nickname: string
  specification: string
  description?: string
  created_at: string
  photo?: string
  phone_verified: boolean
  admin_verified: boolean
  is_premium: boolean
  customer_rating: number
  executor_rating: number
  done_count: number
  taken_count: number
  reviews?: ReviewDTO[]
  role: string
}

export interface UserProfileResponseDTO {
  id: number
  name: string
  nickname: string
  email: string
  specification: string
  description?: string
  photo?: string
  balance: number
  tf_balance?: number
  customer_rating: number
  executor_rating: number
  done_count: number
  taken_count: number
  phone_verified: boolean
  admin_verified: boolean
  phone_number?: string
  created_at: string
  role: string
}

export interface UsersListResponseDTO {
  users: UserPublicProfileDTO[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface UserProfileUpdateDTO {
  name?: string
  description?: string
  specification?: string
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

