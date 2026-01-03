import { Search, Bell, User, LogOut, Shield, ChevronDown } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'

export default function Header() {
  const [searchQuery, setSearchQuery] = useState('')
  const [showUserMenu, setShowUserMenu] = useState(false)
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      navigate(`/articles?search=${encodeURIComponent(searchQuery)}`)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'admin':
        return 'bg-army-maroon text-white'
      case 'analyst':
        return 'bg-army-olive text-white'
      default:
        return 'bg-army-khaki text-army-olive-dark'
    }
  }

  return (
    <header className="h-16 bg-white border-b-2 border-army-khaki/30 flex items-center justify-between px-6 shadow-sm">
      {/* Left - Title & Search */}
      <div className="flex items-center gap-6 flex-1">
        <div className="hidden md:block">
          <h2 className="text-lg font-bold text-army-olive font-['Roboto_Condensed'] uppercase tracking-wide">
            Intelligence Dashboard
          </h2>
          <p className="text-xs text-gray-500">Real-time Strategic Analysis</p>
        </div>

        {/* Search */}
        <form onSubmit={handleSearch} className="flex-1 max-w-xl">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-army-khaki-dark" />
            <input
              type="text"
              placeholder="Search intelligence reports, regions, threats..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-2.5 bg-army-sand/50 border-2 border-army-khaki/30 rounded-lg text-gray-800 placeholder-gray-500 focus:outline-none focus:border-army-olive focus:ring-2 focus:ring-army-olive/20 transition-all"
            />
          </div>
        </form>
      </div>

      {/* Right - Actions */}
      <div className="flex items-center gap-3 ml-4">
        {/* Alert Status Indicator */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 bg-army-maroon/10 border border-army-maroon/30 rounded-lg">
          <div className="w-2 h-2 bg-army-maroon rounded-full animate-pulse"></div>
          <span className="text-xs font-semibold text-army-maroon uppercase">High Alert</span>
        </div>

        {/* Notifications */}
        <button className="relative p-2.5 text-army-olive hover:bg-army-sand rounded-lg transition-colors">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-army-maroon rounded-full border-2 border-white"></span>
        </button>

        {/* User Menu */}
        <div className="relative">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-3 px-3 py-2 bg-army-sand/50 hover:bg-army-sand rounded-lg transition-colors border border-army-khaki/30"
          >
            <div className="w-8 h-8 bg-army-olive rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-army-gold" />
            </div>
            <div className="hidden md:block text-left">
              <span className="text-sm font-semibold text-gray-800 block">
                {user?.full_name || user?.username || 'Operator'}
              </span>
              <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${getRoleBadgeColor(user?.role || 'viewer')}`}>
                {user?.role?.toUpperCase()}
              </span>
            </div>
            <ChevronDown className="w-4 h-4 text-gray-500 hidden md:block" />
          </button>

          {/* Dropdown Menu */}
          {showUserMenu && (
            <div className="absolute right-0 top-full mt-2 w-64 bg-white border-2 border-army-khaki/30 rounded-xl shadow-xl z-50 overflow-hidden">
              <div className="p-4 bg-army-olive">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-army-gold rounded-full flex items-center justify-center">
                    <Shield className="w-6 h-6 text-army-olive" />
                  </div>
                  <div>
                    <p className="font-semibold text-white">
                      {user?.full_name || user?.username}
                    </p>
                    <p className="text-xs text-army-khaki-light">{user?.email}</p>
                  </div>
                </div>
                <div className="mt-3 flex items-center gap-2">
                  <span className={`px-2 py-1 rounded text-xs font-semibold uppercase ${getRoleBadgeColor(user?.role || 'viewer')}`}>
                    {user?.role}
                  </span>
                  <span className="text-xs text-army-khaki-light">
                    {user?.organization || 'Strategic Command'}
                  </span>
                </div>
              </div>
              <div className="p-2">
                <button
                  onClick={() => {
                    setShowUserMenu(false)
                    navigate('/settings')
                  }}
                  className="w-full flex items-center gap-3 px-4 py-3 text-sm text-gray-700 hover:bg-army-sand rounded-lg transition-colors"
                >
                  <User className="w-4 h-4 text-army-olive" />
                  Profile Settings
                </button>
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-3 px-4 py-3 text-sm text-army-maroon hover:bg-red-50 rounded-lg transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                  Sign Out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Click outside to close menu */}
      {showUserMenu && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowUserMenu(false)}
        />
      )}
    </header>
  )
}
