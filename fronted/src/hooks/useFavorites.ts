import { useState, useCallback, useEffect } from 'react'
import { useAuth } from '@/providers/AuthProvider'
import { apiClient } from '@/utils/apiClient'
import { FavoriteDTO, FavoriteListDTO, FavoriteStatusDTO } from '@/dto'

export const useFavorites = () => {
  const [favorites, setFavorites] = useState<FavoriteDTO[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const { isAuthenticated } = useAuth()

  const fetchFavorites = useCallback(async (pageNum: number = 1) => {
    if (!isAuthenticated) return

    try {
      setLoading(true)
      setError(null)
      
      const data = await apiClient.get<FavoriteListDTO>('/favorites/', { page: pageNum, limit: 10 })
      
      setFavorites(data.favorites || [])
      setTotal(data.total || 0)
      setPage(pageNum)
      setTotalPages(data.total_pages || 1)
    } catch (err) {
      console.error('Error fetching favorites:', err)
      setError('Ошибка загрузки избранного')
    } finally {
      setLoading(false)
    }
  }, [isAuthenticated])

  const removeFromFavorites = async (orderId: number): Promise<boolean> => {
    try {
      await apiClient.delete(`/favorites/${orderId}`)
      setFavorites(prev => prev.filter(fav => fav.order_id !== orderId))
      setTotal(prev => prev - 1)
      return true
    } catch (err) {
      console.error('Error removing favorite:', err)
      return false
    }
  }

  return {
    favorites,
    loading,
    error,
    total,
    page,
    totalPages,
    fetchFavorites,
    removeFromFavorites
  }
}

export const useFavoriteStatus = (orderId: number) => {
  const [isFavorite, setIsFavorite] = useState(false)
  const [favoriteCount, setFavoriteCount] = useState(0)
  const [loading, setLoading] = useState(false)
  const { isAuthenticated } = useAuth()

  const checkFavoriteStatus = useCallback(async () => {
    if (!isAuthenticated || orderId <= 0) return

    try {
      setLoading(true)
      const data = await apiClient.get<FavoriteStatusDTO>(`/favorites/${orderId}/status`)
      setIsFavorite(data.is_favorite)
      setFavoriteCount(data.favorite_count)
    } catch (err) {
      console.error('Error checking favorite status:', err)
    } finally {
      setLoading(false)
    }
  }, [isAuthenticated, orderId])

  const toggleFavorite = async (): Promise<boolean> => {
    if (!isAuthenticated) return false

    try {
      setLoading(true)
      
      if (isFavorite) {
        await apiClient.delete(`/favorites/${orderId}`)
      } else {
        await apiClient.post(`/favorites/${orderId}`)
      }

      setIsFavorite(!isFavorite)
      setFavoriteCount(prev => isFavorite ? prev - 1 : prev + 1)
      return true
    } catch (err) {
      console.error('Error toggling favorite:', err)
      return false
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (orderId > 0 && isAuthenticated) {
      checkFavoriteStatus()
    }
  }, [orderId, isAuthenticated, checkFavoriteStatus])

  return {
    isFavorite,
    favoriteCount,
    loading,
    toggleFavorite
  }
}



