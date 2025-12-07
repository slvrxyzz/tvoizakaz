/**
 * Утилиты для работы с временем
 */

export function formatTime(dateString: string): string {
  try {
    // Парсим дату
    const date = new Date(dateString)
    
    // Проверяем, что дата валидна
    if (isNaN(date.getTime())) {
      console.error('Invalid date:', dateString)
      return 'недавно'
    }
    
    const now = new Date()
    const diff = now.getTime() - date.getTime()

    // Если разница отрицательная (дата в будущем), показываем "только что"
    if (diff < 0) return 'только что'
    
    if (diff < 60000) return 'только что'
    if (diff < 3600000) return `${Math.floor(diff / 60000)} мин назад`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)} ч назад`
    return date.toLocaleDateString('ru-RU')
  } catch (error) {
    console.error('Error formatting time:', error, dateString)
    return 'недавно'
  }
}

export function formatTimeOnly(dateString: string): string {
  try {
    const date = new Date(dateString)
    
    if (isNaN(date.getTime())) {
      console.error('Invalid date:', dateString)
      return 'недавно'
    }
    
    return date.toLocaleTimeString('ru-RU', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  } catch (error) {
    console.error('Error formatting time:', error, dateString)
    return 'недавно'
  }
}

export function formatDateTime(dateString: string): string {
  try {
    const date = new Date(dateString)
    
    if (isNaN(date.getTime())) {
      console.error('Invalid date:', dateString)
      return 'недавно'
    }
    
    return date.toLocaleString('ru-RU', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    console.error('Error formatting datetime:', error, dateString)
    return 'недавно'
  }
}

/**
 * Проверяет, является ли дата сегодняшней
 */
export function isToday(dateString: string): boolean {
  try {
    const date = new Date(dateString)
    const today = new Date()
    
    return date.getDate() === today.getDate() &&
           date.getMonth() === today.getMonth() &&
           date.getFullYear() === today.getFullYear()
  } catch (error) {
    return false
  }
}

/**
 * Проверяет, является ли дата вчерашней
 */
export function isYesterday(dateString: string): boolean {
  try {
    const date = new Date(dateString)
    const yesterday = new Date()
    yesterday.setDate(yesterday.getDate() - 1)
    
    return date.getDate() === yesterday.getDate() &&
           date.getMonth() === yesterday.getMonth() &&
           date.getFullYear() === yesterday.getFullYear()
  } catch (error) {
    return false
  }
}
