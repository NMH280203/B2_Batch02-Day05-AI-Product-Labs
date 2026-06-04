import { Restaurant } from '@/lib/types'
import { Badge } from '@/components/ui/Badge'

function StarRating({ rating }: { rating: number }) {
  const stars = Math.round(rating)
  return (
    <div className="flex items-center gap-1">
      {[1, 2, 3, 4, 5].map((s) => (
        <span key={s} className={s <= stars ? 'text-yellow-400' : 'text-gray-600'} style={{ fontSize: '10px' }}>
          ★
        </span>
      ))}
      <span className="text-gray-400 text-xs ml-1">{rating.toFixed(1)}</span>
    </div>
  )
}

function PriceLevel({ level }: { level: number }) {
  return (
    <span className="text-emerald-400 text-xs font-medium">
      {'$'.repeat(level)}<span className="text-gray-600">{'$'.repeat(4 - level)}</span>
    </span>
  )
}

export function RestaurantCard({ restaurant }: { restaurant: Restaurant }) {
  return (
    <div className="group bg-white/5 hover:bg-white/10 border border-white/10 hover:border-emerald-500/40 rounded-2xl p-4 transition-all duration-300 hover:shadow-lg hover:shadow-emerald-500/10">
      {/* Header */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-white text-sm group-hover:text-emerald-300 transition-colors truncate">
            {restaurant.name}
          </h3>
          <p className="text-gray-500 text-xs mt-0.5 truncate">📍 {restaurant.address}</p>
        </div>
        <Badge variant={restaurant.is_open ? 'success' : 'danger'} className="shrink-0">
          {restaurant.is_open ? '🟢 Đang mở' : '🔴 Đóng cửa'}
        </Badge>
      </div>

      {/* Meta */}
      <div className="flex items-center gap-3 mb-3">
        <StarRating rating={restaurant.rating} />
        <span className="text-gray-600">|</span>
        <PriceLevel level={restaurant.price_level} />
        <span className="text-gray-600">|</span>
        <span className="text-sky-400 text-xs">{restaurant.distance_km.toFixed(1)} km</span>
      </div>

      {/* Featured dishes */}
      {restaurant.featured_dishes?.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-3">
          {restaurant.featured_dishes.slice(0, 4).map((dish) => (
            <Badge key={dish} variant="default" className="text-[10px]">
              {dish}
            </Badge>
          ))}
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-2">
        <a
          href={restaurant.maps_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded-lg text-xs font-medium hover:bg-emerald-500/30 transition-colors"
        >
          🗺️ Xem bản đồ
        </a>
        {restaurant.phone && (
          <a
            href={`tel:${restaurant.phone}`}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-sky-500/20 text-sky-400 border border-sky-500/30 rounded-lg text-xs font-medium hover:bg-sky-500/30 transition-colors"
          >
            📞 Gọi ngay
          </a>
        )}
      </div>
    </div>
  )
}
