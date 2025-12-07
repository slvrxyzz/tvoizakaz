export interface ReviewDTO {
  id: number
  type: string
  rate: number
  text: string
  response?: string
  sender_id: number
  reviewee_id: number
  order_id: number
  created_at: string
  reviewer_name?: string
  reviewer_nickname?: string
}

export interface ReviewCreateDTO {
  rate: number
  text: string
}

