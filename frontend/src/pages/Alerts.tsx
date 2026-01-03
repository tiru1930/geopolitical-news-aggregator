import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getAlerts, createAlert, deleteAlert, toggleAlert } from '../services/api'
import { Bell, Plus, Trash2, ToggleLeft, ToggleRight, X } from 'lucide-react'

export default function Alerts() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    regions: [] as string[],
    countries: [] as string[],
    themes: [] as string[],
    keywords: [] as string[],
    min_relevance: 'medium',
    frequency: 'daily' as const,
  })

  const { data: alerts, isLoading } = useQuery({
    queryKey: ['alerts'],
    queryFn: getAlerts,
  })

  const createMutation = useMutation({
    mutationFn: createAlert,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      setShowForm(false)
      setFormData({
        name: '',
        regions: [],
        countries: [],
        themes: [],
        keywords: [],
        min_relevance: 'medium',
        frequency: 'daily',
      })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: deleteAlert,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    },
  })

  const toggleMutation = useMutation({
    mutationFn: toggleAlert,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate(formData)
  }

  const addKeyword = (keyword: string) => {
    if (keyword && !formData.keywords.includes(keyword)) {
      setFormData({ ...formData, keywords: [...formData.keywords, keyword] })
    }
  }

  const removeKeyword = (keyword: string) => {
    setFormData({ ...formData, keywords: formData.keywords.filter((k) => k !== keyword) })
  }

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-24 bg-army-khaki/30 rounded-xl" />
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-army-olive font-['Roboto_Condensed'] uppercase tracking-wide">
            Alert Configuration
          </h1>
          <p className="text-gray-600 mt-1">Configure notifications for strategic topics</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 px-4 py-2 bg-army-olive text-white rounded-lg hover:bg-army-olive-dark transition-colors font-semibold"
        >
          <Plus className="w-4 h-4" />
          New Alert
        </button>
      </div>

      {/* Create Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl w-full max-w-lg border-2 border-army-khaki/30 shadow-xl">
            <div className="flex justify-between items-center p-4 border-b-2 border-army-khaki/30 bg-army-olive rounded-t-xl">
              <h2 className="text-lg font-semibold text-white font-['Roboto_Condensed'] uppercase">Create Alert</h2>
              <button
                onClick={() => setShowForm(false)}
                className="p-1 text-white/80 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-4 space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">Alert Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  placeholder="e.g., China Military Activity"
                  className="w-full bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg px-3 py-2 text-gray-800 focus:outline-none focus:border-army-olive"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">Keywords</label>
                <div className="flex flex-wrap gap-2 mb-2">
                  {formData.keywords.map((keyword) => (
                    <span
                      key={keyword}
                      className="inline-flex items-center gap-1 px-2 py-1 bg-army-olive/20 text-army-olive rounded text-sm font-medium"
                    >
                      {keyword}
                      <button type="button" onClick={() => removeKeyword(keyword)}>
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                </div>
                <input
                  type="text"
                  placeholder="Add keyword and press Enter"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      addKeyword((e.target as HTMLInputElement).value)
                      ;(e.target as HTMLInputElement).value = ''
                    }
                  }}
                  className="w-full bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg px-3 py-2 text-gray-800 focus:outline-none focus:border-army-olive"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">Minimum Priority</label>
                <select
                  value={formData.min_relevance}
                  onChange={(e) => setFormData({ ...formData, min_relevance: e.target.value })}
                  className="w-full bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg px-3 py-2 text-gray-800 focus:outline-none focus:border-army-olive"
                >
                  <option value="low">Routine and above</option>
                  <option value="medium">Priority and above</option>
                  <option value="high">Critical only</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">Frequency</label>
                <select
                  value={formData.frequency}
                  onChange={(e) =>
                    setFormData({ ...formData, frequency: e.target.value as any })
                  }
                  className="w-full bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg px-3 py-2 text-gray-800 focus:outline-none focus:border-army-olive"
                >
                  <option value="immediate">Immediate</option>
                  <option value="hourly">Hourly</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                </select>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="flex-1 px-4 py-2 border-2 border-army-khaki text-gray-700 rounded-lg hover:border-army-olive transition-colors font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isPending}
                  className="flex-1 px-4 py-2 bg-army-olive text-white rounded-lg hover:bg-army-olive-dark transition-colors disabled:opacity-50 font-semibold"
                >
                  Create Alert
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Alerts List */}
      <div className="space-y-4">
        {alerts?.map((alert) => (
          <div
            key={alert.id}
            className={`bg-white rounded-xl p-6 border-2 transition-colors shadow-sm ${
              alert.is_active ? 'border-army-khaki/30' : 'border-army-khaki/30 opacity-60'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-army-olive/10 rounded-lg">
                  <Bell className="w-6 h-6 text-army-olive" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-800">{alert.name}</h3>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {alert.keywords.map((keyword) => (
                      <span
                        key={keyword}
                        className="text-xs px-2 py-0.5 bg-army-olive/20 text-army-olive rounded font-medium"
                      >
                        {keyword}
                      </span>
                    ))}
                    {alert.regions.map((region) => (
                      <span
                        key={region}
                        className="text-xs px-2 py-0.5 bg-army-gold/30 text-army-olive rounded font-medium"
                      >
                        {region}
                      </span>
                    ))}
                  </div>
                  <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
                    <span>Min: {alert.min_relevance}</span>
                    <span className="text-army-khaki">|</span>
                    <span>Frequency: {alert.frequency}</span>
                    <span className="text-army-khaki">|</span>
                    <span>Triggered: {alert.trigger_count} times</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => toggleMutation.mutate(alert.id)}
                  className={`p-2 rounded-lg transition-colors ${
                    alert.is_active
                      ? 'bg-green-100 text-green-600'
                      : 'bg-gray-100 text-gray-400'
                  }`}
                >
                  {alert.is_active ? (
                    <ToggleRight className="w-5 h-5" />
                  ) : (
                    <ToggleLeft className="w-5 h-5" />
                  )}
                </button>
                <button
                  onClick={() => deleteMutation.mutate(alert.id)}
                  className="p-2 rounded-lg bg-army-maroon/10 text-army-maroon hover:bg-army-maroon/20 transition-colors"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        ))}

        {(!alerts || alerts.length === 0) && (
          <div className="text-center py-12 bg-white rounded-xl border-2 border-army-khaki/30">
            <Bell className="w-12 h-12 text-army-khaki mx-auto mb-4" />
            <p className="text-gray-500 mb-4">No alerts configured</p>
            <button
              onClick={() => setShowForm(true)}
              className="px-4 py-2 bg-army-olive text-white rounded-lg hover:bg-army-olive-dark transition-colors font-semibold"
            >
              Create Your First Alert
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
