'use client'

import { useCallback, useState } from 'react'
import { useChatStore } from '@/store/chatStore'
import { Location } from '@/lib/types'

export function useGeolocation() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [location, setLocation] = useState<Location | null>(null)
  const setContext = useChatStore((s) => s.setContext)

  const request = useCallback(() => {
    if (!navigator.geolocation) {
      setError('Trình duyệt của bạn không hỗ trợ định vị.')
      return
    }

    setLoading(true)
    setError(null)

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const loc: Location = {
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
        }
        setLocation(loc)
        setContext({ location: loc })
        setLoading(false)
      },
      (err) => {
        setError(
          err.code === 1
            ? 'Bạn đã từ chối quyền truy cập vị trí.'
            : 'Không thể lấy vị trí của bạn. Vui lòng thử lại.'
        )
        setLoading(false)
      },
      { enableHighAccuracy: true, timeout: 10000 }
    )
  }, [setContext])

  return { location, error, loading, request }
}
