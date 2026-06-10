import type { Locale } from './types'
import en from './locales/en'
import hi from './locales/hi'
import kn from './locales/kn'
import te from './locales/te'
import type { Messages } from './locales/en'

export type { Locale, Messages }
export { LOCALES, LOCALE_LABELS, STORAGE_KEY } from './types'
export { formatINR, formatINRRange, normalizeToInr } from './currency'

const catalogs: Record<Locale, Messages> = { en, hi, kn, te }

type PathVars = Record<string, string | number>

function getNested(obj: unknown, path: string): string | undefined {
  const keys = path.split('.')
  let cur: unknown = obj
  for (const k of keys) {
    if (cur == null || typeof cur !== 'object') return undefined
    cur = (cur as Record<string, unknown>)[k]
  }
  return typeof cur === 'string' ? cur : undefined
}

export function translate(
  locale: Locale,
  path: string,
  vars?: PathVars,
): string {
  const raw = getNested(catalogs[locale], path) ?? getNested(catalogs.en, path) ?? path
  if (!vars) return raw
  return raw.replace(/\{(\w+)\}/g, (_, key: string) => String(vars[key] ?? `{${key}}`))
}

export function statusLabel(locale: Locale, status: string): string {
  const key = `status.${status}` as const
  const v = getNested(catalogs[locale], key)
  return v ?? status
}

export function progressPhaseLabel(locale: Locale, phase: string): string {
  const v = getNested(catalogs[locale], `progress.${phase}`)
  return v ?? phase.replace(/_/g, ' ')
}

export function impactLevelLabel(locale: Locale, level: string): string {
  const v = getNested(catalogs[locale], `analysis.impactLevel.${level}`)
  return v ?? level
}
