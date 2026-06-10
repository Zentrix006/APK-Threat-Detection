import type { Metadata } from 'next'
import { Inter, Noto_Sans_Devanagari, Noto_Sans_Kannada, Noto_Sans_Telugu } from 'next/font/google'
import Providers from '@/components/Providers'
import './globals.css'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

const notoDevanagari = Noto_Sans_Devanagari({
  subsets: ['devanagari'],
  display: 'swap',
  variable: '--font-devanagari',
})

const notoKannada = Noto_Sans_Kannada({
  subsets: ['kannada'],
  display: 'swap',
  variable: '--font-kannada',
})

const notoTelugu = Noto_Sans_Telugu({
  subsets: ['telugu'],
  display: 'swap',
  variable: '--font-telugu',
})

export const metadata: Metadata = {
  title: 'APK Threat Intelligence',
  description: 'Mobile APK security analysis and threat detection',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html
      lang="en-IN"
      className={`${inter.variable} ${notoDevanagari.variable} ${notoKannada.variable} ${notoTelugu.variable}`}
    >
      <body
        className="min-h-screen font-sans antialiased"
        style={{
          fontFamily:
            'var(--font-inter), var(--font-devanagari), var(--font-kannada), var(--font-telugu), system-ui, sans-serif',
        }}
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
