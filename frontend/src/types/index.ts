export type RelevanceLevel = 'high' | 'medium' | 'low'

export interface Article {
  id: number
  title: string
  url: string
  original_content?: string
  published_at?: string
  author?: string
  image_url?: string
  source_id: number
  source_name?: string
  summary_what_happened?: string
  summary_why_matters?: string
  summary_india_implications?: string
  summary_future_developments?: string
  relevance_level: RelevanceLevel
  relevance_score: number
  geo_score: number
  military_score: number
  diplomatic_score: number
  economic_score: number
  region?: string
  country?: string
  theme?: string
  domain?: string
  entities: Entity[]
  is_processed: number
  created_at: string
  updated_at?: string
}

export interface Entity {
  type: string
  name: string
}

export interface ArticleListResponse {
  articles: Article[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface Source {
  id: number
  name: string
  url: string
  feed_url?: string
  source_type: 'rss' | 'api' | 'scrape'
  category: 'news_agency' | 'think_tank' | 'government' | 'military' | 'academic'
  country?: string
  language: string
  description?: string
  reliability_score: number
  bias_rating?: string
  is_active: boolean
  fetch_interval_minutes: number
  last_fetched_at?: string
  last_fetch_status?: string
  article_count: number
  created_at: string
  updated_at?: string
}

export interface Alert {
  id: number
  user_id: number
  name: string
  regions: string[]
  countries: string[]
  themes: string[]
  domains: string[]
  keywords: string[]
  min_relevance: string
  frequency: 'immediate' | 'hourly' | 'daily' | 'weekly'
  is_active: boolean
  email_enabled: boolean
  last_triggered_at?: string
  trigger_count: number
  created_at: string
  updated_at?: string
}

export interface DashboardStats {
  total_articles: number
  relevance_breakdown: {
    high: number
    medium: number
    low: number
  }
  recent_activity: {
    last_24h: number
    last_7d: number
  }
  sources: {
    active: number
    total: number
  }
  pending_processing: number
}

export interface TrendData {
  date: string
  total: number
  high_relevance: number
}

export interface RegionStats {
  region: string
  count: number
  avg_relevance: number
}

export interface ThemeStats {
  theme: string
  count: number
  avg_relevance: number
}

export interface Hotspot {
  region: string
  lat: number
  lng: number
  total_articles: number
  high_relevance: number
  intensity: number
}

export interface ArticleFilters {
  page?: number
  page_size?: number
  region?: string
  country?: string
  theme?: string
  domain?: string
  relevance_level?: RelevanceLevel
  source_id?: number
  search?: string
  start_date?: string
  end_date?: string
}
