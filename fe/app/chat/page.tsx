'use client'

import { useGeolocation } from '@/hooks/useGeolocation'
import { useChatStore } from '@/store/chatStore'
import { ChatWindow } from '@/components/chat/ChatWindow'
import { ResultPanel } from '@/components/results/ResultPanel'
import { Button } from '@/components/ui/Button'
import { Spinner } from '@/components/ui/Spinner'

export default function ChatPage() {
  const clearHistory = useChatStore((s) => s.clearHistory)
  const context = useChatStore((s) => s.context)
  const results = useChatStore((s) => s.results)
  const { request: requestLocation, loading: geoLoading } = useGeolocation()

  const hasResults = results.foods.length > 0 || results.restaurants.length > 0
  const hasLocation = !!context.location

  return (
    <div className="flex flex-col h-screen bg-[#0a0b0f]">
      {/* ── Header ── */}
      <header className="flex items-center justify-between px-4 py-3 border-b border-white/10 bg-[#0a0b0f]/80 backdrop-blur-xl shrink-0 z-10">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-orange-500 to-rose-500 flex items-center justify-center text-lg shadow-lg shadow-orange-500/30">
            🍜
          </div>
          <div>
            <h1 className="text-base font-bold text-white">FoodAI</h1>
            <p className="text-[10px] text-gray-500">Powered by Gemma 4 31B</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Location badge */}
          {hasLocation ? (
            <span className="hidden sm:flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1.5 rounded-full">
              📍 Đã xác định vị trí
            </span>
          ) : null}

          {/* Clear history */}
          <Button
            id="clear-history-btn"
            variant="ghost"
            size="sm"
            onClick={clearHistory}
            title="Xóa lịch sử chat"
          >
            🗑️ <span className="hidden sm:inline">Xóa</span>
          </Button>
        </div>
      </header>

      {/* ── Location banner (nếu chưa có vị trí) ── */}
      {!hasLocation && (
        <div className="mx-4 mt-3 bg-sky-500/10 border border-sky-500/20 rounded-2xl px-4 py-3 flex items-center justify-between gap-3 shrink-0">
          <div className="flex items-center gap-2">
            <span className="text-sky-400">📍</span>
            <p className="text-sm text-sky-300">
              Cho phép truy cập vị trí để tìm quán ăn gần bạn
            </p>
          </div>
          <Button
            id="allow-location-btn"
            variant="secondary"
            size="sm"
            onClick={requestLocation}
            disabled={geoLoading}
          >
            {geoLoading ? <Spinner size="sm" /> : 'Cho phép'}
          </Button>
        </div>
      )}

      {/* ── Main content ── */}
      <div className="flex flex-1 overflow-hidden">
        {/* Chat window — full trên mobile, flex-1 trên desktop */}
        <div className={`flex flex-col ${hasResults ? 'flex-1' : 'w-full'} min-w-0 overflow-hidden`}>
          <ChatWindow />
        </div>

        {/* Result panel — desktop only (w-96) */}
        {hasResults && (
          <div className="hidden md:flex w-96 shrink-0">
            <ResultPanel />
          </div>
        )}
      </div>

      {/* ── Mobile bottom sheet cho results ── */}
      {hasResults && (
        <div className="md:hidden border-t border-white/10 max-h-[40vh] overflow-hidden flex flex-col bg-[#0f1117]">
          <ResultPanel />
        </div>
      )}
    </div>
  )
}
