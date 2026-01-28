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
        <div className="h-8 bg-army-khaki/30 rounded w-1/4" />
        <div className="h-12 bg-army-khaki/30 rounded w-3/4" />
        <div className="h-64 bg-army-khaki/30 rounded" />
      </div>
    )
  }

  if (!article) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Article not found</p>
        <Link to="/articles" className="text-army-olive hover:underline mt-4 inline-block font-semibold">
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
        className="inline-flex items-center gap-2 text-army-olive hover:text-army-olive-dark transition-colors font-semibold"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Intelligence
      </Link>

      {/* Header */}
      <div className="bg-white rounded-xl p-6 border-2 border-army-khaki/30 shadow-sm">
        <div className="flex flex-wrap items-center gap-3 mb-4">
          <RelevanceBadge level={article.relevance_level} score={article.relevance_score} />
          {article.region && (
            <span className="text-sm text-army-olive font-medium px-3 py-1 bg-army-sand rounded-full">
              {article.region}
            </span>
          )}
          {article.theme && (
            <span className="text-sm text-army-olive font-medium px-3 py-1 bg-army-sand rounded-full">
              {article.theme}
            </span>
          )}
          {article.domain && (
            <span className="text-sm text-army-olive font-medium px-3 py-1 bg-army-sand rounded-full capitalize">
              {article.domain}
            </span>
          )}
        </div>

        <h1 className="text-2xl font-bold text-gray-900 mb-4">{article.title}</h1>

        <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
          <span className="font-semibold text-army-olive">{article.source_name}</span>
          {article.published_at && (
            <>
              <span className="text-army-khaki">|</span>
              <span>{format(new Date(article.published_at), 'MMMM d, yyyy')}</span>
            </>
          )}
          {article.author && (
            <>
              <span className="text-army-khaki">|</span>
              <span>By {article.author}</span>
            </>
          )}
        </div>

        <a
          href={article.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 mt-4 px-4 py-2 bg-army-olive text-white rounded-lg hover:bg-army-olive-dark transition-colors font-semibold"
        >
          Read Original <ExternalLink className="w-4 h-4" />
        </a>
      </div>

      {/* Quick Summary - Bullet Points */}
      {article.summary_bullets && (
        <div className="bg-army-olive/5 rounded-xl p-6 border-2 border-army-olive/20 shadow-sm">
          <h2 className="text-lg font-bold text-army-olive font-['Roboto_Condensed'] uppercase tracking-wide mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Quick Summary
          </h2>
          <div className="space-y-2">
            {article.summary_bullets.split('\n').map((bullet, index) => (
              <p key={index} className="text-gray-800 leading-relaxed">
                {bullet}
              </p>
            ))}
          </div>
        </div>
      )}

      {/* Strategic Analysis */}
      {article.is_processed === 1 && (article.summary_what_happened || article.summary_why_matters) && (
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-army-olive font-['Roboto_Condensed'] uppercase tracking-wide">
            Strategic Analysis
          </h2>

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
              title="Strategic Implications"
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
      <div className="bg-white rounded-xl p-6 border-2 border-army-khaki/30 shadow-sm">
        <h2 className="text-lg font-bold text-army-olive font-['Roboto_Condensed'] uppercase tracking-wide mb-4">
          Relevance Breakdown
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <ScoreBar label="Geographic" score={article.geo_score} color="blue" />
          <ScoreBar label="Military" score={article.military_score} color="red" />
          <ScoreBar label="Diplomatic" score={article.diplomatic_score} color="yellow" />
          <ScoreBar label="Economic" score={article.economic_score} color="green" />
        </div>
      </div>

      {/* Entities */}
      {article.entities && article.entities.length > 0 && (
        <div className="bg-white rounded-xl p-6 border-2 border-army-khaki/30 shadow-sm">
          <h2 className="text-lg font-bold text-army-olive font-['Roboto_Condensed'] uppercase tracking-wide mb-4">
            Key Entities
          </h2>
          <div className="flex flex-wrap gap-2">
            {article.entities.map((entity, index) => (
              <span
                key={index}
                className="inline-flex items-center gap-2 px-3 py-1.5 bg-army-sand rounded-full text-sm border border-army-khaki/30"
              >
                <EntityIcon type={entity.type} />
                <span className="text-gray-800 font-medium">{entity.name}</span>
                <span className="text-gray-500 text-xs capitalize">({entity.type})</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Original Content */}
      {article.original_content && (
        <div className="bg-white rounded-xl p-6 border-2 border-army-khaki/30 shadow-sm">
          <h2 className="text-lg font-bold text-army-olive font-['Roboto_Condensed'] uppercase tracking-wide mb-4">
            Original Content
          </h2>
          <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
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
    blue: {
      bg: 'bg-blue-50',
      border: 'border-blue-300',
      icon: 'text-blue-600',
      title: 'text-blue-800',
    },
    red: {
      bg: 'bg-army-maroon/10',
      border: 'border-army-maroon/30',
      icon: 'text-army-maroon',
      title: 'text-army-maroon',
    },
    yellow: {
      bg: 'bg-army-gold/20',
      border: 'border-army-gold',
      icon: 'text-army-gold-light',
      title: 'text-amber-800',
    },
    green: {
      bg: 'bg-army-olive/10',
      border: 'border-army-olive/30',
      icon: 'text-army-olive',
      title: 'text-army-olive',
    },
  }

  if (!content) return null

  const colorSet = colors[color]

  return (
    <div className={`rounded-xl p-5 border-2 ${colorSet.bg} ${colorSet.border}`}>
      <div className="flex items-center gap-2 mb-3">
        <Icon className={`w-5 h-5 ${colorSet.icon}`} />
        <h3 className={`font-bold ${colorSet.title}`}>{title}</h3>
      </div>
      <p className="text-gray-700 text-sm leading-relaxed">{content}</p>
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
    red: 'bg-army-maroon',
    yellow: 'bg-army-gold',
    green: 'bg-army-olive',
  }

  const percentage = Math.round(score * 100)

  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600 font-medium">{label}</span>
        <span className="text-gray-800 font-semibold">{percentage}%</span>
      </div>
      <div className="h-2.5 bg-army-khaki/30 rounded-full overflow-hidden">
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
      return <Globe2 className="w-3 h-3 text-army-olive" />
    case 'location':
      return <MapPin className="w-3 h-3 text-army-maroon" />
    default:
      return <Tag className="w-3 h-3 text-army-gold" />
  }
}
