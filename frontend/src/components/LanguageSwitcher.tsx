'use client'

import { Languages } from 'lucide-react'
import { useLanguage } from '@/contexts/LanguageContext'
import { LOCALE_LABELS, type Locale } from '@/lib/i18n/types'

const ORDER: Locale[] = ['en', 'hi', 'kn', 'te']

export default function LanguageSwitcher() {
  const { locale, setLocale, t } = useLanguage()

  return (
    <div className="flex items-center gap-2">
      <Languages size={16} className="text-slate-500 shrink-0" aria-hidden />
      <label htmlFor="app-locale" className="sr-only">
        {t('header.language')}
      </label>
      <select
        id="app-locale"
        value={locale}
        onChange={(e) => setLocale(e.target.value as Locale)}
        className="rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-sm font-medium text-slate-700 shadow-sm hover:border-indigo-300 focus:outline-none focus:ring-2 focus:ring-indigo-400/50 cursor-pointer"
      >
        {ORDER.map((code) => (
          <option key={code} value={code}>
            {LOCALE_LABELS[code]}
          </option>
        ))}
      </select>
    </div>
  )
}
