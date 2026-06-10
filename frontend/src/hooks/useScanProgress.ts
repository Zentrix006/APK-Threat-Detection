'use client'

import { useCallback, useEffect, useState } from 'react'
import { api, type ScanProgress } from '@/lib/api'

export function useScanProgress(apkId: string | null, pollMs = 2500) {
  const [progress, setProgress] = useState<ScanProgress | null>(null)

  const refresh = useCallback(async () => {
    if (!apkId) return
    try {
      const res = await api.get<ScanProgress>(`/api/v1/investigation/${apkId}/progress`)
      setProgress(res.data)
    } catch {
      setProgress(null)
    }
  }, [apkId])

  useEffect(() => {
    if (!apkId) return
    refresh()
    if (progress?.phase === 'failed' || progress?.status === 'failed') return
    const t = setInterval(refresh, pollMs)
    return () => clearInterval(t)
  }, [apkId, pollMs, refresh, progress?.phase, progress?.status])

  const isFailed = progress?.status === 'failed' || progress?.phase === 'failed'
  const isRunning =
    !isFailed &&
    (progress?.status === 'analyzing' ||
      progress?.status === 'uploaded' ||
      (progress != null && progress.percent < 100 && progress.phase !== 'completed'))

  return { progress, refresh, isRunning, isFailed }
}
