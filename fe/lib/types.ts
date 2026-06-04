// ─────────────────────────────────────────────────────────────
// Core types dùng xuyên suốt FE
// ─────────────────────────────────────────────────────────────

export interface Location {
  lat: number
  lng: number
  address?: string
}

export interface UserContext {
  location?: Location
  budget?: number          // VND
  people?: number
  meal_time?: 'breakfast' | 'lunch' | 'dinner' | 'snack'
  purpose?: 'family' | 'date' | 'friends' | 'work' | 'solo'
  preferences?: string[]
  allergies?: string[]
}

export interface FoodSuggestion {
  name: string
  category: string
  description: string
  estimated_price: number
  reason: string
  tags: string[]
}

export interface Restaurant {
  place_id: string
  name: string
  address: string
  distance_km: number
  rating: number
  price_level: number        // 1–4
  is_open: boolean
  phone?: string
  maps_url: string
  photo_url?: string
  featured_dishes: string[]
  score: number
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  foods?: FoodSuggestion[]
  restaurants?: Restaurant[]
  follow_up_suggestions?: string[]
  status?: string             // trạng thái thinking
  ask_field?: string          // trường thông tin đang hỏi thêm (vd: 'location')
}

export interface ChatStore {
  messages: Message[]
  context: UserContext
  isLoading: boolean
  currentStatus: string
  results: {
    foods: FoodSuggestion[]
    restaurants: Restaurant[]
  }
  addMessage: (msg: Message) => void
  updateLastAssistantMessage: (patch: Partial<Message>) => void
  setContext: (ctx: Partial<UserContext>) => void
  setLoading: (v: boolean) => void
  setStatus: (s: string) => void
  setResults: (foods: FoodSuggestion[], restaurants: Restaurant[]) => void
  clearHistory: () => void
}
