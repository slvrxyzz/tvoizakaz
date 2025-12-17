import { getApiUrl } from './config'

interface ApiRequestOptions extends RequestInit {
  params?: Record<string, string | number>
}

export class ApiError extends Error {
  status?: number
  details?: unknown

  constructor(message: string, status?: number, details?: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.details = details
  }
}

class ApiClient {
  private baseUrl: string

  constructor() {
    this.baseUrl = getApiUrl()
  }

  private buildUrl(endpoint: string, params?: Record<string, string | number>): string {
    // Добавляем префикс /api/v1 если его нет
    const apiEndpoint = endpoint.startsWith('/api/v1') ? endpoint : `/api/v1${endpoint}`
    const url = new URL(`${this.baseUrl}${apiEndpoint}`)
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, String(value))
      })
    }
    return url.toString()
  }

  private async handleRealRequest(endpoint: string, options: ApiRequestOptions): Promise<Response> {
    const url = this.buildUrl(endpoint, options.params)

    const isFormData = typeof FormData !== 'undefined' && options.body instanceof FormData
    const headers: HeadersInit = {
      ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
      ...options.headers
    }

    // Добавляем токен из localStorage в заголовок Authorization (если есть)
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token')
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
    }

    try {
      return await fetch(url, {
        ...options,
        headers,
        credentials: options.credentials ?? 'include'
      })
    } catch (error) {
      // Network error - бэкенд недоступен
      throw new ApiError('Сервер временно недоступен', 0, error)
    }
  }

  async request<T = any>(endpoint: string, options: ApiRequestOptions = {}, retry = true): Promise<T> {
    const response = await this.handleRealRequest(endpoint, options)

    if (response.status === 401 && retry) {
      try {
        const refreshResponse = await this.handleRealRequest('/auth/refresh', { method: 'POST' })
        if (refreshResponse.ok) {
          return this.request<T>(endpoint, options, false)
        }
      } catch (refreshError) {
        // no-op, fall through to default handling
      }
    }

    if (!response.ok) {
      const errorBody = await response.json().catch(() => null)
      let errorMsg = 'Произошла ошибка. Повторите попытку позже.'

      if (errorBody && typeof errorBody === 'object') {
        const candidate = (errorBody as Record<string, unknown>).message ?? (errorBody as Record<string, unknown>).detail
        if (typeof candidate === 'string' && candidate.trim().length > 0) {
          errorMsg = candidate
        }
      }

      if (response.status === 401) {
        // Для эндпоинтов авторизации показываем "Неверный логин или пароль"
        // Для остальных - "Нужно войти в аккаунт"
        if (endpoint.includes('/auth/login') || endpoint.includes('/auth/register')) {
          errorMsg = 'Неверный логин или пароль'
        } else {
          errorMsg = 'Нужно войти в аккаунт'
        }
      } else if (response.status >= 500) {
        errorMsg = 'Сервис временно недоступен'
      }

      throw new ApiError(errorMsg, response.status, errorBody)
    }

    if (response.status === 204) {
      return undefined as T
    }

    const contentType = response.headers.get('content-type') || ''
    if (!contentType.includes('application/json')) {
      return undefined as T
    }

    return response.json() as Promise<T>
  }

  async get<T = any>(endpoint: string, params?: Record<string, string | number>): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET', params })
  }

  post<T = any>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  put<T = any>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }

  delete<T = any>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' })
  }
}

export const apiClient = new ApiClient()

