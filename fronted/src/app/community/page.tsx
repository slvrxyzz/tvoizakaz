'use client'

import { useCallback, useEffect, useState } from 'react'

import Footer from '@/components/layout/Footer'
import Header from '@/components/layout/Header'
import { ArticlesGrid } from '@/components/community/ArticlesGrid'
import { CareerGuide } from '@/components/community/CareerGuide'
import { CommunityHero } from '@/components/community/CommunityHero'
import { CommunityTabs } from '@/components/community/CommunityTabs'
import { NewsGrid } from '@/components/community/NewsGrid'
import { TestsGrid } from '@/components/community/TestsGrid'
import styles from '@/components/community/CommunityPage.module.css'
import type { ArticleItem, NewsItem, TabKey, TestItem } from '@/components/community/types'
import { apiClient } from '@/utils/apiClient'

interface ContentItem {
  id: number
  title: string
  content: string
  type: string
  status: string
  tags: string[]
  author_id: number
  author_name: string
  author_nickname: string
  created_at: string
  updated_at: string
  published_at?: string
  views: number
  likes: number
  is_published: boolean
}

const DEFAULT_TAB: TabKey = 'news'

const tabToContentType: Record<TabKey, string> = {
  news: 'news',
  articles: 'article',
  tests: 'test',
  career: 'career',
}

export default function CommunityPage() {
  const [activeTab, setActiveTab] = useState<TabKey>(DEFAULT_TAB)
  const [loading, setLoading] = useState(false)
  const [newsItems, setNewsItems] = useState<NewsItem[]>([])
  const [articles, setArticles] = useState<ArticleItem[]>([])
  const [tests, setTests] = useState<TestItem[]>([])

  const fetchContent = useCallback(async (tab: TabKey) => {
    if (tab === 'career') {
      setLoading(false)
      return
    }

    setLoading(true)

    try {
      const response = await apiClient.get<{ content: ContentItem[]; total: number }>('/content/', {
        type: tabToContentType[tab],
        status: 'published',
        page: 1,
        page_size: 10,
      })
      const items = response.content || []

      if (tab === 'news') {
        setNewsItems(
          items.map((item) => ({
            id: item.id,
            title: item.title,
            excerpt: `${item.content.substring(0, 100)}...`,
            date: new Date(item.created_at).toLocaleDateString('ru-RU', {
              day: 'numeric',
              month: 'short',
              year: 'numeric',
            }),
            category: item.tags[0] || 'Обновления',
            author: item.author_name || 'Команда TeenFreelance',
          }))
        )
      }

      if (tab === 'articles') {
        setArticles(
          items.map((item) => ({
            id: item.id,
            title: item.title,
            excerpt: `${item.content.substring(0, 100)}...`,
            readTime: `${Math.max(1, Math.ceil(item.content.length / 1000))} мин`,
            category: item.tags[0] || 'Обучение',
          }))
        )
      }

      if (tab === 'tests') {
        setTests(
          items.map((item) => ({
            id: item.id,
            title: item.title,
            description: `${item.content.substring(0, 100)}...`,
            questionsCount: Math.max(1, Math.ceil(item.content.length / 50)),
            completionTime: `${Math.max(1, Math.ceil(item.content.length / 1000))} мин`,
          }))
        )
      }
    } catch (error) {
      console.warn('Error fetching community content (backend unavailable)', error)

      if (tab === 'news') {
        setNewsItems([])
      }

      if (tab === 'articles') {
        setArticles([])
      }

      if (tab === 'tests') {
        setTests([])
      }
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchContent(activeTab)
  }, [activeTab, fetchContent])

  return (
    <>
      <Header />

      <main className={styles.page}>
        <div className={styles.pageHero}>
          <CommunityHero />
        </div>

        <section className={styles.contentSection}>
          <div className={styles.container}>
            <CommunityTabs activeTab={activeTab} onChange={setActiveTab} />

            {activeTab === 'news' && <NewsGrid items={newsItems} loading={loading} />}
            {activeTab === 'articles' && <ArticlesGrid items={articles} loading={loading} />}
            {activeTab === 'tests' && <TestsGrid items={tests} loading={loading} />}
            {activeTab === 'career' && <CareerGuide />}
          </div>
        </section>
      </main>

      <Footer />
    </>
  )
}