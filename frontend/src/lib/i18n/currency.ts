import type { Locale } from './types'
import { LOCALE_BCP47 } from './types'

const USD_TO_INR = 83

/** Format amount as Indian Rupees (₹). Converts legacy USD payloads when needed. */
export function formatINR(
  amount: number,
  locale: Locale,
  currency?: string,
): string {
  const inr = currency === 'USD' ? Math.round(amount * USD_TO_INR) : amount

  return new Intl.NumberFormat(LOCALE_BCP47[locale], {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(inr)
}

export function formatINRRange(
  low: number,
  high: number,
  locale: Locale,
  currency?: string,
): string {
  return `${formatINR(low, locale, currency)} – ${formatINR(high, locale, currency)}`
}

export function normalizeToInr(amount: number, currency?: string): number {
  if (currency === 'USD') return Math.round(amount * USD_TO_INR)
  return amount
}
