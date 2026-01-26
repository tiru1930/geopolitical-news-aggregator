import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Shield } from 'lucide-react'

type Role = 'analyst' | 'admin'

export default function Register() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    organization: '',
    role: 'analyst' as Role,
    invite_code: '',
  })
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const { register } = useAuth()
  const navigate = useNavigate()

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters')
      return
    }

    if (formData.role === 'admin' && !formData.invite_code) {
      setError('Invite code required for admin role')
      return
    }

    setIsLoading(true)

    try {
      await register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name || undefined,
        organization: formData.organization || undefined,
        role: formData.role,
        invite_code: formData.invite_code || undefined,
      })
      navigate('/')
    } catch (err: any) {
      setError(err.message || 'Registration failed')
    } finally {
      setIsLoading(false)
    }
  }

  const getRoleBadgeColor = (role: Role, isSelected: boolean) => {
    if (!isSelected) return 'bg-white text-gray-600 border-army-khaki/50 hover:border-army-olive'
    switch (role) {
      case 'admin':
        return 'bg-army-maroon text-white border-army-maroon'
      case 'analyst':
        return 'bg-army-olive text-white border-army-olive'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-army-sand via-army-cream to-army-khaki-light flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        {/* Logo/Header */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 mx-auto mb-4 bg-army-olive rounded-xl flex items-center justify-center shadow-lg">
            <Shield className="w-12 h-12 text-army-gold" />
          </div>
          <h1 className="text-3xl font-bold text-army-olive tracking-wide">
            प्रज्ञा
          </h1>
          <p className="text-gray-600 mt-1">Create your secure account</p>
        </div>

        {/* Registration Form */}
        <div className="bg-white rounded-xl shadow-xl border-2 border-army-khaki/30 overflow-hidden">
          <div className="bg-army-olive px-6 py-4">
            <h2 className="text-xl font-bold text-white font-['Roboto_Condensed'] uppercase tracking-wide">
              New Registration
            </h2>
            <p className="text-army-khaki-light text-sm mt-1">All fields marked * are required</p>
          </div>

          <div className="p-6">
            {error && (
              <div className="bg-red-50 border-l-4 border-army-maroon rounded-r-lg p-4 mb-6">
                <p className="text-army-maroon text-sm font-medium">{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">
                    Username *
                  </label>
                  <input
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    className="w-full px-4 py-3 bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:border-army-olive focus:ring-2 focus:ring-army-olive/20"
                    placeholder="username"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">
                    Full Name
                  </label>
                  <input
                    type="text"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                    className="w-full px-4 py-3 bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:border-army-olive focus:ring-2 focus:ring-army-olive/20"
                    placeholder="John Doe"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">
                  Email *
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:border-army-olive focus:ring-2 focus:ring-army-olive/20"
                  placeholder="you@example.com"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">
                  Organization
                </label>
                <input
                  type="text"
                  name="organization"
                  value={formData.organization}
                  onChange={handleChange}
                  className="w-full px-4 py-3 bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:border-army-olive focus:ring-2 focus:ring-army-olive/20"
                  placeholder="Company or unit"
                />
              </div>

              {/* Role Selection */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">
                  Access Level
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {(['analyst', 'admin'] as Role[]).map((role) => (
                    <button
                      key={role}
                      type="button"
                      onClick={() => setFormData({ ...formData, role })}
                      className={`py-3 px-3 text-sm font-semibold rounded-lg transition-all border-2 uppercase tracking-wide ${getRoleBadgeColor(role, formData.role === role)}`}
                    >
                      {role}
                    </button>
                  ))}
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  {formData.role === 'analyst' && 'Analyst access - Create and manage alerts'}
                  {formData.role === 'admin' && 'Admin access - Full system control (invite code required)'}
                </p>
              </div>

              {/* Invite Code - Only for Admin */}
              {formData.role === 'admin' && (
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">
                    Admin Invite Code *
                  </label>
                  <input
                    type="text"
                    name="invite_code"
                    value={formData.invite_code}
                    onChange={handleChange}
                    className="w-full px-4 py-3 bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:border-army-olive focus:ring-2 focus:ring-army-olive/20"
                    placeholder="Enter admin authorization code"
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Contact administrator for invite code
                  </p>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">
                    Password *
                  </label>
                  <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    className="w-full px-4 py-3 bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:border-army-olive focus:ring-2 focus:ring-army-olive/20"
                    placeholder="Min. 6 characters"
                    required
                    minLength={6}
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">
                    Confirm *
                  </label>
                  <input
                    type="password"
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    className="w-full px-4 py-3 bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg text-gray-900 placeholder-gray-500 focus:outline-none focus:border-army-olive focus:ring-2 focus:ring-army-olive/20"
                    placeholder="Repeat password"
                    required
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3 bg-army-olive hover:bg-army-olive-dark text-white font-semibold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg uppercase tracking-wide mt-4"
              >
                {isLoading ? 'Processing...' : 'Create Account'}
              </button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-gray-600">
                Already registered?{' '}
                <Link to="/login" className="text-army-olive hover:text-army-olive-dark font-semibold">
                  Sign in
                </Link>
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <p className="mt-6 text-center text-sm text-gray-500">
          By registering, you agree to security protocols
        </p>
      </div>
    </div>
  )
}
