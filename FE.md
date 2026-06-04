Bạn là senior Frontend Engineer. Hãy implement toàn bộ Frontend cho dự án AI Chatbot gợi ý món ăn & nhà hàng theo đúng spec dưới đây. Không hỏi lại, implement trực tiếp.

---

## Tech stack
- Next.js 14 (App Router), TypeScript, Tailwind CSS
- Zustand (state management)
- Không có Auth, không có Database phía FE
- Toàn bộ state lưu trong localStorage

---

## Cấu trúc thư mục (tạo đúng theo cấu trúc này)

fe/
├── app/
│   ├── layout.tsx
│   ├── page.tsx                   # redirect → /chat
│   └── chat/
│       ├── page.tsx               # trang chat chính
│       └── layout.tsx
├── components/
│   ├── chat/
│   │   ├── ChatWindow.tsx
│   │   ├── MessageList.tsx
│   │   ├── MessageBubble.tsx
│   │   ├── MessageInput.tsx
│   │   └── TypingIndicator.tsx
│   ├── results/
│   │   ├── FoodCard.tsx
│   │   ├── FoodList.tsx
│   │   ├── RestaurantCard.tsx
│   │   ├── RestaurantList.tsx
│   │   └── ResultPanel.tsx
│   ├── map/
│   │   └── MapEmbed.tsx
│   └── ui/
│       ├── Button.tsx
│       ├── Spinner.tsx
│       └── Badge.tsx
├── hooks/
│   ├── useChat.ts
│   ├── useGeolocation.ts
│   └── useChatStore.ts
├── lib/
│   ├── api.ts
│   ├── storage.ts
│   └── types.ts
└── store/
    └── chatStore.ts

---

## Types (định nghĩa trong lib/types.ts, dùng xuyên suốt)

interface Location {
  lat: number
  lng: number
  address?: string
}

interface UserContext {
  location?: Location
  budget?: number          // VND
  people?: number
  meal_time?: "breakfast" | "lunch" | "dinner" | "snack"
  purpose?: "family" | "date" | "friends" | "work" | "solo"
  preferences?: string[]
  allergies?: string[]
}

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: number
  foods?: FoodSuggestion[]
  restaurants?: Restaurant[]
  follow_up_suggestions?: string[]
  status?: string             // trạng thái thinking
}

interface FoodSuggestion {
  name: string
  category: string
  description: string
  estimated_price: number
  reason: string
  tags: string[]
}

interface Restaurant {
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

interface ChatStore {
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

---

## Store (store/chatStore.ts)

- Dùng Zustand với persist middleware lưu vào localStorage
- Key localStorage: "food-chat-store"
- Persist: messages, context (không persist isLoading, currentStatus)

---

## localStorage helpers (lib/storage.ts)

Implement 3 hàm:
- saveChat(messages: Message[]): void
- loadChat(): Message[]
- saveContext(ctx: UserContext): void
- loadContext(): UserContext

---

## API layer (lib/api.ts)

### sendMessage
Gọi POST {NEXT_PUBLIC_API_URL}/api/chat
Body: { messages: Message[], context: UserContext }
Dùng fetch với ReadableStream để đọc SSE.

Parse từng dòng SSE theo format:
  event: thinking         → callback onThinking(status: string)
  event: food_results     → callback onFoodResults(foods: FoodSuggestion[])
  event: restaurant_results → callback onRestaurantResults(restaurants: Restaurant[])
  event: text             → callback onTextDelta(delta: string)
  event: ask_context      → callback onAskContext(field: string, message: string)
  event: done             → callback onDone(follow_up_suggestions: string[])
  event: error            → callback onError(message: string)

Signature:
  sendMessage(payload, callbacks): Promise<void>

### getRestaurants
Gọi GET {NEXT_PUBLIC_API_URL}/api/restaurants?lat=&lng=&query=&budget=&radius=&limit=
Trả về { restaurants: Restaurant[], total: number }

---

## Hooks

### useGeolocation (hooks/useGeolocation.ts)
- Gọi navigator.geolocation.getCurrentPosition
- Trả về { location: Location | null, error: string | null, loading: boolean, request: () => void }
- Khi có location, tự động gọi setContext({ location }) vào store

### useChat (hooks/useChat.ts)
- sendMessage(text: string): void
  1. Tạo Message user, addMessage vào store
  2. Tạo Message assistant rỗng, addMessage vào store
  3. Gọi api.sendMessage với toàn bộ messages + context
  4. Từng SSE event → cập nhật store tương ứng:
     - onThinking → setStatus(status)
     - onFoodResults → setResults(foods, [])
     - onRestaurantResults → setResults(foods, restaurants) (giữ foods cũ)
     - onTextDelta → updateLastAssistantMessage append content
     - onAskContext → addMessage assistant với content = message
     - onDone → updateLastAssistantMessage với follow_up_suggestions, setLoading(false)
     - onError → updateLastAssistantMessage với content = lỗi, setLoading(false)

---

## Components

### MessageBubble.tsx
- User bubble: căn phải, màu primary
- Assistant bubble: căn trái, màu surface
- Nếu message có foods → render FoodList bên dưới text
- Nếu message có restaurants → render RestaurantList bên dưới
- Nếu message có follow_up_suggestions → render các chip nhỏ có thể click, khi click gọi sendMessage(suggestion)
- Nếu message.status tồn tại → render TypingIndicator với text đó thay vì content

### MessageInput.tsx
- Textarea tự giãn (max 4 dòng)
- Enter gửi, Shift+Enter xuống dòng
- Disabled khi isLoading
- Có nút gửi icon

### ResultPanel.tsx
- Panel bên phải (desktop) hoặc bottom sheet (mobile)
- 3 tab: Món ăn / Quán ăn / Bản đồ
- Tabs chỉ hiện khi có data tương ứng
- MapEmbed nhận danh sách restaurants, hiển thị markers qua Google Maps Embed API

### RestaurantCard.tsx
- Hiển thị: tên, địa chỉ, distance_km, rating (sao), price_level ($), is_open badge, featured_dishes, nút "Xem bản đồ" → mở maps_url

### FoodCard.tsx
- Hiển thị: tên, category badge, description, estimated_price, reason, tags

---

## Layout tổng thể (app/chat/page.tsx)
- Desktop: flex row — ChatWindow (flex-1) + ResultPanel (w-96 fixed)
- Mobile: ChatWindow full screen, ResultPanel là bottom sheet kéo lên
- Header: tên app + nút xóa lịch sử + badge vị trí hiện tại
- Nếu chưa có location trong context → hiển thị banner "Cho phép truy cập vị trí để tìm quán gần bạn" + nút "Cho phép"

---

## Môi trường
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GOOGLE_MAPS_KEY=YOUR_KEY

---

## Yêu cầu chung
- Toàn bộ code TypeScript strict, không dùng any
- Xử lý đầy đủ loading state và error state
- Responsive mobile/desktop
- Khi BE chưa sẵn sàng, api.ts có thể mock SSE bằng cách export thêm hàm mockSendMessage() trả về fake events sau 500ms mỗi event để FE test độc lập