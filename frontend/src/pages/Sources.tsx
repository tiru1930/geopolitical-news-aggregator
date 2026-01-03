import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getSources, toggleSource, seedDefaultSources, createSource, deleteSource } from '../services/api'
import {
  Rss,
  Globe2,
  Building2,
  GraduationCap,
  Shield,
  CheckCircle,
  XCircle,
  RefreshCw,
  Plus,
  Trash2,
  X,
  Download,
  Loader2,
} from 'lucide-react'
import { format } from 'date-fns'
import api from '../services/api'

interface AddSourceForm {
  name: string
  url: string
  feed_url: string
  source_type: string
  category: string
  country: string
  description: string
  reliability_score: number
}

export default function Sources() {
  const queryClient = useQueryClient()
  const [showAddModal, setShowAddModal] = useState(false)
  const [formData, setFormData] = useState<AddSourceForm>({
    name: '',
    url: '',
    feed_url: '',
    source_type: 'rss',
    category: 'news_agency',
    country: '',
    description: '',
    reliability_score: 7,
  })

  const { data: sources, isLoading } = useQuery({
    queryKey: ['sources'],
    queryFn: getSources,
  })

  const toggleMutation = useMutation({
    mutationFn: toggleSource,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sources'] })
    },
  })

  const seedMutation = useMutation({
    mutationFn: seedDefaultSources,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sources'] })
    },
  })

  const seedAdditionalMutation = useMutation({
    mutationFn: async () => {
      await api.post('/api/sources/seed-additional')
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sources'] })
    },
  })

  const fetchAllMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post('/api/sources/fetch-all')
      return response.data
    },
  })

  const fetchGdeltMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post('/api/sources/fetch-gdelt')
      return response.data
    },
  })

  const createMutation = useMutation({
    mutationFn: createSource,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sources'] })
      setShowAddModal(false)
      setFormData({
        name: '',
        url: '',
        feed_url: '',
        source_type: 'rss',
        category: 'news_agency',
        country: '',
        description: '',
        reliability_score: 7,
      })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: deleteSource,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sources'] })
    },
  })

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'news_agency':
        return Rss
      case 'think_tank':
        return Building2
      case 'government':
        return Shield
      case 'military':
        return Shield
      case 'academic':
        return GraduationCap
      default:
        return Globe2
    }
  }

  const getCategoryLabel = (category: string) => {
    return category.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-24 bg-army-khaki/20 rounded-xl" />
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-army-olive font-['Roboto_Condensed'] uppercase tracking-wide">
            Intelligence Sources
          </h1>
          <p className="text-gray-600 mt-1">{sources?.length || 0} configured sources</p>
        </div>
        <div className="flex gap-3 flex-wrap">
          <button
            onClick={() => fetchAllMutation.mutate()}
            disabled={fetchAllMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-army-olive text-white rounded-lg hover:bg-army-olive-dark transition-colors disabled:opacity-50 font-semibold"
          >
            {fetchAllMutation.isPending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Download className="w-4 h-4" />
            )}
            Fetch RSS
          </button>
          <button
            onClick={() => fetchGdeltMutation.mutate()}
            disabled={fetchGdeltMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-army-gold text-army-olive-dark rounded-lg hover:bg-army-gold-light transition-colors disabled:opacity-50 font-semibold"
          >
            {fetchGdeltMutation.isPending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Globe2 className="w-4 h-4" />
            )}
            Fetch GDELT
          </button>
          <button
            onClick={() => seedMutation.mutate()}
            disabled={seedMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-white border-2 border-army-khaki rounded-lg text-army-olive hover:border-army-olive transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${seedMutation.isPending ? 'animate-spin' : ''}`} />
            Seed Defaults
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-army-maroon text-white rounded-lg hover:bg-army-maroon-light transition-colors font-semibold"
          >
            <Plus className="w-4 h-4" />
            Add Source
          </button>
        </div>
      </div>

      {/* Fetch Status Messages */}
      {fetchAllMutation.isSuccess && (
        <div className="p-4 bg-army-olive/10 border-l-4 border-army-olive rounded-r-lg text-army-olive">
          RSS fetch triggered! Check back in a moment for new articles.
        </div>
      )}
      {fetchGdeltMutation.isSuccess && (
        <div className="p-4 bg-army-gold/20 border-l-4 border-army-gold rounded-r-lg text-army-olive">
          GDELT fetch complete! {(fetchGdeltMutation.data as any)?.message}
        </div>
      )}

      {/* Sources List */}
      <div className="space-y-4">
        {sources?.map((source) => {
          const Icon = getCategoryIcon(source.category)

          return (
            <div
              key={source.id}
              className={`bg-white rounded-xl p-6 border-2 transition-colors shadow-sm ${
                source.is_active ? 'border-army-khaki/30' : 'border-gray-200 opacity-60'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-army-olive/10 rounded-lg">
                    <Icon className="w-6 h-6 text-army-olive" />
                  </div>
                  <div>
                    <div className="flex items-center gap-3 flex-wrap">
                      <h3 className="text-lg font-semibold text-gray-800">{source.name}</h3>
                      <span className="text-xs px-2 py-0.5 bg-army-sand rounded text-army-olive font-medium">
                        {getCategoryLabel(source.category)}
                      </span>
                      <span className="text-xs px-2 py-0.5 bg-gray-100 rounded text-gray-600 font-medium">
                        {source.source_type?.toUpperCase()}
                      </span>
                      {source.country && (
                        <span className="text-xs px-2 py-0.5 bg-gray-100 rounded text-gray-600">
                          {source.country}
                        </span>
                      )}
                    </div>
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-gray-500 hover:text-army-olive transition-colors"
                    >
                      {source.url}
                    </a>
                    {source.feed_url && (
                      <p className="text-xs text-gray-400 mt-1 truncate max-w-lg">
                        Feed: {source.feed_url}
                      </p>
                    )}
                    <div className="flex items-center gap-4 mt-3 text-sm flex-wrap">
                      <span className="text-gray-600 font-medium">
                        {source.article_count} articles
                      </span>
                      <span className="text-gray-500">
                        Reliability: {source.reliability_score}/10
                      </span>
                      {source.last_fetched_at && (
                        <span className="text-gray-500">
                          Last fetch: {format(new Date(source.last_fetched_at), 'MMM d, HH:mm')}
                        </span>
                      )}
                      {source.last_fetch_status && (
                        <span
                          className={
                            source.last_fetch_status === 'success'
                              ? 'text-army-olive font-medium'
                              : 'text-army-maroon font-medium'
                          }
                        >
                          {source.last_fetch_status}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => toggleMutation.mutate(source.id)}
                    disabled={toggleMutation.isPending}
                    className={`p-2 rounded-lg transition-colors ${
                      source.is_active
                        ? 'bg-army-olive/20 text-army-olive hover:bg-army-olive/30'
                        : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
                    }`}
                    title={source.is_active ? 'Disable source' : 'Enable source'}
                  >
                    {source.is_active ? (
                      <CheckCircle className="w-5 h-5" />
                    ) : (
                      <XCircle className="w-5 h-5" />
                    )}
                  </button>
                  <button
                    onClick={() => {
                      if (confirm(`Delete source "${source.name}"?`)) {
                        deleteMutation.mutate(source.id)
                      }
                    }}
                    disabled={deleteMutation.isPending}
                    className="p-2 rounded-lg bg-army-maroon/10 text-army-maroon hover:bg-army-maroon/20 transition-colors"
                    title="Delete source"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          )
        })}

        {(!sources || sources.length === 0) && (
          <div className="text-center py-12 bg-white rounded-xl border-2 border-army-khaki/30">
            <Rss className="w-12 h-12 text-army-khaki mx-auto mb-4" />
            <p className="text-gray-500 mb-4">No intelligence sources configured</p>
            <button
              onClick={() => seedMutation.mutate()}
              disabled={seedMutation.isPending}
              className="px-4 py-2 bg-army-olive text-white rounded-lg hover:bg-army-olive-dark transition-colors font-semibold"
            >
              Seed Default Sources
            </button>
          </div>
        )}
      </div>

      {/* Add Source Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl w-full max-w-lg border-2 border-army-khaki/30 shadow-xl overflow-hidden">
            <div className="flex justify-between items-center p-6 bg-army-olive">
              <h2 className="text-xl font-bold text-white font-['Roboto_Condensed'] uppercase">
                Add New Source
              </h2>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-white/80 hover:text-white"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1 uppercase tracking-wide">Name *</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2 bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg text-gray-800 focus:outline-none focus:border-army-olive"
                  placeholder="Reuters World News"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1 uppercase tracking-wide">Website URL *</label>
                <input
                  type="url"
                  required
                  value={formData.url}
                  onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                  className="w-full px-4 py-2 bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg text-gray-800 focus:outline-none focus:border-army-olive"
                  placeholder="https://www.reuters.com"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1 uppercase tracking-wide">RSS Feed URL *</label>
                <input
                  type="url"
                  required
                  value={formData.feed_url}
                  onChange={(e) => setFormData({ ...formData, feed_url: e.target.value })}
                  className="w-full px-4 py-2 bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg text-gray-800 focus:outline-none focus:border-army-olive"
                  placeholder="https://www.reuters.com/rss/world"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1 uppercase tracking-wide">Type</label>
                  <select
                    value={formData.source_type}
                    onChange={(e) => setFormData({ ...formData, source_type: e.target.value })}
                    className="w-full px-4 py-2 bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg text-gray-800 focus:outline-none focus:border-army-olive"
                  >
                    <option value="rss">RSS Feed</option>
                    <option value="api">API</option>
                    <option value="scrape">Web Scrape</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1 uppercase tracking-wide">Category</label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className="w-full px-4 py-2 bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg text-gray-800 focus:outline-none focus:border-army-olive"
                  >
                    <option value="news_agency">News Agency</option>
                    <option value="think_tank">Think Tank</option>
                    <option value="government">Government</option>
                    <option value="military">Military</option>
                    <option value="academic">Academic</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1 uppercase tracking-wide">Country</label>
                  <input
                    type="text"
                    value={formData.country}
                    onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                    className="w-full px-4 py-2 bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg text-gray-800 focus:outline-none focus:border-army-olive"
                    placeholder="USA"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1 uppercase tracking-wide">Reliability (1-10)</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={formData.reliability_score}
                    onChange={(e) => setFormData({ ...formData, reliability_score: parseInt(e.target.value) })}
                    className="w-full px-4 py-2 bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg text-gray-800 focus:outline-none focus:border-army-olive"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1 uppercase tracking-wide">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-4 py-2 bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg text-gray-800 focus:outline-none focus:border-army-olive"
                  rows={2}
                  placeholder="Brief description of the source"
                />
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 bg-white border-2 border-army-khaki rounded-lg text-gray-700 hover:border-army-olive"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isPending}
                  className="px-4 py-2 bg-army-olive text-white rounded-lg hover:bg-army-olive-dark disabled:opacity-50 font-semibold"
                >
                  {createMutation.isPending ? 'Adding...' : 'Add Source'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
