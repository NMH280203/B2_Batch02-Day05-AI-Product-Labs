'use client'

import { useState } from 'react'
import { Message } from '@/lib/types'
import { FoodList } from '@/components/results/FoodList'
import { RestaurantList } from '@/components/results/RestaurantList'
import { TypingIndicator } from './TypingIndicator'
import { useChat } from '@/hooks/useChat'
import { useChatStore } from '@/store/chatStore'

function formatTime(timestamp: number) {
  return new Date(timestamp).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })
}

function MessageBubble({ msg }: { msg: Message }) {
  const { sendMessage } = useChat()
  const isUser = msg.role === 'user'
  const [geoLoading, setGeoLoading] = useState(false)
  const [geoError, setGeoError] = useState<string | null>(null)

  const handleShareLocation = () => {
    if (!navigator.geolocation) {
      setGeoError('Trình duyệt của bạn không hỗ trợ định vị.')
      return
    }

    setGeoLoading(true)
    setGeoError(null)

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const loc = {
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
        }
        useChatStore.getState().setContext({ location: loc })
        setGeoLoading(false)

        const msgs = useChatStore.getState().messages
        const lastUserQuery = [...msgs].reverse().find((m) => m.role === 'user')?.content
        if (lastUserQuery) {
          sendMessage(lastUserQuery)
        } else {
          sendMessage("Đã chia sẻ vị trí của tôi")
        }
      },
      (err) => {
        setGeoError(
          err.code === 1
            ? 'Bạn đã từ chối quyền truy cập vị trí.'
            : 'Không thể lấy vị trí. Vui lòng thử lại.'
        )
        setGeoLoading(false)
      },
      { enableHighAccuracy: true, timeout: 10000 }
    )
  }

  if (isUser) {
    return (
      <div className="flex justify-end mb-4">
        <div className="max-w-[80%]">
          <div className="bg-gradient-to-br from-orange-500 to-rose-500 text-white rounded-2xl rounded-tr-sm px-4 py-3 shadow-lg shadow-orange-500/20">
            <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
          </div>
          <p className="text-[10px] text-gray-600 mt-1 text-right">{formatTime(msg.timestamp)}</p>
        </div>
      </div>
    )
  }

  // Assistant message
  return (
    <div className="flex justify-start mb-4 gap-3">
      {/* Avatar */}
      <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shrink-0 text-sm mt-1 shadow-lg shadow-purple-500/20">
        🤖
      </div>

      <div className="flex-1 max-w-[85%]">
        <div className="bg-white/5 border border-white/10 rounded-2xl rounded-tl-sm px-4 py-3">
          {/* Thinking status */}
          {msg.status ? (
            <TypingIndicator text={msg.status} />
          ) : (
            <>
              {/* Text content */}
              {msg.content && (
                <p className="text-sm text-gray-200 leading-relaxed whitespace-pre-wrap">
                  {msg.content}
                </p>
              )}

              {/* Ask context button for location */}
              {msg.ask_field === 'location' && (
                <div className="mt-3 flex flex-col items-start gap-1.5">
                  <button
                    onClick={handleShareLocation}
                    disabled={geoLoading}
                    className="flex items-center gap-2 text-xs px-4 py-2.5 bg-gradient-to-r from-orange-500 to-rose-500 hover:from-orange-600 hover:to-rose-600 text-white rounded-xl font-semibold shadow-md shadow-orange-500/20 hover:shadow-lg transition-all duration-200 active:scale-95 disabled:opacity-50"
                  >
                    {geoLoading ? (
                      <>
                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Đang lấy vị trí...
                      </>
                    ) : (
                      <>📍 Chia sẻ vị trí của tôi</>
                    )}
                  </button>
                  {geoError && (
                    <p className="text-[10px] text-rose-400 mt-1">{geoError}</p>
                  )}
                </div>
              )}

              {/* Food results */}
              {msg.foods && msg.foods.length > 0 && <FoodList foods={msg.foods} />}

              {/* Restaurant results */}
              {msg.restaurants && msg.restaurants.length > 0 && (
                <RestaurantList restaurants={msg.restaurants} />
              )}

              {/* Follow-up suggestions */}
              {msg.follow_up_suggestions && msg.follow_up_suggestions.length > 0 && (
                <div className="mt-4 pt-3 border-t border-white/10">
                  <p className="text-[10px] text-gray-600 mb-2 uppercase tracking-wider">Gợi ý tiếp theo</p>
                  <div className="flex flex-wrap gap-2">
                    {msg.follow_up_suggestions.map((s, i) => (
                      <button
                        key={i}
                        id={`followup-${i}`}
                        onClick={() => sendMessage(s)}
                        className="text-xs px-3 py-1.5 bg-white/5 hover:bg-orange-500/20 text-gray-400 hover:text-orange-300 border border-white/10 hover:border-orange-500/30 rounded-full transition-all duration-200"
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
        <p className="text-[10px] text-gray-600 mt-1">{formatTime(msg.timestamp)}</p>
      </div>
    </div>
  )
}

export { MessageBubble }
