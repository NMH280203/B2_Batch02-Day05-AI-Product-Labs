'use client'

import { useEffect, useRef } from 'react'
import { useChatStore } from '@/store/chatStore'
import { MessageBubble } from './MessageBubble'

export function MessageList() {
  const messages = useChatStore((s) => s.messages)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center px-6 text-center">
        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-orange-500 to-rose-500 flex items-center justify-center text-3xl mb-4 shadow-xl shadow-orange-500/30 animate-pulse">
          🍜
        </div>
        <h2 className="text-xl font-bold text-white mb-2">Xin chào! Hôm nay bạn muốn ăn gì? 😊</h2>
        <p className="text-gray-500 text-sm max-w-sm leading-relaxed">
          Hãy kể cho tôi nghe về tâm trạng, khẩu vị hay ngân sách của bạn — tôi sẽ gợi ý ngay!
        </p>
        <div className="mt-6 grid grid-cols-1 gap-2 w-full max-w-xs">
          {[
            'Hôm nay mệt, muốn ăn gì đó nhẹ, khoảng 80k',
            'Cuối tuần đi hẹn hò, cần quán đẹp, budget 300k',
            'Muốn ăn gì đó lạ, không phải đồ Việt thường ngày',
          ].map((s, i) => (
            <div key={i} className="text-xs text-gray-600 bg-white/5 border border-white/10 rounded-xl px-3 py-2">
              💬 &ldquo;{s}&rdquo;
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto px-4 py-4 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
      {messages.map((msg) => (
        <MessageBubble key={msg.id} msg={msg} />
      ))}
      <div ref={bottomRef} />
    </div>
  )
}
