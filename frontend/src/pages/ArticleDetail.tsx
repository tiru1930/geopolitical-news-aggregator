import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  ArrowLeft,
  ExternalLink,
  Globe2,
  Target,
  TrendingUp,
  AlertCircle,
  Lightbulb,
  MapPin,
  Tag,
} from 'lucide-react'
import { getArticle } from '../services/api'
import RelevanceBadge from '../components/articles/RelevanceBadge'
import { format } from 'date-fns'

export default function ArticleDetail() {
  const { id } = useParams<{ id: string }>()

  const { data: article, isLoading } = useQuery({
    queryKey: ['article', id],
    queryFn: () => getArticle(parseInt(id!)),
    enabled: !!id,
  })

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="h-8 bg-dark-200 rounded w-1/4" />
        <div className="h-12 bg-dark-200 rounded w-3/4" />
        <div className="h-64 bg-dark-200 rounded" />
      </div>
    )
  }

  if (!article) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400">Article not found</p>
        <Link to="/articles" className="text-primary-400 hover:underline mt-4 inline-block">
          Back to Articles
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Back Button */}
      <Link
        to="/articles"
        className="inline-flex items-center gap-2 text-gray-400 hover:text-gray-200 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Articles
      </Link>

      {/* Header */}
      <div className="bg-dark-200 rounded-xl p-6 border border-gray-800">
        <div className="flex items-center gap-3 mb-4">
          <RelevanceBadge level={article.relevance_level} score={article.relevance_score} />
          {article.region && (
            <span className="text-sm text-gray-400 px-3 py-1 bg-dark-300 rounded-full">
              {article.region}
            </span>
          )}
          {article.theme && (
            <span className="text-sm text-gray-400 px-3 py-1 bg-dark-300 rounded-full">
              {article.theme}
            </span>
          )}
          {article.domain && (
            <span className="text-sm text-gray-400 px-3 py-1 bg-dark-300 rounded-full capitalize">
              {article.domain}
            </span>
          )}
        </div>

        <h1 className="text-2xl font-bold text-white mb-4">{article.title}</h1>

        <div className="flex items-center gap-4 text-sm text-gray-400">
          <span className="font-medium text-gray-300">{article.source_name}</span>
          {article.published_at && (
            <>
              <span>|</span>
              <span>{format(new Date(article.published_at), 'MMMM d, yyyy')}</span>
            </>
          )}
          {article.author && (
            <>
              <span>|</span>
              <span>By {article.author}</span>
            </>
          )}
        </div>

        <a
          href={article.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 mt-4 text-primary-400 hover:text-primary-300 transition-colors"
        >
          Read Original <ExternalLink className="w-4 h-4" />
        </a>
      </div>

      {/* Strategic Analysis */}
      {article.is_processed === 1 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-white">Strategic Analysis</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <AnalysisCard
              icon={Target}
              title="What Happened"
              content={article.summary_what_happened}
              color="blue"
            />
            <AnalysisCard
              icon={AlertCircle}
              title="Why It Matters"
              content={article.summary_why_matters}
              color="red"
            />
            <AnalysisCard
              icon={Globe2}
              title="Implications for India"
              content={article.summary_india_implications}
              color="yellow"
            />
            <AnalysisCard
              icon={Lightbulb}
              title="Future Developments"
              content={article.summary_future_developments}
              color="green"
            />
          </div>
        </div>
      )}

      {/* Relevance Scores */}
      <div className="bg-dark-200 rounded-xl p-6 border border-gray-800">
        <h2 className="text-lg font-semibold text-white mb-4">Relevance Breakdown</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <ScoreBar label="Geographic" score={article.geo_score} color="blue" />
          <ScoreBar label="Military" score={article.military_score} color="red" />
          <ScoreBar label="Diplomatic" score={article.diplomatic_score} color="yellow" />
          <ScoreBar label="Economic" score={article.economic_score} color="green" />
        </div>
      </div>

      {/* Entities */}
      {article.entities && article.entities.length > 0 && (
        <div className="bg-dark-200 rounded-xl p-6 border border-gray-800">
          <h2 className="text-lg font-semibold text-white mb-4">Key Entities</h2>
          <div className="flex flex-wrap gap-2">
            {article.entities.map((entity, index) => (
              <span
                key={index}
                className="inline-flex items-center gap-2 px-3 py-1.5 bg-dark-300 rounded-full text-sm"
              >
                <EntityIcon type={entity.type} />
                <span className="text-gray-300">{entity.name}</span>
                <span className="text-gray-500 text-xs capitalize">({entity.type})</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Original Content */}
      {article.original_content && (
        <div className="bg-dark-200 rounded-xl p-6 border border-gray-800">
          <h2 className="text-lg font-semibold text-white mb-4">Original Content</h2>
          <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">
            {article.original_content}
          </p>
        </div>
      )}
    </div>
  )
}

function AnalysisCard({
  icon: Icon,
  title,
  content,
  color,
}: {
  icon: any
  title: string
  content?: string
  color: 'blue' | 'red' | 'yellow' | 'green'
}) {
  const colors = {
    blue: 'bg-blue-500/10 border-blue-500/30 text-blue-400',
    red: 'bg-red-500/10 border-red-500/30 text-red-400',
    yellow: 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400',
    green: 'bg-green-500/10 border-green-500/30 text-green-400',
  }

  if (!content) return null

  return (
    <div className={`rounded-xl p-5 border ${colors[color]}`}>
      <div className="flex items-center gap-2 mb-3">
        <Icon className="w-5 h-5" />
        <h3 className="font-semibold">{title}</h3>
      </div>
      <p className="text-gray-300 text-sm leading-relaxed">{content}</p>
    </div>
  )
}

function ScoreBar({
  label,
  score,
  color,
}: {
  label: string
  score: number
  color: 'blue' | 'red' | 'yellow' | 'green'
}) {
  const colors = {
    blue: 'bg-blue-500',
    red: 'bg-red-500',
    yellow: 'bg-yellow-500',
    green: 'bg-green-500',
  }

  const percentage = Math.round(score * 100)

  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-400">{label}</span>
        <span className="text-gray-300">{percentage}%</span>
      </div>
      <div className="h-2 bg-dark-400 rounded-full overflow-hidden">
        <div
          className={`h-full ${colors[color]} rounded-full transition-all`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}

function EntityIcon({ type }: { type: string }) {
  switch (type) {
    case 'country':
      return <Globe2 className="w-3 h-3 text-gray-500" />
    case 'location':
      return <MapPin className="w-3 h-3 text-gray-500" />
    default:
      return <Tag className="w-3 h-3 text-gray-500" />
  }
}
