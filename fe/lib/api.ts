import { FoodSuggestion, Message, Restaurant, UserContext } from './types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// ─────────────────────────────────────────────────────────────
// SSE Callbacks
// ─────────────────────────────────────────────────────────────

export interface SendMessageCallbacks {
  onThinking: (status: string) => void
  onFoodResults: (foods: FoodSuggestion[]) => void
  onRestaurantResults: (restaurants: Restaurant[]) => void
  onTextDelta: (delta: string) => void
  onAskContext: (field: string, message: string) => void
  onDone: (followUpSuggestions: string[]) => void
  onError: (message: string) => void
}

// ─────────────────────────────────────────────────────────────
// sendMessage — POST /api/chat với SSE stream
// ─────────────────────────────────────────────────────────────

export async function sendMessage(
  payload: { messages: Message[]; context: UserContext },
  callbacks: SendMessageCallbacks
): Promise<void> {
  const { onError } = callbacks

  try {
    const res = await fetch(`${API_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: payload.messages.map((m) => ({ role: m.role, content: m.content })),
        context: payload.context,
      }),
    })

    if (!res.ok) {
      onError(`Server lỗi: ${res.status} ${res.statusText}`)
      return
    }

    if (!res.body) {
      onError('Không nhận được response từ server.')
      return
    }

    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    const processEventBlock = (block: string) => {
      let currentEvent = ''
      const dataLines: string[] = []

      for (const line of block.split('\n')) {
        if (line.startsWith('event: ')) {
          currentEvent = line.slice(7).trim()
        } else if (line.startsWith('data: ')) {
          dataLines.push(line.slice(6))
        }
      }

      if (!currentEvent || dataLines.length === 0) return

      try {
        const parsed = JSON.parse(dataLines.join('\n'))
        dispatchEvent(currentEvent, parsed, callbacks)
      } catch {
        // Ignore malformed SSE payloads so one bad event does not break the stream.
      }
    }

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })

      const blocks = buffer.split(/\n\n/)
      buffer = blocks.pop() ?? ''
      blocks.forEach(processEventBlock)
    }

    const tail = buffer.trim()
    if (tail) processEventBlock(tail)
  } catch (err) {
    onError(err instanceof Error ? err.message : 'Lỗi kết nối không xác định')
  }
}

function dispatchEvent(
  event: string,
  data: Record<string, unknown>,
  cb: SendMessageCallbacks
): void {
  switch (event) {
    case 'thinking':
      cb.onThinking((data.status as string) || 'Đang xử lý...')
      break
    case 'food_results':
      cb.onFoodResults((data.foods as FoodSuggestion[]) || [])
      break
    case 'restaurant_results':
      cb.onRestaurantResults((data.restaurants as Restaurant[]) || [])
      break
    case 'text':
      cb.onTextDelta((data.delta as string) || '')
      break
    case 'ask_context':
      cb.onAskContext((data.field as string) || '', (data.message as string) || '')
      break
    case 'done':
      cb.onDone((data.follow_up_suggestions as string[]) || [])
      break
    case 'error':
      cb.onError((data.message as string) || 'Đã xảy ra lỗi.')
      break
  }
}

// ─────────────────────────────────────────────────────────────
// getRestaurants — GET /api/restaurants
// ─────────────────────────────────────────────────────────────

export async function getRestaurants(params: {
  lat: number
  lng: number
  query?: string
  budget?: number
  radius?: number
  limit?: number
}): Promise<{ restaurants: Restaurant[]; total: number }> {
  const qs = new URLSearchParams({
    lat: params.lat.toString(),
    lng: params.lng.toString(),
    query: params.query || 'quán ăn',
    radius: (params.radius || 2000).toString(),
    limit: (params.limit || 5).toString(),
  })
  if (params.budget) qs.set('budget', params.budget.toString())

  const res = await fetch(`${API_URL}/api/restaurants?${qs}`)
  if (!res.ok) throw new Error(`Server lỗi: ${res.status}`)
  return res.json()
}

// ─────────────────────────────────────────────────────────────
// mockSendMessage — fake SSE để test FE độc lập khi BE chưa sẵn
// ─────────────────────────────────────────────────────────────

export async function mockSendMessage(
  _payload: { messages: Message[]; context: UserContext },
  callbacks: SendMessageCallbacks
): Promise<void> {
  const delay = (ms: number) => new Promise((r) => setTimeout(r, ms))

  await delay(500)
  callbacks.onThinking('Đang phân tích yêu cầu của bạn...')

  await delay(800)
  callbacks.onThinking('Đang gợi ý món ăn phù hợp...')

  await delay(700)
  callbacks.onFoodResults([
    {
      name: 'Cơm tấm sườn nướng',
      category: 'Cơm',
      description: 'Cơm tấm với sườn nướng thơm ngon, ăn kèm bì và chả trứng',
      estimated_price: 55000,
      reason: 'Phù hợp bữa trưa nhanh, no lâu, giá hợp lý',
      tags: ['no bụng', 'phổ biến', 'nhanh'],
    },
    {
      name: 'Phở bò tái',
      category: 'Phở',
      description: 'Phở bò với nước dùng trong, thịt bò tái mềm',
      estimated_price: 65000,
      reason: 'Nhẹ bụng, phù hợp người không muốn ăn quá nặng',
      tags: ['nhẹ', 'nước dùng thơm', 'thanh đạm'],
    },
    {
      name: 'Bún bò Huế',
      category: 'Bún',
      description: 'Bún bò Huế đậm đà với chả cua và thịt bò',
      estimated_price: 60000,
      reason: 'Đậm vị, phù hợp buổi tối sau giờ làm',
      tags: ['đậm đà', 'cay nhẹ', 'đặc sản Huế'],
    },
  ])

  await delay(1000)
  callbacks.onThinking('Đang tìm quán ăn gần bạn...')

  await delay(800)
  callbacks.onRestaurantResults([
    {
      place_id: 'mock_001',
      name: 'Cơm Tấm Thuận Kiều',
      address: '123 Nguyễn Trãi, Q.1, TP.HCM',
      distance_km: 0.3,
      rating: 4.5,
      price_level: 2,
      is_open: true,
      maps_url: 'https://maps.google.com',
      featured_dishes: ['Cơm tấm sườn', 'Cơm tấm bì chả'],
      score: 0.92,
    },
    {
      place_id: 'mock_002',
      name: 'Phở Hà Nội Ngon',
      address: '45 Lê Lợi, Q.1, TP.HCM',
      distance_km: 0.7,
      rating: 4.2,
      price_level: 2,
      is_open: true,
      maps_url: 'https://maps.google.com',
      featured_dishes: ['Phở bò tái', 'Phở gà'],
      score: 0.85,
    },
  ])

  await delay(500)
  callbacks.onThinking('Đang soạn gợi ý cho bạn...')

  const fullText =
    'Dựa trên ngữ cảnh của bạn, mình gợi ý **Cơm tấm sườn nướng** 🍚 — vừa no lâu, giá cả phải chăng (55k), phù hợp bữa trưa nhanh sau giờ làm.\n\nGần bạn nhất là **Cơm Tấm Thuận Kiều** (cách 300m, rating 4.5⭐) — quán quen của nhiều dân văn phòng Q.1!'

  for (const char of fullText.split('')) {
    await delay(15)
    callbacks.onTextDelta(char)
  }

  await delay(300)
  callbacks.onDone([
    'Tôi muốn đổi sang món khác',
    'Quán nào có chỗ ngồi yên tĩnh?',
    'Gợi ý món ăn dưới 50k',
  ])
}
