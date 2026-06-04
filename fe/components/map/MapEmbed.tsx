'use client'

import { Restaurant } from '@/lib/types'

const MAPS_KEY = process.env.NEXT_PUBLIC_GOOGLE_MAPS_KEY || ''

export function MapEmbed({ restaurants }: { restaurants: Restaurant[] }) {
  if (!restaurants?.length) {
    return (
      <div className="h-64 flex items-center justify-center bg-white/5 rounded-2xl border border-white/10">
        <p className="text-gray-500 text-sm">Chưa có quán ăn nào để hiển thị</p>
      </div>
    )
  }

  // Lấy quán đầu tiên làm center
  const center = restaurants[0]
  const query = restaurants.map((r) => encodeURIComponent(r.name)).join('|')

  if (!MAPS_KEY) {
    // Fallback khi không có key: hiển thị danh sách với link
    return (
      <div className="space-y-2">
        <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl px-3 py-2 text-xs text-amber-400">
          ⚠️ Chưa có Google Maps API key. Thêm vào <code>.env.local</code> để xem bản đồ.
        </div>
        <div className="space-y-2">
          {restaurants.map((r) => (
            <a
              key={r.place_id}
              href={r.maps_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 p-3 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl transition-colors"
            >
              <span className="text-2xl">📍</span>
              <div>
                <p className="text-white text-sm font-medium">{r.name}</p>
                <p className="text-gray-500 text-xs">{r.address}</p>
              </div>
            </a>
          ))}
        </div>
      </div>
    )
  }

  const src = `https://www.google.com/maps/embed/v1/search?key=${MAPS_KEY}&q=${query}&center=${center.distance_km},${center.rating}`

  return (
    <div className="rounded-2xl overflow-hidden border border-white/10">
      <iframe
        src={src}
        width="100%"
        height="300"
        loading="lazy"
        allowFullScreen
        referrerPolicy="no-referrer-when-downgrade"
        className="w-full"
        title="Bản đồ quán ăn"
      />
    </div>
  )
}
