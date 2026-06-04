import { FoodSuggestion } from '@/lib/types'
import { FoodCard } from './FoodCard'

export function FoodList({ foods }: { foods: FoodSuggestion[] }) {
  if (!foods?.length) return null
  return (
    <div className="mt-3 space-y-2">
      <p className="text-xs text-gray-500 font-medium uppercase tracking-wider mb-2">🍽️ Món gợi ý</p>
      <div className="grid gap-2">
        {foods.map((food, i) => (
          <FoodCard key={`${food.name}-${i}`} food={food} />
        ))}
      </div>
    </div>
  )
}
