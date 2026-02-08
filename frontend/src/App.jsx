import React, { useState } from 'react'
import {
  Plane, MapPin, Calendar, DollarSign, Sparkles,
  Clock, Share2, Download, ChevronDown, ChevronUp,
  ExternalLink, Utensils, Camera, Hotel, Compass,
  Globe, MessageCircle, Copy, Check, Loader2, Play
} from 'lucide-react'

// API URL - change this in production
const API_URL = '/api'

function App() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [itinerary, setItinerary] = useState(null)
  const [expandedDays, setExpandedDays] = useState({})
  const [copied, setCopied] = useState(false)
  const [preferences, setPreferences] = useState('')
  const [duration, setDuration] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!url.trim()) return

    setLoading(true)
    setError(null)
    setItinerary(null)

    try {
      const response = await fetch(`${API_URL}/extract`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: url.trim(),
          trip_duration: duration ? parseInt(duration) : null,
          preferences: preferences || null
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to extract itinerary')
      }

      const data = await response.json()
      setItinerary(data)

      // Expand first day by default
      setExpandedDays({ 1: true })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleDemo = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`${API_URL}/extract/demo`, {
        method: 'POST',
      })
      const data = await response.json()
      setItinerary(data)
      setExpandedDays({ 1: true })
    } catch (err) {
      setError('Failed to load demo')
    } finally {
      setLoading(false)
    }
  }

  const toggleDay = (day) => {
    setExpandedDays(prev => ({
      ...prev,
      [day]: !prev[day]
    }))
  }

  const copyToClipboard = () => {
    const text = formatItineraryAsText(itinerary)
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const getLocationIcon = (type) => {
    switch (type) {
      case 'restaurant': return <Utensils className="w-4 h-4" />
      case 'attraction': return <Camera className="w-4 h-4" />
      case 'hotel': return <Hotel className="w-4 h-4" />
      case 'activity': return <Compass className="w-4 h-4" />
      default: return <MapPin className="w-4 h-4" />
    }
  }

  const formatItineraryAsText = (itin) => {
    let text = `${itin.destination} - ${itin.duration_days} Day Itinerary\n`
    text += `${itin.summary}\n\n`

    itin.days.forEach(day => {
      text += `Day ${day.day}: ${day.title}\n`
      day.locations.forEach(loc => {
        text += `  - ${loc.name} (${loc.type})\n`
        if (loc.tips) text += `    Tip: ${loc.tips}\n`
      })
      text += '\n'
    })

    return text
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-orange-50">
      {/* Header */}
      <header className="border-b border-slate-100 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 gradient-bg rounded-xl flex items-center justify-center">
              <Play className="w-5 h-5 text-white fill-white" />
            </div>
            <span className="text-xl font-bold">
              <span className="gradient-text">TikTok</span>
              <span className="text-slate-800">toTrip</span>
            </span>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={handleDemo}
              className="text-sm text-slate-600 hover:text-slate-900 transition"
            >
              Try Demo
            </button>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-slate-600 hover:text-slate-900 transition"
            >
              GitHub
            </a>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Hero Section */}
        {!itinerary && (
          <div className="text-center mb-12 pt-8">
            <h1 className="text-4xl md:text-5xl font-extrabold text-slate-900 mb-4">
              Turn Travel <span className="gradient-text">Inspiration</span>
              <br />Into Your Next Trip
            </h1>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto mb-8">
              Paste a TikTok or Instagram travel video URL and we'll transform it into
              a detailed, actionable itinerary you can actually use.
            </p>

            {/* Input Form */}
            <form onSubmit={handleSubmit} className="max-w-2xl mx-auto">
              <div className="bg-white rounded-2xl shadow-lg shadow-slate-200/50 p-2 mb-4">
                <div className="flex flex-col md:flex-row gap-2">
                  <input
                    type="text"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="Paste TikTok, Instagram, or YouTube URL..."
                    className="flex-1 px-4 py-3 rounded-xl bg-slate-50 border-0 focus:outline-none focus:ring-2 focus:ring-orange-500/20 text-slate-800 placeholder:text-slate-400"
                  />
                  <button
                    type="submit"
                    disabled={loading || !url.trim()}
                    className="gradient-bg text-white px-6 py-3 rounded-xl font-semibold hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-5 h-5" />
                        Generate Trip
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Optional preferences */}
              <div className="flex flex-col md:flex-row gap-4 justify-center text-sm">
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-slate-400" />
                  <input
                    type="number"
                    min="1"
                    max="30"
                    value={duration}
                    onChange={(e) => setDuration(e.target.value)}
                    placeholder="Days (optional)"
                    className="px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 w-32"
                  />
                </div>
                <div className="flex items-center gap-2">
                  <Compass className="w-4 h-4 text-slate-400" />
                  <select
                    value={preferences}
                    onChange={(e) => setPreferences(e.target.value)}
                    className="px-3 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700"
                  >
                    <option value="">Travel style (optional)</option>
                    <option value="budget">Budget-friendly</option>
                    <option value="luxury">Luxury</option>
                    <option value="foodie">Foodie focus</option>
                    <option value="adventure">Adventure</option>
                    <option value="relaxed">Relaxed pace</option>
                    <option value="family">Family-friendly</option>
                  </select>
                </div>
              </div>
            </form>

            {/* Error */}
            {error && (
              <div className="mt-6 p-4 bg-red-50 border border-red-100 rounded-xl text-red-600 max-w-2xl mx-auto">
                {error}
              </div>
            )}

            {/* Features */}
            <div className="grid md:grid-cols-3 gap-6 mt-16">
              <FeatureCard
                icon={<Globe className="w-6 h-6" />}
                title="Any Platform"
                description="Works with TikTok, Instagram Reels, and YouTube videos"
              />
              <FeatureCard
                icon={<Sparkles className="w-6 h-6" />}
                title="AI-Powered"
                description="Extracts locations, restaurants, and activities automatically"
              />
              <FeatureCard
                icon={<MapPin className="w-6 h-6" />}
                title="Actionable"
                description="Get addresses, tips, and even booking links"
              />
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && !itinerary && (
          <div className="text-center py-16">
            <div className="inline-flex items-center justify-center w-16 h-16 gradient-bg rounded-full mb-6 animate-pulse-slow">
              <Plane className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2">Creating Your Itinerary</h2>
            <p className="text-slate-600 mb-8">Analyzing video content and building your personalized trip plan...</p>
            <div className="flex justify-center gap-2">
              {[0, 1, 2].map((i) => (
                <div
                  key={i}
                  className="w-3 h-3 rounded-full gradient-bg animate-bounce"
                  style={{ animationDelay: `${i * 0.15}s` }}
                />
              ))}
            </div>
          </div>
        )}

        {/* Itinerary Display */}
        {itinerary && (
          <div className="animate-fade-in">
            {/* Header */}
            <div className="bg-white rounded-2xl shadow-lg shadow-slate-200/50 p-6 md:p-8 mb-6">
              <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4 mb-6">
                <div>
                  <h1 className="text-3xl md:text-4xl font-bold text-slate-900 mb-2">
                    {itinerary.destination}
                  </h1>
                  <div className="flex flex-wrap items-center gap-3 text-sm text-slate-600">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-4 h-4" />
                      {itinerary.duration_days} days
                    </span>
                    <span className="flex items-center gap-1">
                      <Sparkles className="w-4 h-4 text-orange-500" />
                      {itinerary.vibe}
                    </span>
                    {itinerary.estimated_budget && (
                      <span className="flex items-center gap-1">
                        <DollarSign className="w-4 h-4" />
                        {itinerary.estimated_budget}
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={copyToClipboard}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-200 hover:bg-slate-50 transition text-sm"
                  >
                    {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
                    {copied ? 'Copied!' : 'Copy'}
                  </button>
                  <button
                    onClick={() => {
                      setItinerary(null)
                      setUrl('')
                    }}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl gradient-bg text-white text-sm hover:opacity-90 transition"
                  >
                    <Sparkles className="w-4 h-4" />
                    New Trip
                  </button>
                </div>
              </div>

              <p className="text-slate-600 text-lg">{itinerary.summary}</p>

              {itinerary.source_creator && (
                <div className="mt-4 pt-4 border-t border-slate-100 text-sm text-slate-500">
                  Based on content from <span className="font-medium text-slate-700">{itinerary.source_creator}</span>
                </div>
              )}
            </div>

            {/* Days */}
            <div className="space-y-4 mb-6">
              {itinerary.days.map((day) => (
                <div key={day.day} className="bg-white rounded-2xl shadow-lg shadow-slate-200/50 overflow-hidden">
                  <button
                    onClick={() => toggleDay(day.day)}
                    className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-50 transition"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 gradient-bg rounded-xl flex items-center justify-center text-white font-bold">
                        {day.day}
                      </div>
                      <div className="text-left">
                        <h3 className="font-semibold text-slate-900">{day.title}</h3>
                        <p className="text-sm text-slate-500">{day.locations.length} stops</p>
                      </div>
                    </div>
                    {expandedDays[day.day] ? (
                      <ChevronUp className="w-5 h-5 text-slate-400" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-slate-400" />
                    )}
                  </button>

                  {expandedDays[day.day] && (
                    <div className="px-6 pb-6">
                      {day.notes && (
                        <p className="text-sm text-slate-600 mb-4 p-3 bg-orange-50 rounded-xl">
                          {day.notes}
                        </p>
                      )}
                      <div className="space-y-4">
                        {day.locations.map((location, idx) => (
                          <LocationCard key={idx} location={location} getIcon={getLocationIcon} />
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Tips & Phrases */}
            <div className="grid md:grid-cols-2 gap-6">
              {itinerary.packing_tips && itinerary.packing_tips.length > 0 && (
                <div className="bg-white rounded-2xl shadow-lg shadow-slate-200/50 p-6">
                  <h3 className="font-bold text-slate-900 mb-4 flex items-center gap-2">
                    <span className="text-xl">🧳</span> Packing Tips
                  </h3>
                  <ul className="space-y-2">
                    {itinerary.packing_tips.map((tip, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-slate-600 text-sm">
                        <span className="text-orange-500 mt-1">•</span>
                        {tip}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {itinerary.local_phrases && itinerary.local_phrases.length > 0 && (
                <div className="bg-white rounded-2xl shadow-lg shadow-slate-200/50 p-6">
                  <h3 className="font-bold text-slate-900 mb-4 flex items-center gap-2">
                    <MessageCircle className="w-5 h-5 text-orange-500" /> Useful Phrases
                  </h3>
                  <div className="space-y-2">
                    {itinerary.local_phrases.map((phrase, idx) => (
                      <div key={idx} className="flex justify-between text-sm">
                        <span className="font-medium text-slate-800">{phrase.phrase}</span>
                        <span className="text-slate-500">{phrase.meaning}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-100 mt-16 py-8 text-center text-sm text-slate-500">
        <p>Built with AI to turn your travel dreams into reality.</p>
        <p className="mt-1">
          <a href="#" className="text-orange-500 hover:text-orange-600">TikToktoTrip</a> - POC Demo
        </p>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, description }) {
  return (
    <div className="bg-white rounded-2xl p-6 shadow-lg shadow-slate-200/50 text-left">
      <div className="w-12 h-12 gradient-bg-subtle rounded-xl flex items-center justify-center text-orange-500 mb-4">
        {icon}
      </div>
      <h3 className="font-semibold text-slate-900 mb-2">{title}</h3>
      <p className="text-slate-600 text-sm">{description}</p>
    </div>
  )
}

function LocationCard({ location, getIcon }) {
  return (
    <div className="flex gap-4 p-4 rounded-xl bg-slate-50 hover:bg-slate-100 transition">
      <div className="w-10 h-10 rounded-lg bg-white shadow-sm flex items-center justify-center text-orange-500 shrink-0">
        {getIcon(location.type)}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <h4 className="font-semibold text-slate-900">{location.name}</h4>
          {location.price_level && (
            <span className="text-xs font-medium text-slate-500 bg-white px-2 py-1 rounded-full">
              {location.price_level}
            </span>
          )}
        </div>
        {location.description && (
          <p className="text-sm text-slate-600 mt-1">{location.description}</p>
        )}
        {location.address && (
          <p className="text-xs text-slate-500 mt-2 flex items-center gap-1">
            <MapPin className="w-3 h-3" />
            {location.address}
          </p>
        )}
        {location.tips && (
          <p className="text-xs text-orange-600 mt-2 p-2 bg-orange-50 rounded-lg">
            💡 {location.tips}
          </p>
        )}
        {location.google_maps_url && (
          <a
            href={location.google_maps_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-xs text-orange-500 hover:text-orange-600 mt-2"
          >
            <ExternalLink className="w-3 h-3" />
            View on Google Maps
          </a>
        )}
      </div>
    </div>
  )
}

export default App
