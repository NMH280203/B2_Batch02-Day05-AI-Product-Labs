'use client'

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { ChatStore, FoodSuggestion, Message, Restaurant, UserContext } from '@/lib/types'

export const useChatStore = create<ChatStore>()(
  persist(
    (set) => ({
      messages: [],
      context: {},
      isLoading: false,
      currentStatus: '',
      results: { foods: [], restaurants: [] },

      addMessage: (msg: Message) =>
        set((state) => ({ messages: [...state.messages, msg] })),

      updateLastAssistantMessage: (patch: Partial<Message>) =>
        set((state) => {
          const messages = [...state.messages]
          // Tìm assistant message cuối cùng
          for (let i = messages.length - 1; i >= 0; i--) {
            if (messages[i].role === 'assistant') {
              messages[i] = { ...messages[i], ...patch }
              // Nếu patch có content (text delta), append thay vì replace
              if (patch.content !== undefined && !patch.foods && !patch.restaurants && !patch.follow_up_suggestions) {
                messages[i].content = messages[i].content + ''
              }
              break
            }
          }
          return { messages }
        }),

      setContext: (ctx: Partial<UserContext>) =>
        set((state) => ({ context: { ...state.context, ...ctx } })),

      setLoading: (v: boolean) => set({ isLoading: v }),

      setStatus: (s: string) => set({ currentStatus: s }),

      setResults: (foods: FoodSuggestion[], restaurants: Restaurant[]) =>
        set({ results: { foods, restaurants } }),

      clearHistory: () =>
        set({ messages: [], results: { foods: [], restaurants: [] }, currentStatus: '' }),
    }),
    {
      name: 'food-chat-store',
      // Chỉ persist messages và context
      partialize: (state) => ({
        messages: state.messages,
        context: state.context,
      }),
    }
  )
)
