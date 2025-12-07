export const isDevMode = () => {
  if (process.env.NEXT_PUBLIC_MODE !== undefined) {
    return process.env.NEXT_PUBLIC_MODE === 'dev'
  }
  return process.env.NODE_ENV === 'development'
}

export const getApiUrl = () => {
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
}

export const getWsUrl = () => {
  return process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws'
}

