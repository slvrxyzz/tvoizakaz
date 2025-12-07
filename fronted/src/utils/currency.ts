import { CurrencyType } from '@/dto/common.dto'

export const getCurrencySymbol = (currency: CurrencyType | string | undefined): string => {
  if (!currency) {
    return '₽'
  }
  const normalized = typeof currency === 'string' ? currency.toUpperCase() : currency
  return normalized === CurrencyType.TF ? 'TF' : '₽'
}

export const formatCurrency = (value: number, currency: CurrencyType | string | undefined): string => {
  const amount = Number.isFinite(value) ? value : 0
  const symbol = getCurrencySymbol(currency)
  return `${new Intl.NumberFormat('ru-RU').format(amount)} ${symbol}`
}


