import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { setupDefaultAccounts } from '../services/api'

interface Account {
  username: string
  password?: string
  role: string
}

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [accounts, setAccounts] = useState<Account[]>([])
  const [showAccounts, setShowAccounts] = useState(false)
  const [setupMessage, setSetupMessage] = useState('')

  const { login } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    const setupAccounts = async () => {
      try {
        const result = await setupDefaultAccounts()
        setAccounts(result.accounts)
        if (result.accounts.some(a => a.password)) {
          setSetupMessage('Default accounts created!')
        }
      } catch (err) {
        console.error('Failed to setup accounts:', err)
      }
    }
    setupAccounts()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      await login({ username, password })
      navigate('/')
    } catch (err: any) {
      setError(err.message || 'Login failed')
    } finally {
      setIsLoading(false)
    }
  }

  const handleQuickLogin = async (user: string, pass: string) => {
    setUsername(user)
    setPassword(pass)
    setIsLoading(true)
    setError('')
    try {
      await login({ username: user, password: pass })
      navigate('/')
    } catch (err: any) {
      setError(err.message || 'Login failed')
    } finally {
      setIsLoading(false)
    }
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
    <div className="min-h-screen bg-gradient-to-br from-army-sand via-army-cream to-army-khaki-light flex">
      {/* Left Panel - Army Imagery */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        <div className="absolute inset-0 bg-army-olive">
          {/* Army themed background pattern */}
          <div className="absolute inset-0 opacity-10">
            <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
              <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
                <path d="M 10 0 L 0 0 0 10" fill="none" stroke="currentColor" strokeWidth="0.5"/>
              </pattern>
              <rect width="100" height="100" fill="url(#grid)" className="text-army-gold"/>
            </svg>
          </div>

          {/* Ashoka Chakra inspired design */}
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
            <div className="w-64 h-64 rounded-full border-8 border-army-gold opacity-20"></div>
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-48 h-48 rounded-full border-4 border-army-gold opacity-30"></div>
          </div>
        </div>

        {/* Content overlay */}
        <div className="relative z-10 flex flex-col justify-center items-center w-full p-12 text-white">
          <div className="text-center">
            {/* Indian Army Emblem placeholder */}
            <div className="w-32 h-32 mx-auto mb-8 bg-army-gold rounded-full flex items-center justify-center shadow-2xl">
              <svg className="w-20 h-20 text-army-olive" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
              </svg>
            </div>

            <h1 className="text-4xl font-bold font-['Roboto_Condensed'] tracking-wide mb-4">
              STRATEGIC INTELLIGENCE
            </h1>
            <h2 className="text-2xl font-['Roboto_Condensed'] text-army-gold mb-6">
              BUREAU
            </h2>
            <div className="w-24 h-1 bg-army-gold mx-auto mb-6"></div>
            <p className="text-lg text-army-khaki-light max-w-md">
              Defence & Geopolitical News Intelligence Platform
            </p>

            {/* Motto */}
            <div className="mt-12 border-t border-b border-army-gold/30 py-4">
              <p className="text-army-gold font-['Roboto_Condensed'] text-xl tracking-widest">
                "SERVICE BEFORE SELF"
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Mobile Logo */}
          <div className="lg:hidden text-center mb-8">
            <div className="w-20 h-20 mx-auto mb-4 bg-army-olive rounded-full flex items-center justify-center shadow-lg">
              <svg className="w-12 h-12 text-army-gold" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-army-olive font-['Roboto_Condensed']">
              STRATEGIC INTELLIGENCE BUREAU
            </h1>
          </div>

          {/* Setup Message */}
          {setupMessage && (
            <div className="bg-army-olive/10 border-l-4 border-army-olive rounded-r-lg p-4 mb-6">
              <p className="text-army-olive text-sm font-medium">{setupMessage}</p>
            </div>
          )}

          {/* Login Card */}
          <div className="bg-white rounded-xl shadow-xl border border-army-khaki/30 overflow-hidden">
            {/* Card Header */}
            <div className="bg-army-olive px-6 py-4">
              <h2 className="text-xl font-semibold text-white font-['Roboto_Condensed'] tracking-wide">
                SECURE LOGIN
              </h2>
              <p className="text-army-khaki-light text-sm mt-1">Access Intelligence Dashboard</p>
            </div>

            <div className="p-6">
              {error && (
                <div className="bg-red-50 border-l-4 border-army-maroon rounded-r-lg p-4 mb-6">
                  <p className="text-army-maroon text-sm">{error}</p>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">
                    Username / Email
                  </label>
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full px-4 py-3 bg-army-sand/50 border-2 border-army-khaki/50 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:border-army-olive focus:ring-2 focus:ring-army-olive/20 transition-all"
                    placeholder="Enter your username"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">
                    Password
                  </label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-4 py-3 bg-army-sand/50 border-2 border-army-khaki/50 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:border-army-olive focus:ring-2 focus:ring-army-olive/20 transition-all"
                    placeholder="Enter your password"
                    required
                  />
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full py-3 bg-army-olive hover:bg-army-olive-dark text-white font-semibold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl uppercase tracking-wide"
                >
                  {isLoading ? 'Authenticating...' : 'Login'}
                </button>
              </form>

              {/* Quick Access */}
              <div className="mt-6">
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t-2 border-army-khaki/30"></div>
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-3 bg-white text-gray-500 font-medium uppercase tracking-wide">
                      Quick Access
                    </span>
                  </div>
                </div>

                <div className="mt-4 grid grid-cols-3 gap-3">
                  <button
                    onClick={() => handleQuickLogin('admin', 'admin123')}
                    disabled={isLoading}
                    className="py-2 px-3 bg-army-maroon hover:bg-army-maroon-light text-white text-sm font-semibold rounded-lg transition-all disabled:opacity-50 shadow"
                  >
                    Admin
                  </button>
                  <button
                    onClick={() => handleQuickLogin('analyst', 'analyst123')}
                    disabled={isLoading}
                    className="py-2 px-3 bg-army-olive hover:bg-army-olive-light text-white text-sm font-semibold rounded-lg transition-all disabled:opacity-50 shadow"
                  >
                    Analyst
                  </button>
                  <button
                    onClick={() => handleQuickLogin('demo', 'demo123')}
                    disabled={isLoading}
                    className="py-2 px-3 bg-army-khaki hover:bg-army-khaki-dark text-army-olive-dark text-sm font-semibold rounded-lg transition-all disabled:opacity-50 shadow"
                  >
                    Viewer
                  </button>
                </div>

                {/* Show credentials toggle */}
                <button
                  onClick={() => setShowAccounts(!showAccounts)}
                  className="mt-4 w-full text-sm text-army-olive hover:text-army-olive-dark font-medium"
                >
                  {showAccounts ? 'Hide' : 'Show'} account credentials
                </button>

                {showAccounts && (
                  <div className="mt-3 p-4 bg-army-sand/50 rounded-lg border border-army-khaki/30 space-y-2">
                    {accounts.map((acc) => (
                      <div key={acc.username} className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-0.5 rounded text-xs font-semibold uppercase ${getRoleBadgeColor(acc.role)}`}>
                            {acc.role}
                          </span>
                          <span className="text-gray-700 font-medium">{acc.username}</span>
                        </div>
                        <span className="text-gray-500 font-mono text-xs">
                          {acc.password || `${acc.username}123`}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="mt-6 text-center">
                <p className="text-gray-600">
                  New user?{' '}
                  <Link to="/register" className="text-army-olive hover:text-army-olive-dark font-semibold">
                    Register here
                  </Link>
                </p>
              </div>
            </div>
          </div>

          {/* Footer */}
          <p className="mt-6 text-center text-sm text-gray-500">
            Defence & Strategic Intelligence Platform
          </p>
        </div>
      </div>
    </div>
  )
}
