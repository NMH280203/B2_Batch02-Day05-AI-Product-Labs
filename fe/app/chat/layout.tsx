import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'FoodAI Chat — Tư vấn ăn uống thông minh',
  description: 'Chat với AI để nhận gợi ý món ăn và quán ăn phù hợp ngữ cảnh của bạn',
}

export default function ChatLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
