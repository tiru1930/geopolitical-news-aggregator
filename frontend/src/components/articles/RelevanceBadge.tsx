import type { RelevanceLevel } from '../../types'

interface RelevanceBadgeProps {
  level: RelevanceLevel
  score?: number
  size?: 'sm' | 'md'
}

export default function RelevanceBadge({ level, score, size = 'md' }: RelevanceBadgeProps) {
  const colors = {
    high: 'bg-army-maroon text-white',
    medium: 'bg-army-gold text-army-olive-dark',
    low: 'bg-army-olive text-white',
  }

  const labels = {
    high: 'CRITICAL',
    medium: 'PRIORITY',
    low: 'ROUTINE',
  }

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded font-semibold uppercase tracking-wide ${colors[level]} ${sizeClasses[size]}`}
    >
      <span
        className={`w-1.5 h-1.5 rounded-full ${
          level === 'high'
            ? 'bg-white animate-pulse'
            : level === 'medium'
            ? 'bg-army-olive'
            : 'bg-army-khaki'
        }`}
      />
      {labels[level]}
      {score !== undefined && (
        <span className="opacity-80 font-normal">({(score * 100).toFixed(0)}%)</span>
      )}
    </span>
  )
}
