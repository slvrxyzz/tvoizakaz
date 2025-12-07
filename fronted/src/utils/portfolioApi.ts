import { apiClient } from './apiClient'

export interface PortfolioItem {
  id: number
  title: string
  description?: string
  media_url?: string
  attachment_url?: string
  tags?: string
  is_featured: boolean
  created_at: string
}

export interface CreatePortfolioPayload {
  title: string
  description?: string
  media_url?: string
  attachment_url?: string
  tags?: string
  is_featured?: boolean
}

export const portfolioApi = {
  listMine: () => apiClient.get<PortfolioItem[]>('/portfolio/me'),
  listUser: (userId: number) => apiClient.get<PortfolioItem[]>(`/portfolio/users/${userId}`),
  create: (payload: CreatePortfolioPayload) => apiClient.post<PortfolioItem>('/portfolio', payload),
  update: (id: number, payload: Partial<CreatePortfolioPayload>) =>
    apiClient.put<PortfolioItem>(`/portfolio/${id}`, payload),
  remove: (id: number) => apiClient.delete<{ success: boolean }>(`/portfolio/${id}`),
  upload: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await apiClient.request<{ url: string }>('/portfolio/upload', {
      method: 'POST',
      body: formData
    })
    return response.url
  },
  achievementsBoard: () => apiClient.get<{ items: Array<{ id: number; title: string; description?: string; icon?: string; awarded_at: string }> }>('/portfolio/achievements')
}



