export const isDevMode = () => {
  if (process.env.NEXT_PUBLIC_MODE !== undefined) {
    return process.env.NEXT_PUBLIC_MODE === 'dev'
  }
  return process.env.NODE_ENV === 'development'
}

export const getApiUrl = () => {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL
  }

  if (typeof window !== 'undefined') {
    return window.location.origin
  }

  return 'http://localhost:8000'
}

export const getWsUrl = () => {
  if (process.env.NEXT_PUBLIC_WS_URL) {
    return process.env.NEXT_PUBLIC_WS_URL
  }

  if (typeof window !== 'undefined') {
    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    return `${proto}//${window.location.host}`
  }

  return 'ws://localhost:8000'
}

