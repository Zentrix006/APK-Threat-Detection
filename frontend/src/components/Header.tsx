'use client'

import { useCallback, useEffect, useState } from 'react'
import { Activity } from 'lucide-react'
import { api } from '@/lib/api'
import { useLanguage } from '@/contexts/LanguageContext'
import LanguageSwitcher from '@/components/LanguageSwitcher'

export default function Header() {
  const { t } = useLanguage()
  const [online, setOnline] = useState<boolean | null>(null)

  const checkHealth = useCallback(async () => {
    try {
      await api.get('/api/v1/config', { timeout: 8000 })
      setOnline(true)
    } catch {
      try {
        await api.get('/health', { timeout: 5000 })
        setOnline(true)
      } catch {
        setOnline(false)
      }
    }
  }, [])

  useEffect(() => {
    checkHealth()
    const timer = setInterval(checkHealth, 30000)
    return () => clearInterval(timer)
  }, [checkHealth])

  return (
    <header className="shrink-0 bg-white/80 backdrop-blur-md border-b border-slate-200/80 px-6 py-4 shadow-sm">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">{t('header.title')}</h1>
          <p className="text-sm text-slate-500 mt-0.5">{t('header.subtitle')}</p>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          <LanguageSwitcher />

          <button
            type="button"
            onClick={checkHealth}
            className="flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-sm hover:bg-slate-100"
          >
            <Activity
              size={16}
              className={
                online === true
                  ? 'text-emerald-500'
                  : online === false
                    ? 'text-red-500'
                    : 'text-slate-400'
              }
            />
            <span className="text-slate-600">
              {t('common.backend')}:{' '}
              <span
                className={`font-semibold ${
                  online === true
                    ? 'text-emerald-700'
                    : online === false
                      ? 'text-red-700'
                      : 'text-slate-500'
                }`}
              >
                {online === null
                  ? t('common.checking')
                  : online
                    ? t('common.online')
                    : t('common.offline')}
              </span>
            </span>
          </button>
        </div>
      </div>
    </header>
  )
}
