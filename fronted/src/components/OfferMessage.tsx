'use client'

import { MessageDTO } from '@/dto'
import { formatCurrency } from '@/utils/currency'

interface OfferMessageProps {
  message: MessageDTO
  isOwnMessage: boolean
  isOrderOwner: boolean
  isExecutor: boolean
  orderStatus?: string
  onCancel?: () => void
  onAccept?: () => void
  onSubmitForReview?: () => void
}

export default function OfferMessage({ 
  message, 
  isOwnMessage, 
  isOrderOwner, 
  isExecutor, 
  orderStatus,
  onCancel,
  onAccept,
  onSubmitForReview
}: OfferMessageProps) {
  if (message.type !== 'offer' || !message.offer_price || !message.order_id) {
    return null
  }

  return (
    <div className="offer-message">
      <div className="offer-header">
        <span className="offer-label">Предложение</span>
        <span className="offer-author">{message.sender_name}</span>
      </div>
      <div className="offer-content">
        <div className="offer-price">
          {formatCurrency(message.offer_price ?? 0, message.offer_currency)}
        </div>
        <div className="offer-date">{new Date(message.created_at).toLocaleString('ru-RU')}</div>
      </div>
    </div>
  )
}



