'use client'

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import {
  translate,
  statusLabel,
  progressPhaseLabel,
  impactLevelLabel,
  type Locale,
} from '@/lib/i18n'
import { LOCALES, STORAGE_KEY } from '@/lib/i18n/types'

interface LanguageContextValue {
  locale: Locale
  setLocale: (locale: Locale) => void
  t: (path: string, vars?: Record<string, string | number>) => string
  statusLabel: (status: string) => string
  progressPhaseLabel: (phase: string) => string
  impactLevelLabel: (level: string) => string
}

const LanguageContext = createContext<LanguageContextValue | null>(null)

function readStoredLocale(): Locale {
  if (typeof window === 'undefined') return 'en'
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored && (LOCALES as readonly string[]).includes(stored)) {
    return stored as Locale
  }
  return 'en'
}

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>('en')

  useEffect(() => {
    setLocaleState(readStoredLocale())
  }, [])

  const setLocale = useCallback((next: Locale) => {
    setLocaleState(next)
    localStorage.setItem(STORAGE_KEY, next)
    document.documentElement.lang = next === 'en' ? 'en-IN' : next
  }, [])

  const t = useCallback(
    (path: string, vars?: Record<string, string | number>) => translate(locale, path, vars),
    [locale],
  )

  const value = useMemo<LanguageContextValue>(
    () => ({
      locale,
      setLocale,
      t,
      statusLabel: (status) => statusLabel(locale, status),
      progressPhaseLabel: (phase) => progressPhaseLabel(locale, phase),
      impactLevelLabel: (level) => impactLevelLabel(locale, level),
    }),
    [locale, setLocale, t],
  )

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
}

export function useLanguage() {
  const ctx = useContext(LanguageContext)
  if (!ctx) throw new Error('useLanguage must be used within LanguageProvider')
  return ctx
}
