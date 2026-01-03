import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import { getHotspots, getRegionStats, getCountryStats } from '../services/api'
import { ArrowUpRight, Globe2 } from 'lucide-react'
import 'leaflet/dist/leaflet.css'

export default function Regions() {
  const { data: hotspots } = useQuery({
    queryKey: ['hotspots'],
    queryFn: getHotspots,
  })

  const { data: regions } = useQuery({
    queryKey: ['region-stats'],
    queryFn: getRegionStats,
  })

  const { data: countries } = useQuery({
    queryKey: ['country-stats'],
    queryFn: () => getCountryStats(15),
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-army-olive font-['Roboto_Condensed'] uppercase tracking-wide">
          Theatre Map
        </h1>
        <p className="text-gray-600 mt-1">Geopolitical hotspots and regional coverage</p>
      </div>

      {/* Map */}
      <div className="bg-white rounded-xl border-2 border-army-khaki/30 overflow-hidden shadow-sm">
        <div className="h-96">
          <MapContainer
            center={[20, 80]}
            zoom={3}
            className="h-full w-full"
            style={{ background: '#F4E9D8' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {hotspots?.map((hotspot) => (
              <CircleMarker
                key={hotspot.region}
                center={[hotspot.lat, hotspot.lng]}
                radius={Math.max(hotspot.high_relevance * 2, 10)}
                pathOptions={{
                  color: hotspot.intensity > 0.5 ? '#800020' : '#D4AF37',
                  fillColor: hotspot.intensity > 0.5 ? '#800020' : '#D4AF37',
                  fillOpacity: 0.5,
                  weight: 2,
                }}
              >
                <Popup>
                  <div className="text-center">
                    <strong className="text-lg text-army-olive">{hotspot.region}</strong>
                    <p className="text-sm mt-1 text-gray-600">
                      {hotspot.total_articles} articles
                      <br />
                      {hotspot.high_relevance} critical priority
                    </p>
                  </div>
                </Popup>
              </CircleMarker>
            ))}
          </MapContainer>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Regions */}
        <div className="bg-white rounded-xl border-2 border-army-khaki/30 shadow-sm overflow-hidden">
          <div className="p-4 border-b-2 border-army-khaki/30 bg-army-olive">
            <h2 className="text-lg font-bold text-white font-['Roboto_Condensed'] uppercase">
              Coverage by Region
            </h2>
          </div>
          <div className="p-4 space-y-2">
            {regions?.map((region, index) => (
              <Link
                key={region.region}
                to={`/articles?region=${encodeURIComponent(region.region)}`}
                className="flex items-center justify-between p-3 rounded-lg hover:bg-army-sand/50 transition-colors border border-transparent hover:border-army-khaki/30"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-army-olive/10 rounded flex items-center justify-center text-sm font-bold text-army-olive">
                    {index + 1}
                  </div>
                  <span className="text-gray-800 font-medium">{region.region}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-gray-500 font-medium">{region.count} reports</span>
                  <ArrowUpRight className="w-4 h-4 text-army-olive" />
                </div>
              </Link>
            ))}
            {(!regions || regions.length === 0) && (
              <div className="text-center py-8">
                <Globe2 className="w-12 h-12 mx-auto mb-3 text-army-khaki" />
                <p className="text-gray-500">No region data available</p>
              </div>
            )}
          </div>
        </div>

        {/* Countries */}
        <div className="bg-white rounded-xl border-2 border-army-khaki/30 shadow-sm overflow-hidden">
          <div className="p-4 border-b-2 border-army-khaki/30 bg-army-olive">
            <h2 className="text-lg font-bold text-white font-['Roboto_Condensed'] uppercase">
              Top Countries
            </h2>
          </div>
          <div className="p-4 space-y-2">
            {countries?.map((country, index) => (
              <Link
                key={country.country}
                to={`/articles?country=${encodeURIComponent(country.country)}`}
                className="flex items-center justify-between p-3 rounded-lg hover:bg-army-sand/50 transition-colors border border-transparent hover:border-army-khaki/30"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-army-gold/20 rounded flex items-center justify-center text-sm font-bold text-army-olive">
                    {index + 1}
                  </div>
                  <span className="text-gray-800 font-medium">{country.country}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-gray-500 font-medium">{country.count} reports</span>
                  <ArrowUpRight className="w-4 h-4 text-army-olive" />
                </div>
              </Link>
            ))}
            {(!countries || countries.length === 0) && (
              <div className="text-center py-8">
                <Globe2 className="w-12 h-12 mx-auto mb-3 text-army-khaki" />
                <p className="text-gray-500">No country data available</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="bg-white rounded-xl p-4 border-2 border-army-khaki/30 shadow-sm">
        <h3 className="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wide">Map Legend</h3>
        <div className="flex items-center gap-6 flex-wrap">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-army-maroon opacity-70" />
            <span className="text-sm text-gray-600">High Activity</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-army-gold opacity-70" />
            <span className="text-sm text-gray-600">Moderate Activity</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">Circle size = number of critical reports</span>
          </div>
        </div>
      </div>
    </div>
  )
}
