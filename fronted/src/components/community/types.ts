export interface NewsItem {
  id: number
  title: string
  excerpt: string
  date: string
  category: string
  author: string
}

export interface ArticleItem {
  id: number
  title: string
  excerpt: string
  readTime: string
  category: string
}

export interface TestItem {
  id: number
  title: string
  description: string
  questionsCount: number
  completionTime: string
}

type TabKey = 'news' | 'articles' | 'tests' | 'career'

export type { TabKey }
