import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Newspaper,
  Globe2,
  Rss,
  Bell,
  Settings,
  Shield,
  Target,
} from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard', description: 'Overview' },
  { path: '/articles', icon: Newspaper, label: 'Intelligence', description: 'News Feed' },
  { path: '/regions', icon: Globe2, label: 'Theatre Map', description: 'Regions' },
  { path: '/sources', icon: Rss, label: 'Sources', description: 'News Sources', adminOnly: true },
  { path: '/alerts', icon: Bell, label: 'Alerts', description: 'Notifications' },
  { path: '/settings', icon: Settings, label: 'Settings', description: 'Configuration' },
]

export default function Sidebar() {
  const { user } = useAuth()
  const isAdmin = user?.role === 'admin'

  const filteredNavItems = navItems.filter(item => !item.adminOnly || isAdmin)

  return (
    <aside className="w-72 bg-army-olive flex flex-col shadow-xl">
      {/* Logo / Header */}
      <div className="h-20 flex items-center gap-4 px-6 border-b border-army-olive-light/30 bg-army-olive-dark">
        <div className="w-12 h-12 bg-army-gold rounded-lg flex items-center justify-center shadow-lg">
          <Shield className="w-7 h-7 text-army-olive-dark" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide">
            प्रज्ञा
          </h1>
          <p className="text-xs text-army-khaki-light uppercase tracking-wider">
            News Aggregator
          </p>
        </div>
      </div>

      {/* User Badge */}
      <div className="px-4 py-3 bg-army-olive-dark/50 border-b border-army-olive-light/20">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-army-gold/20 border-2 border-army-gold flex items-center justify-center">
            <Target className="w-5 h-5 text-army-gold" />
          </div>
          <div>
            <p className="text-sm font-semibold text-white">
              {user?.full_name || user?.username || 'Operator'}
            </p>
            <p className="text-xs text-army-khaki uppercase tracking-wide">
              {user?.role || 'viewer'}
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        <p className="px-4 py-2 text-xs font-semibold text-army-khaki uppercase tracking-widest">
          Operations
        </p>
        {filteredNavItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                isActive
                  ? 'bg-army-gold text-army-olive-dark shadow-lg'
                  : 'text-army-khaki-light hover:bg-army-olive-light/30 hover:text-white'
              }`
            }
          >
            <item.icon className="w-5 h-5" />
            <div>
              <span className="font-semibold text-sm">{item.label}</span>
              <p className={`text-xs opacity-70`}>{item.description}</p>
            </div>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-army-olive-light/20 bg-army-olive-dark/30">
        <div className="px-2 text-xs text-army-khaki-light">
          <p className="font-semibold tracking-wide">प्रज्ञा</p>
          <p className="mt-1 opacity-70">v1.0.0 | Strategic Platform</p>
        </div>
      </div>
    </aside>
  )
}
