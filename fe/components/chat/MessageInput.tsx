'use client'

import { KeyboardEvent, useRef, useState } from 'react'
import { useChat } from '@/hooks/useChat'
import { Spinner } from '@/components/ui/Spinner'

export function MessageInput() {
  const [text, setText] = useState('')
  const { sendMessage, isLoading } = useChat()
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSend = () => {
    if (!text.trim() || isLoading) return
    sendMessage(text)
    setText('')
    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleInput = () => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 120)}px` // max 4 dòng ~120px
  }

  return (
    <div className="border-t border-white/10 p-4">
      <div className="flex items-end gap-3 bg-white/5 border border-white/10 hover:border-orange-500/30 focus-within:border-orange-500/50 rounded-2xl px-4 py-3 transition-all duration-200">
        <textarea
          ref={textareaRef}
          id="message-input"
          rows={1}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onInput={handleInput}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          placeholder="Nhập ngữ cảnh của bạn... (vd: 'mệt mỏi, muốn ăn nhẹ, khoảng 80k')"
          className="flex-1 bg-transparent text-white text-sm placeholder-gray-600 resize-none focus:outline-none leading-relaxed disabled:opacity-50 scrollbar-none"
          style={{ maxHeight: '120px' }}
        />
        <button
          id="send-button"
          onClick={handleSend}
          disabled={isLoading || !text.trim()}
          className="shrink-0 w-9 h-9 flex items-center justify-center rounded-xl bg-gradient-to-br from-orange-500 to-rose-500 text-white hover:from-orange-600 hover:to-rose-600 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-orange-500/30 hover:scale-105 active:scale-95"
          aria-label="Gửi tin nhắn"
        >
          {isLoading ? (
            <Spinner size="sm" />
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
              <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
            </svg>
          )}
        </button>
      </div>
      <p className="text-[10px] text-gray-700 mt-2 text-center">
        Enter để gửi · Shift+Enter để xuống dòng
      </p>
    </div>
  )
}
