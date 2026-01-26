import axios from 'axios'
import type {
  Article,
  ArticleListResponse,
  ArticleFilters,
  Source,
  Alert,
  DashboardStats,
  TrendData,
  RegionStats,
  ThemeStats,
  Hotspot,
} from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Articles
export const getArticles = async (filters: ArticleFilters = {}): Promise<ArticleListResponse> => {
  const params = new URLSearchParams()

  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      params.append(key, String(value))
    }
  })

  const response = await api.get(`/api/articles/?${params.toString()}`)
  return response.data
}

export const getArticle = async (id: number): Promise<Article> => {
  const response = await api.get(`/api/articles/${id}`)
  return response.data
}

export const getHighRelevanceArticles = async (limit: number = 10): Promise<Article[]> => {
  const response = await api.get(`/api/articles/high-relevance?limit=${limit}`)
  return response.data
}

// Sources
export const getSources = async (): Promise<Source[]> => {
  const response = await api.get('/api/sources/')
  return response.data
}

export const getSource = async (id: number): Promise<Source> => {
  const response = await api.get(`/api/sources/${id}`)
  return response.data
}

export const createSource = async (data: Partial<Source>): Promise<Source> => {
  const response = await api.post('/api/sources/', data)
  return response.data
}

export const updateSource = async (id: number, data: Partial<Source>): Promise<Source> => {
  const response = await api.put(`/api/sources/${id}`, data)
  return response.data
}

export const deleteSource = async (id: number): Promise<void> => {
  await api.delete(`/api/sources/${id}`)
}

export const toggleSource = async (id: number): Promise<{ is_active: boolean }> => {
  const response = await api.post(`/api/sources/${id}/toggle`)
  return response.data
}

export const seedDefaultSources = async (): Promise<void> => {
  await api.post('/api/sources/seed-defaults')
}

// Dashboard
export const getDashboardStats = async (): Promise<DashboardStats> => {
  const response = await api.get('/api/dashboard/stats')
  return response.data
}

export const getTrends = async (days: number = 7): Promise<TrendData[]> => {
  const response = await api.get(`/api/dashboard/trends?days=${days}`)
  return response.data
}

export const getRegionStats = async (): Promise<RegionStats[]> => {
  const response = await api.get('/api/dashboard/regions')
  return response.data
}

export const getThemeStats = async (): Promise<ThemeStats[]> => {
  const response = await api.get('/api/dashboard/themes')
  return response.data
}

export const getCountryStats = async (limit: number = 20): Promise<{ country: string; count: number }[]> => {
  const response = await api.get(`/api/dashboard/countries?limit=${limit}`)
  return response.data
}

export const getHotspots = async (): Promise<Hotspot[]> => {
  const response = await api.get('/api/dashboard/hotspots')
  return response.data
}

export interface CountryHotspot {
  country: string
  lat: number
  lng: number
  total_articles: number
  high_relevance: number
  intensity: number
}

export const getCountryHotspots = async (limit: number = 30): Promise<CountryHotspot[]> => {
  const response = await api.get(`/api/dashboard/country-hotspots?limit=${limit}`)
  return response.data
}

export const getRecentHighImpact = async (limit: number = 5): Promise<Article[]> => {
  const response = await api.get(`/api/dashboard/recent-high-impact?limit=${limit}`)
  return response.data
}

// Alerts
export const getAlerts = async (): Promise<Alert[]> => {
  const response = await api.get('/api/alerts/')
  return response.data
}

export const getAlert = async (id: number): Promise<Alert> => {
  const response = await api.get(`/api/alerts/${id}`)
  return response.data
}

export const createAlert = async (data: Partial<Alert>): Promise<Alert> => {
  const response = await api.post('/api/alerts/', data)
  return response.data
}

export const updateAlert = async (id: number, data: Partial<Alert>): Promise<Alert> => {
  const response = await api.put(`/api/alerts/${id}`, data)
  return response.data
}

export const deleteAlert = async (id: number): Promise<void> => {
  await api.delete(`/api/alerts/${id}`)
}

export const toggleAlert = async (id: number): Promise<{ is_active: boolean }> => {
  const response = await api.post(`/api/alerts/${id}/toggle`)
  return response.data
}

// Health
export const checkHealth = async (): Promise<{ status: string }> => {
  const response = await api.get('/health')
  return response.data
}

// Auth
export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterData {
  email: string
  username: string
  password: string
  full_name?: string
  organization?: string
  role?: 'admin' | 'analyst'
  invite_code?: string
}

export interface AuthToken {
  access_token: string
  token_type: string
}

export interface User {
  id: number
  email: string
  username: string
  full_name: string | null
  organization: string | null
  role: 'admin' | 'analyst'
  is_active: boolean
  is_verified: boolean
  preferred_regions: string | null
  preferred_themes: string | null
  dark_mode: boolean
  created_at: string
  last_login_at: string | null
}

export const login = async (credentials: LoginCredentials): Promise<AuthToken> => {
  const response = await api.post('/api/auth/login', credentials)
  return response.data
}

export const register = async (data: RegisterData): Promise<User> => {
  const response = await api.post('/api/auth/register', data)
  return response.data
}

export const getCurrentUser = async (): Promise<User> => {
  const response = await api.get('/api/auth/me')
  return response.data
}

export const setupDefaultAccounts = async (): Promise<{ message: string; accounts: Array<{ username: string; password?: string; role: string }> }> => {
  const response = await api.post('/api/auth/setup-accounts')
  return response.data
}

// Set auth token for API requests
export const setAuthToken = (token: string | null) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common['Authorization']
  }
}

export default api
