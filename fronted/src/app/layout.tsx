import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { AuthProvider } from '@/providers/AuthProvider'
import { WebSocketProvider } from '@/providers/WebSocketProvider'
import WebSocketConnector from '@/components/WebSocketConnector'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Teen Freelance',
  description: 'Фриланс платформа для школьников и студентов',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ru">
      <body className={inter.className}>
        <AuthProvider>
          <WebSocketProvider>
            <WebSocketConnector />
            <div style={{ flex: '1 0 auto' }}>
              {children}
            </div>
          </WebSocketProvider>
        </AuthProvider>
      </body>
    </html>
  )
}