import { useState } from 'react'
import { User, Shield, Database, RefreshCw, Check, Settings as SettingsIcon } from 'lucide-react'

export default function Settings() {
  const [saved, setSaved] = useState(false)

  const handleSave = () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="max-w-3xl space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-army-olive font-['Roboto_Condensed'] uppercase tracking-wide">
          Configuration
        </h1>
        <p className="text-gray-600 mt-1">Configure your preferences</p>
      </div>

      {/* Profile */}
      <div className="bg-white rounded-xl border-2 border-army-khaki/30 shadow-sm overflow-hidden">
        <div className="p-4 border-b-2 border-army-khaki/30 bg-army-olive">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2 font-['Roboto_Condensed'] uppercase">
            <User className="w-5 h-5" />
            Profile
          </h2>
        </div>
        <div className="p-4 space-y-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">Display Name</label>
            <input
              type="text"
              defaultValue="Demo Analyst"
              className="w-full bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg px-3 py-2 text-gray-800 focus:outline-none focus:border-army-olive"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">Organization</label>
            <input
              type="text"
              defaultValue="Strategic Analysis Unit"
              className="w-full bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg px-3 py-2 text-gray-800 focus:outline-none focus:border-army-olive"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">Email</label>
            <input
              type="email"
              defaultValue="demo@example.com"
              className="w-full bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg px-3 py-2 text-gray-800 focus:outline-none focus:border-army-olive"
            />
          </div>
        </div>
      </div>

      {/* Preferences */}
      <div className="bg-white rounded-xl border-2 border-army-khaki/30 shadow-sm overflow-hidden">
        <div className="p-4 border-b-2 border-army-khaki/30 bg-army-olive">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2 font-['Roboto_Condensed'] uppercase">
            <Shield className="w-5 h-5" />
            Intelligence Preferences
          </h2>
        </div>
        <div className="p-4 space-y-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">Priority Regions</label>
            <input
              type="text"
              placeholder="e.g., South Asia, Indo-Pacific"
              className="w-full bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg px-3 py-2 text-gray-800 focus:outline-none focus:border-army-olive"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">Priority Themes</label>
            <input
              type="text"
              placeholder="e.g., Great Power Competition, Maritime Security"
              className="w-full bg-army-sand/30 border-2 border-army-khaki/50 rounded-lg px-3 py-2 text-gray-800 focus:outline-none focus:border-army-olive"
            />
          </div>
        </div>
      </div>

      {/* System Info */}
      <div className="bg-white rounded-xl border-2 border-army-khaki/30 shadow-sm overflow-hidden">
        <div className="p-4 border-b-2 border-army-khaki/30 bg-army-olive">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2 font-['Roboto_Condensed'] uppercase">
            <Database className="w-5 h-5" />
            System Status
          </h2>
        </div>
        <div className="p-4 space-y-3 text-sm">
          <div className="flex justify-between py-2 border-b border-army-khaki/20">
            <span className="text-gray-600 font-medium">Version</span>
            <span className="text-gray-800 font-semibold">1.0.0</span>
          </div>
          <div className="flex justify-between py-2 border-b border-army-khaki/20">
            <span className="text-gray-600 font-medium">API Status</span>
            <span className="text-green-600 flex items-center gap-1 font-semibold">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              Connected
            </span>
          </div>
          <div className="flex justify-between py-2 border-b border-army-khaki/20">
            <span className="text-gray-600 font-medium">LLM Provider</span>
            <span className="text-gray-800 font-semibold">Groq (Llama 3.1)</span>
          </div>
          <div className="flex justify-between py-2">
            <span className="text-gray-600 font-medium">Intel Fetch Interval</span>
            <span className="text-gray-800 font-semibold">30 minutes</span>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end gap-3">
        <button className="px-4 py-2 border-2 border-army-khaki text-gray-700 rounded-lg hover:border-army-olive transition-colors font-semibold">
          Reset Defaults
        </button>
        <button
          onClick={handleSave}
          className="flex items-center gap-2 px-4 py-2 bg-army-olive text-white rounded-lg hover:bg-army-olive-dark transition-colors font-semibold"
        >
          {saved ? (
            <>
              <Check className="w-4 h-4" />
              Saved!
            </>
          ) : (
            <>
              <RefreshCw className="w-4 h-4" />
              Save Changes
            </>
          )}
        </button>
      </div>
    </div>
  )
}
