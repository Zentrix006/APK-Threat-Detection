'use client'

import { AlertCircle, CheckCircle, Info, Loader2 } from 'lucide-react'

type AlertVariant = 'error' | 'success' | 'info' | 'loading'

interface StatusAlertProps {
  variant: AlertVariant
  title?: string
  message: string
  onRetry?: () => void
  retryLabel?: string
}

const styles: Record<AlertVariant, { box: string; icon: string; text: string }> = {
  error: {
    box: 'bg-red-50 border-red-200',
    icon: 'text-red-600',
    text: 'text-red-900',
  },
  success: {
    box: 'bg-emerald-50 border-emerald-200',
    icon: 'text-emerald-600',
    text: 'text-emerald-900',
  },
  info: {
    box: 'bg-blue-50 border-blue-200',
    icon: 'text-blue-600',
    text: 'text-blue-900',
  },
  loading: {
    box: 'bg-amber-50 border-amber-200',
    icon: 'text-amber-600',
    text: 'text-amber-900',
  },
}

export default function StatusAlert({
  variant,
  title,
  message,
  onRetry,
  retryLabel = 'Try again',
}: StatusAlertProps) {
  const s = styles[variant]
  const Icon =
    variant === 'success' ? CheckCircle : variant === 'loading' ? Loader2 : variant === 'info' ? Info : AlertCircle

  return (
    <div className={`border rounded-xl p-4 flex items-start gap-3 shadow-sm ${s.box}`}>
      <Icon
        className={`${s.icon} shrink-0 mt-0.5 ${variant === 'loading' ? 'animate-spin' : ''}`}
        size={22}
        aria-hidden
      />
      <div className="flex-1 min-w-0">
        {title && <p className={`font-semibold ${s.text}`}>{title}</p>}
        <p className={`text-sm ${s.text} ${title ? 'mt-1 opacity-90' : ''}`}>{message}</p>
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            className="mt-3 text-sm font-semibold text-blue-700 hover:text-blue-800 underline-offset-2 hover:underline"
          >
            {retryLabel}
          </button>
        )}
      </div>
    </div>
  )
}

export function statusBadgeClass(status: string): string {
  switch (status) {
    case 'analyzed':
      return 'bg-emerald-100 text-emerald-800 ring-emerald-600/20'
    case 'analyzing':
    case 'uploaded':
      return 'bg-amber-100 text-amber-900 ring-amber-600/20'
    case 'failed':
      return 'bg-red-100 text-red-800 ring-red-600/20'
    default:
      return 'bg-slate-100 text-slate-700 ring-slate-500/20'
  }
}
