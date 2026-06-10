export const LOCALES = ['en', 'hi', 'kn', 'te'] as const
export type Locale = (typeof LOCALES)[number]

export const LOCALE_LABELS: Record<Locale, string> = {
  en: 'English',
  hi: 'हिंदी',
  kn: 'ಕನ್ನಡ',
  te: 'తెలుగు',
}

export const LOCALE_BCP47: Record<Locale, string> = {
  en: 'en-IN',
  hi: 'hi-IN',
  kn: 'kn-IN',
  te: 'te-IN',
}

export const STORAGE_KEY = 'apk-threat-locale'
