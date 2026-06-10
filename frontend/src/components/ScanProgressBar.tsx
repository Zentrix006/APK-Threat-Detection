'use client'

import { AlertTriangle, Clock, Loader2 } from 'lucide-react'
import type { ScanProgress } from '@/lib/api'
import { useLanguage } from '@/contexts/LanguageContext'

export default function ScanProgressBar({ progress }: { progress: ScanProgress }) {
  const { t, progressPhaseLabel } = useLanguage()
  const failed = progress.phase === 'failed' || progress.status === 'failed'
  const label = progressPhaseLabel(progress.phase)
  const pct = Math.min(100, Math.max(0, progress.percent))
  const detail = progress.error || progress.message

  const formatEta = (seconds: number): string => {
    if (seconds <= 0) return t('progress.almostDone')
    if (seconds < 60) return t('progress.secondsLeft', { seconds })
    const m = Math.ceil(seconds / 60)
    return t('progress.minutesLeft', { minutes: m })
  }

  if (failed) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50/90 p-4 space-y-2">
        <div className="flex items-center gap-2 text-red-900">
          <AlertTriangle className="shrink-0" size={18} />
          <span className="text-sm font-semibold">{label}</span>
        </div>
        <p className="text-sm text-red-800 font-mono break-words">{detail}</p>
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-blue-200 bg-blue-50/80 p-4 space-y-3">
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 text-blue-900">
          <Loader2 className="animate-spin shrink-0" size={18} />
          <span className="text-sm font-semibold">{label}</span>
        </div>
        <span className="text-sm font-bold text-blue-700 tabular-nums">{pct}%</span>
      </div>

      <div className="h-2.5 w-full rounded-full bg-blue-100 overflow-hidden">
        <div
          className="h-full rounded-full bg-blue-600 transition-all duration-500 ease-out"
          style={{ width: `${pct}%` }}
        />
      </div>

      <p className="text-sm text-blue-800">{progress.message}</p>

      <div className="flex items-center gap-1.5 text-xs text-blue-600">
        <Clock size={14} />
        <span>{formatEta(progress.eta_seconds)}</span>
      </div>
    </div>
  )
}
