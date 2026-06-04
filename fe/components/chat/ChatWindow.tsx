'use client'

import { MessageList } from './MessageList'
import { MessageInput } from './MessageInput'

export function ChatWindow() {
  return (
    <div className="flex flex-col h-full">
      <MessageList />
      <MessageInput />
    </div>
  )
}
