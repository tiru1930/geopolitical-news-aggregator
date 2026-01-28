import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams, Link } from 'react-router-dom'
import { Filter, ExternalLink, ChevronLeft, ChevronRight, Newspaper } from 'lucide-react'
import { getArticles, getRegionStats, getThemeStats } from '../services/api'
import RelevanceBadge from '../components/articles/RelevanceBadge'
import type { ArticleFilters, RelevanceLevel } from '../types'
import { format } from 'date-fns'

export default function Articles() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [showFilters, setShowFilters] = useState(false)

  const filters: ArticleFilters = {
    page: parseInt(searchParams.get('page') || '1'),
    page_size: 20,
    region: searchParams.get('region') || undefined,
    country: searchParams.get('country') || undefined,
    theme: searchParams.get('theme') || undefined,
    domain: searchParams.get('domain') || undefined,
    relevance_level: (searchParams.get('relevance_level') as RelevanceLevel) || undefined,
    search: searchParams.get('search') || undefined,
  }

  const { data, isLoading } = useQuery({
    queryKey: ['articles', filters],
    queryFn: () => getArticles(filters),
  })

  const { data: regions } = useQuery({
    queryKey: ['regions'],
    queryFn: getRegionStats,
  })

  const { data: themes } = useQuery({
    queryKey: ['themes'],
    queryFn: getThemeStats,
  })

  const updateFilter = (key: string, value: string | undefined) => {
    const newParams = new URLSearchParams(searchParams)
    if (value) {
      newParams.set(key, value)
    } else {
      newParams.delete(key)
    }
    newParams.set('page', '1')
    setSearchParams(newParams)
  }

  const goToPage = (page: number) => {
    const newParams = new URLSearchParams(searchParams)
    newParams.set('page', String(page))
    setSearchParams(newParams)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-army-olive font-['Roboto_Condensed'] uppercase tracking-wide">
            Intelligence Reports
          </h1>
          <p className="text-gray-600 mt-1">
            {data?.total || 0} reports in database
          </p>
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg border-2 transition-colors font-semibold ${
            showFilters
              ? 'bg-army-olive text-white border-army-olive'
              : 'border-army-khaki text-army-olive hover:border-army-olive'
          }`}
        >
          <Filter className="w-4 h-4" />
          Filters
        </button>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="bg-white rounded-xl p-6 border-2 border-army-khaki/30 shadow-sm grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">Region</label>
            <select
              value={filters.region || ''}
              onChange={(e) => updateFilter('region', e.target.value || undefined)}
              className="w-full bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg px-3 py-2 text-gray-800 focus:outline-none focus:border-army-olive"
            >
              <option value="">All Regions</option>
              {regions?.map((r) => (
                <option key={r.region} value={r.region}>
                  {r.region} ({r.count})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">Theme</label>
            <select
              value={filters.theme || ''}
              onChange={(e) => updateFilter('theme', e.target.value || undefined)}
              className="w-full bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg px-3 py-2 text-gray-800 focus:outline-none focus:border-army-olive"
            >
              <option value="">All Themes</option>
              {themes?.map((t) => (
                <option key={t.theme} value={t.theme}>
                  {t.theme} ({t.count})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">Priority</label>
            <select
              value={filters.relevance_level || ''}
              onChange={(e) => updateFilter('relevance_level', e.target.value || undefined)}
              className="w-full bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg px-3 py-2 text-gray-800 focus:outline-none focus:border-army-olive"
            >
              <option value="">All Levels</option>
              <option value="high">Critical</option>
              <option value="medium">Priority</option>
              <option value="low">Routine</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">Domain</label>
            <select
              value={filters.domain || ''}
              onChange={(e) => updateFilter('domain', e.target.value || undefined)}
              className="w-full bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg px-3 py-2 text-gray-800 focus:outline-none focus:border-army-olive"
            >
              <option value="">All Domains</option>
              <option value="land">Land</option>
              <option value="maritime">Maritime</option>
              <option value="air">Air</option>
              <option value="cyber">Cyber</option>
              <option value="space">Space</option>
              <option value="nuclear">Nuclear</option>
              <option value="diplomatic">Diplomatic</option>
              <option value="economic">Economic</option>
            </select>
          </div>
        </div>
      )}

      {/* Articles List */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="bg-white rounded-xl p-6 animate-pulse border-2 border-army-khaki/20">
                <div className="h-6 bg-army-khaki/30 rounded w-3/4 mb-4" />
                <div className="h-4 bg-army-khaki/30 rounded w-1/2" />
              </div>
            ))}
          </div>
        ) : (
          <>
            {data?.articles.map((article) => (
              <Link
                key={article.id}
                to={`/articles/${article.id}`}
                className="block bg-white rounded-xl p-6 border-2 border-army-khaki/30 hover:border-army-olive transition-colors shadow-sm"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <RelevanceBadge level={article.relevance_level} size="sm" />
                      {article.is_priority && (
                        <span className="text-xs text-white font-semibold px-2 py-0.5 bg-army-maroon rounded">
                          PRIORITY
                        </span>
                      )}
                      {article.region && (
                        <span className="text-xs text-army-olive font-medium px-2 py-0.5 bg-army-sand rounded">
                          {article.region}
                        </span>
                      )}
                      {article.theme && (
                        <span className="text-xs text-gray-600 font-medium px-2 py-0.5 bg-gray-100 rounded">
                          {article.theme}
                        </span>
                      )}
                    </div>
                    <h3 className="text-lg font-semibold text-gray-800 mb-2">
                      {article.title}
                    </h3>
                    {article.summary_bullets ? (
                      <div className="text-gray-600 text-sm space-y-1">
                        {article.summary_bullets.split('\n').slice(0, 2).map((bullet, idx) => (
                          <p key={idx} className="line-clamp-1">{bullet}</p>
                        ))}
                      </div>
                    ) : article.summary_what_happened && (
                      <p className="text-gray-600 text-sm line-clamp-2">
                        {article.summary_what_happened}
                      </p>
                    )}
                    <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
                      <span className="font-medium text-army-olive">{article.source_name}</span>
                      {article.published_at && (
                        <>
                          <span className="text-army-khaki">|</span>
                          <span>{format(new Date(article.published_at), 'MMM d, yyyy')}</span>
                        </>
                      )}
                      {article.country && (
                        <>
                          <span className="text-army-khaki">|</span>
                          <span>{article.country}</span>
                        </>
                      )}
                    </div>
                  </div>
                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="p-2 text-army-khaki-dark hover:text-army-olive transition-colors"
                  >
                    <ExternalLink className="w-5 h-5" />
                  </a>
                </div>
              </Link>
            ))}

            {data?.articles.length === 0 && (
              <div className="text-center py-12 bg-white rounded-xl border-2 border-army-khaki/30">
                <Newspaper className="w-12 h-12 mx-auto mb-3 text-army-khaki" />
                <p className="text-gray-500">No reports found matching your criteria.</p>
              </div>
            )}
          </>
        )}
      </div>

      {/* Pagination */}
      {data && data.total_pages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => goToPage(filters.page! - 1)}
            disabled={filters.page === 1}
            className="p-2 rounded-lg border-2 border-army-khaki text-army-olive hover:border-army-olive disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <span className="px-4 py-2 text-gray-600 font-medium">
            Page {filters.page} of {data.total_pages}
          </span>
          <button
            onClick={() => goToPage(filters.page! + 1)}
            disabled={filters.page === data.total_pages}
            className="p-2 rounded-lg border-2 border-army-khaki text-army-olive hover:border-army-olive disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      )}
    </div>
  )
}
