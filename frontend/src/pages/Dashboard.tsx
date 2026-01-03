import { useQuery } from '@tanstack/react-query'
import {
  Newspaper,
  TrendingUp,
  AlertTriangle,
  Globe2,
  Clock,
  ArrowUpRight,
  Shield,
  Target,
  Radio,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import {
  getDashboardStats,
  getTrends,
  getRegionStats,
  getRecentHighImpact,
} from '../services/api'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import RelevanceBadge from '../components/articles/RelevanceBadge'

export default function Dashboard() {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: getDashboardStats,
  })

  const { data: trends } = useQuery({
    queryKey: ['dashboard-trends'],
    queryFn: () => getTrends(7),
  })

  const { data: regions } = useQuery({
    queryKey: ['region-stats'],
    queryFn: getRegionStats,
  })

  const { data: recentHigh } = useQuery({
    queryKey: ['recent-high-impact'],
    queryFn: () => getRecentHighImpact(5),
  })

  if (statsLoading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-32 bg-army-khaki/30 rounded-xl" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-army-olive font-['Roboto_Condensed'] uppercase tracking-wide">
            Strategic Command Centre
          </h1>
          <p className="text-gray-600 mt-1">Real-time geopolitical intelligence overview</p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 bg-army-olive text-white rounded-lg">
          <Radio className="w-4 h-4 animate-pulse" />
          <span className="text-sm font-semibold uppercase">Live Intel</span>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Intelligence Reports"
          value={stats?.total_articles || 0}
          icon={Newspaper}
          color="olive"
        />
        <StatCard
          title="Critical Priority"
          value={stats?.relevance_breakdown.high || 0}
          icon={AlertTriangle}
          color="maroon"
        />
        <StatCard
          title="Last 24 Hours"
          value={stats?.recent_activity.last_24h || 0}
          icon={Clock}
          color="gold"
        />
        <StatCard
          title="Active Sources"
          value={`${stats?.sources.active || 0}/${stats?.sources.total || 0}`}
          icon={Globe2}
          color="khaki"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Trend Chart */}
        <div className="bg-white rounded-xl p-6 border-2 border-army-khaki/30 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-army-olive font-['Roboto_Condensed'] uppercase">
              Intel Flow (7 Days)
            </h2>
            <div className="flex items-center gap-4 text-xs">
              <span className="flex items-center gap-1">
                <div className="w-3 h-3 bg-army-olive rounded"></div>
                Total
              </span>
              <span className="flex items-center gap-1">
                <div className="w-3 h-3 bg-army-maroon rounded"></div>
                Critical
              </span>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trends || []}>
                <defs>
                  <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#4B5320" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#4B5320" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorHigh" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#800020" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#800020" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="date"
                  stroke="#6b7280"
                  fontSize={12}
                  tickFormatter={(value) => value.slice(5)}
                />
                <YAxis stroke="#6b7280" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '2px solid #C3B091',
                    borderRadius: '8px',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="total"
                  stroke="#4B5320"
                  strokeWidth={2}
                  fill="url(#colorTotal)"
                  name="Total"
                />
                <Area
                  type="monotone"
                  dataKey="high_relevance"
                  stroke="#800020"
                  strokeWidth={2}
                  fill="url(#colorHigh)"
                  name="Critical"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Region Distribution */}
        <div className="bg-white rounded-xl p-6 border-2 border-army-khaki/30 shadow-sm">
          <h2 className="text-lg font-bold text-army-olive font-['Roboto_Condensed'] uppercase mb-4">
            Theatre Coverage
          </h2>
          <div className="space-y-3">
            {regions?.slice(0, 6).map((region, index) => (
              <div key={region.region} className="flex items-center gap-4">
                <div className="w-8 h-8 bg-army-olive/10 rounded flex items-center justify-center text-sm font-bold text-army-olive">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-semibold text-gray-700">{region.region}</span>
                    <span className="text-sm text-gray-500 font-medium">{region.count} reports</span>
                  </div>
                  <div className="h-2 bg-army-sand rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-army-olive to-army-olive-light rounded-full"
                      style={{
                        width: `${Math.min((region.count / (regions[0]?.count || 1)) * 100, 100)}%`,
                      }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* High Impact Articles */}
      <div className="bg-white rounded-xl border-2 border-army-khaki/30 shadow-sm overflow-hidden">
        <div className="p-6 border-b-2 border-army-khaki/30 bg-army-olive flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-army-gold rounded-lg flex items-center justify-center">
              <Target className="w-5 h-5 text-army-olive" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white font-['Roboto_Condensed'] uppercase">
                Priority Intelligence
              </h2>
              <p className="text-army-khaki-light text-sm">Critical strategic updates</p>
            </div>
          </div>
          <Link
            to="/articles?relevance_level=high"
            className="flex items-center gap-1 px-4 py-2 bg-army-gold text-army-olive-dark rounded-lg font-semibold text-sm hover:bg-army-gold-light transition-colors"
          >
            View All <ArrowUpRight className="w-4 h-4" />
          </Link>
        </div>
        <div className="divide-y divide-army-khaki/20">
          {recentHigh?.map((article: any, index: number) => (
            <Link
              key={article.id}
              to={`/articles/${article.id}`}
              className="block p-4 hover:bg-army-sand/30 transition-colors"
            >
              <div className="flex items-start gap-4">
                <div className="w-8 h-8 bg-army-maroon/10 rounded flex items-center justify-center text-sm font-bold text-army-maroon flex-shrink-0">
                  {index + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-gray-800 font-semibold truncate">{article.title}</h3>
                  <div className="flex items-center gap-3 mt-2 text-sm text-gray-500">
                    <span className="font-medium text-army-olive">{article.source}</span>
                    <span className="text-army-khaki">|</span>
                    <span>{article.region}</span>
                    {article.theme && (
                      <>
                        <span className="text-army-khaki">|</span>
                        <span>{article.theme}</span>
                      </>
                    )}
                  </div>
                </div>
                <RelevanceBadge level="high" score={article.relevance_score} />
              </div>
            </Link>
          ))}
          {(!recentHigh || recentHigh.length === 0) && (
            <div className="p-8 text-center text-gray-500">
              <Shield className="w-12 h-12 mx-auto mb-3 text-army-khaki" />
              <p>No priority intelligence yet.</p>
              <p className="text-sm mt-1">Reports will appear here as they are processed.</p>
            </div>
          )}
        </div>
      </div>

      {/* Relevance Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <RelevanceCard
          level="high"
          count={stats?.relevance_breakdown.high || 0}
          description="Critical strategic importance"
        />
        <RelevanceCard
          level="medium"
          count={stats?.relevance_breakdown.medium || 0}
          description="Moderate strategic relevance"
        />
        <RelevanceCard
          level="low"
          count={stats?.relevance_breakdown.low || 0}
          description="General news coverage"
        />
      </div>
    </div>
  )
}

function StatCard({
  title,
  value,
  icon: Icon,
  color,
}: {
  title: string
  value: number | string
  icon: any
  color: 'olive' | 'maroon' | 'gold' | 'khaki'
}) {
  const colors = {
    olive: {
      bg: 'bg-army-olive',
      icon: 'bg-army-gold text-army-olive',
      text: 'text-white',
    },
    maroon: {
      bg: 'bg-army-maroon',
      icon: 'bg-white text-army-maroon',
      text: 'text-white',
    },
    gold: {
      bg: 'bg-army-gold',
      icon: 'bg-army-olive text-army-gold',
      text: 'text-army-olive-dark',
    },
    khaki: {
      bg: 'bg-white border-2 border-army-khaki',
      icon: 'bg-army-olive text-army-gold',
      text: 'text-army-olive',
    },
  }

  const c = colors[color]

  return (
    <div className={`rounded-xl p-6 shadow-sm ${c.bg}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className={`text-sm uppercase tracking-wide font-medium ${color === 'khaki' ? 'text-gray-600' : 'opacity-80 ' + c.text}`}>
            {title}
          </p>
          <p className={`text-3xl font-bold mt-2 ${c.text}`}>{value}</p>
        </div>
        <div className={`p-3 rounded-lg ${c.icon}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  )
}

function RelevanceCard({
  level,
  count,
  description,
}: {
  level: 'high' | 'medium' | 'low'
  count: number
  description: string
}) {
  const colors = {
    high: 'border-army-maroon/30 bg-army-maroon/5 hover:bg-army-maroon/10',
    medium: 'border-army-gold/30 bg-army-gold/5 hover:bg-army-gold/10',
    low: 'border-army-olive/30 bg-army-olive/5 hover:bg-army-olive/10',
  }

  return (
    <Link
      to={`/articles?relevance_level=${level}`}
      className={`block p-6 rounded-xl border-2 ${colors[level]} transition-colors shadow-sm`}
    >
      <div className="flex items-center justify-between mb-2">
        <RelevanceBadge level={level} />
        <TrendingUp className="w-4 h-4 text-gray-400" />
      </div>
      <p className="text-2xl font-bold text-gray-800 mt-3">{count}</p>
      <p className="text-sm text-gray-500 mt-1">{description}</p>
    </Link>
  )
}
