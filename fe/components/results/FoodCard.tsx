import { FoodSuggestion } from '@/lib/types'
import { Badge } from '@/components/ui/Badge'

export function FoodCard({ food }: { food: FoodSuggestion }) {
  return (
    <div className="group relative bg-white/5 hover:bg-white/10 border border-white/10 hover:border-orange-500/40 rounded-2xl p-4 transition-all duration-300 hover:shadow-lg hover:shadow-orange-500/10">
      {/* Header */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <div>
          <h3 className="font-semibold text-white text-sm group-hover:text-orange-300 transition-colors">
            {food.name}
          </h3>
          <Badge variant="info" className="mt-1">{food.category}</Badge>
        </div>
        <div className="text-right shrink-0">
          <span className="text-orange-400 font-bold text-sm">
            ~{food.estimated_price.toLocaleString('vi-VN')}đ
          </span>
        </div>
      </div>

      {/* Description */}
      <p className="text-gray-400 text-xs leading-relaxed mb-3">{food.description}</p>

      {/* Reason */}
      <div className="bg-orange-500/10 border border-orange-500/20 rounded-xl px-3 py-2 mb-3">
        <p className="text-orange-300 text-xs">💡 {food.reason}</p>
      </div>

      {/* Tags */}
      {food.tags?.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {food.tags.map((tag) => (
            <Badge key={tag} variant="default" className="text-[10px]">
              #{tag}
            </Badge>
          ))}
        </div>
      )}
    </div>
  )
}
