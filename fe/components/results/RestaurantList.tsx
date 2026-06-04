import { Restaurant } from '@/lib/types'
import { RestaurantCard } from './RestaurantCard'

export function RestaurantList({ restaurants }: { restaurants: Restaurant[] }) {
  if (!restaurants?.length) return null
  return (
    <div className="mt-3 space-y-2">
      <p className="text-xs text-gray-500 font-medium uppercase tracking-wider mb-2">🏪 Quán gợi ý</p>
      <div className="space-y-2">
        {restaurants.map((r) => (
          <RestaurantCard key={r.place_id} restaurant={r} />
        ))}
      </div>
    </div>
  )
}
