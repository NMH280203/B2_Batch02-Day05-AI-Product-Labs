import { Message, UserContext } from './types'

const MESSAGES_KEY = 'food-chat-messages'
const CONTEXT_KEY = 'food-chat-context'

export function saveChat(messages: Message[]): void {
  try {
    localStorage.setItem(MESSAGES_KEY, JSON.stringify(messages))
  } catch {
    // ignore quota errors
  }
}

export function loadChat(): Message[] {
  try {
    const raw = localStorage.getItem(MESSAGES_KEY)
    return raw ? (JSON.parse(raw) as Message[]) : []
  } catch {
    return []
  }
}

export function saveContext(ctx: UserContext): void {
  try {
    localStorage.setItem(CONTEXT_KEY, JSON.stringify(ctx))
  } catch {
    // ignore
  }
}

export function loadContext(): UserContext {
  try {
    const raw = localStorage.getItem(CONTEXT_KEY)
    return raw ? (JSON.parse(raw) as UserContext) : {}
  } catch {
    return {}
  }
}
