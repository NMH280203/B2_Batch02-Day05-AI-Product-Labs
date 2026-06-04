'use client'

import { useCallback } from 'react'
import { useChatStore } from '@/store/chatStore'
import { sendMessage as apiSendMessage } from '@/lib/api'
import { Message } from '@/lib/types'

function generateId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

export function useChat() {
  const {
    messages,
    context,
    isLoading,
    addMessage,
    updateLastAssistantMessage,
    setLoading,
    setStatus,
    setResults,
  } = useChatStore()

  const sendMessage = useCallback(
    async (text: string) => {
      if (isLoading || !text.trim()) return

      // 1. Tạo user message
      const userMsg: Message = {
        id: generateId(),
        role: 'user',
        content: text.trim(),
        timestamp: Date.now(),
      }
      addMessage(userMsg)

      // 2. Tạo assistant message rỗng (placeholder)
      const assistantMsg: Message = {
        id: generateId(),
        role: 'assistant',
        content: '',
        timestamp: Date.now(),
        status: 'Đang kết nối...',
      }
      addMessage(assistantMsg)
      setLoading(true)
      setStatus('Đang kết nối...')

      // 3. Gọi API
      const allMessages = [...messages, userMsg]

      try {
        await apiSendMessage(
          { messages: allMessages, context },
          {
            onThinking: (status) => {
              setStatus(status)
              updateLastAssistantMessage({ status, content: '' })
            },

            onFoodResults: (foods) => {
              const currentRestaurants = useChatStore.getState().results.restaurants
              setResults(foods, currentRestaurants)
              updateLastAssistantMessage({ foods })
            },

            onRestaurantResults: (restaurants) => {
              const currentFoods = useChatStore.getState().results.foods
              setResults(currentFoods, restaurants)
              updateLastAssistantMessage({ restaurants })
            },

            onTextDelta: (delta) => {
              // Append text delta
              const current = useChatStore.getState()
              const msgs = [...current.messages]
              for (let i = msgs.length - 1; i >= 0; i--) {
                if (msgs[i].role === 'assistant') {
                  msgs[i] = {
                    ...msgs[i],
                    content: msgs[i].content + delta,
                    status: undefined,
                  }
                  break
                }
              }
              useChatStore.setState({ messages: msgs })
            },

            onAskContext: (field, message) => {
              updateLastAssistantMessage({ content: message, status: undefined, ask_field: field })
            },

            onDone: (followUpSuggestions) => {
              updateLastAssistantMessage({
                follow_up_suggestions: followUpSuggestions,
                status: undefined,
              })
              setLoading(false)
              setStatus('')
            },

            onError: (errorMsg) => {
              updateLastAssistantMessage({
                content: `❌ ${errorMsg}`,
                status: undefined,
              })
              setLoading(false)
              setStatus('')
            },
          }
        )
      } catch (err) {
        updateLastAssistantMessage({
          content: `❌ Lỗi không xác định: ${err instanceof Error ? err.message : String(err)}`,
          status: undefined,
        })
        setLoading(false)
        setStatus('')
      }
    },
    [messages, context, isLoading, addMessage, updateLastAssistantMessage, setLoading, setStatus, setResults]
  )

  return { sendMessage, isLoading, messages, context }
}
