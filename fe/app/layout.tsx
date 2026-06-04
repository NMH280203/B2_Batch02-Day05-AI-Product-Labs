import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin', 'vietnamese'] })

export const metadata: Metadata = {
  title: 'FoodAI — Gợi ý món ăn & quán ăn thông minh',
  description: 'AI gợi ý món ăn và quán ăn phù hợp với ngữ cảnh, tâm trạng và ngân sách của bạn. Powered by Gemma 4.',
  keywords: ['gợi ý món ăn', 'tìm quán ăn', 'AI', 'food recommendation', 'ẩm thực Việt Nam'],
  openGraph: {
    title: 'FoodAI — Gợi ý món ăn thông minh',
    description: 'Không biết hôm nay ăn gì? Để AI giúp bạn!',
    locale: 'vi_VN',
    type: 'website',
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi">
      <body className={`${inter.className} bg-[#0a0b0f] text-white antialiased`}>
        {children}
      </body>
    </html>
  )
}
