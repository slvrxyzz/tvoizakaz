'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useRouter } from 'next/navigation'

import { ApiError, apiClient } from '@/utils/apiClient'
import { UserDTO } from '@/dto'

interface AuthContextType {
  user: UserDTO | null
  loading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<UserDTO>
  logout: () => Promise<void>
  register: (data: any) => Promise<void>
  refreshUser: () => Promise<UserDTO | null>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<UserDTO | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      if (typeof window === 'undefined') {
        setLoading(false)
        return
      }

      const userData = await apiClient.get<UserDTO>('/auth/me')
      const normalizedUser = normalizeUser(userData)
      setUser(normalizedUser)
      localStorage.setItem('user', JSON.stringify(normalizedUser))
    } catch (error) {
      setUser(null)
      localStorage.removeItem('user')
      if (error instanceof ApiError && error.status === 401) {
        router.push('/login')
      } else if (error instanceof ApiError && error.status === 0) {
        // Backend is not available, silently ignore
        console.debug('Auth check skipped: backend unavailable')
      } else {
        console.warn('Auth check error:', error)
      }
    } finally {
      setLoading(false)
    }
  }

  const normalizeUser = (rawUser: UserDTO) => {
    const normalizedRole = (rawUser.role ?? 'CUSTOMER').toUpperCase()
    const supportFlag = Boolean((rawUser as any).is_support)
    return {
      ...rawUser,
      balance: Number(rawUser.balance ?? 0),
      tf_balance: Number((rawUser as any).tf_balance ?? 0),
      role: normalizedRole,
      is_support: supportFlag || normalizedRole === 'SUPPORT',
      admin_verified:
        Boolean(rawUser.admin_verified) ||
        supportFlag ||
        normalizedRole === 'ADMIN' ||
        normalizedRole === 'SUPPORT',
    }
  }

  const login = async (email: string, password: string) => {
    const data = await apiClient.post<{ token?: string; access_token?: string; user?: UserDTO }>('/auth/login', { email, password })
    
    // Сохраняем токен для WebSocket
    const token = data.token || data.access_token
    if (token && typeof window !== 'undefined') {
      localStorage.setItem('access_token', token)
    }
    
    if (data.user) {
      const normalized = normalizeUser(data.user)
      localStorage.setItem('user', JSON.stringify(normalized))
      setUser(normalized)
      return normalized
    }

    const userData = await apiClient.get<UserDTO>('/auth/me')
    const normalizedFallback = normalizeUser(userData)
    localStorage.setItem('user', JSON.stringify(normalizedFallback))
    setUser(normalizedFallback)
    return normalizedFallback
  }

  const logout = async () => {
    try {
      await apiClient.post('/auth/logout')
    } catch (error) {
      console.warn('Logout request failed:', error)
    }
    localStorage.removeItem('user')
    localStorage.removeItem('access_token')
    setUser(null)
  }

  const register = async (data: any) => {
    const registerData = {
      name: data.name,
      email: data.email,
      nickname: data.nickname,
      password: data.password,
      passwordConfirm: data.passwordConfirm,
      specification: data.specification || '',
      phone: data.phone || '',
      description: data.description || '',
      role: data.role || ''
    }
    const response = await apiClient.post<{ token?: string; access_token?: string; user?: UserDTO }>('/auth/register', registerData)
    
    // Сохраняем токен для WebSocket
    const token = response.token || response.access_token
    if (token && typeof window !== 'undefined') {
      localStorage.setItem('access_token', token)
    }
    
    if (response.user) {
      const normalized = normalizeUser(response.user)
      localStorage.setItem('user', JSON.stringify(normalized))
      setUser(normalized)
      return { ...response, user: normalized }
    }

    const userData = await apiClient.get<UserDTO>('/auth/me')
    const normalizedUser = normalizeUser(userData)
    localStorage.setItem('user', JSON.stringify(normalizedUser))
    setUser(normalizedUser)
    return { ...response, user: normalizedUser }
  }

  const refreshUser = async () => {
    try {
      const userData = await apiClient.get<UserDTO>('/auth/me')
      const normalized = normalizeUser(userData)
      setUser(normalized)
      if (typeof window !== 'undefined') {
        localStorage.setItem('user', JSON.stringify(normalized))
      }
      return normalized
    } catch (error) {
      console.warn('Refresh user error:', error)
      return null
    }
  }

  return (
    <AuthContext.Provider value={{
      user,
      loading,
      isAuthenticated: !!user,
      login,
      logout,
      register,
      refreshUser
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}



