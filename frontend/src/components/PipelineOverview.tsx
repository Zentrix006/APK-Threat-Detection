'use client'

import { useState } from 'react'
import { ChevronDown, ChevronRight, Sparkles } from 'lucide-react'
import { INVESTIGATION_PIPELINE } from '@/lib/pipeline'
import { useLanguage } from '@/contexts/LanguageContext'

export default function PipelineOverview({ onStartUpload }: { onStartUpload?: () => void }) {
  const { t } = useLanguage()
  const [openId, setOpenId] = useState<string | null>(INVESTIGATION_PIPELINE[0]?.id ?? null)

  return (
    <div className="max-w-3xl space-y-8">
      <div className="hero-gradient rounded-2xl p-6 md:p-8 text-white shadow-lg">
        <div className="flex items-center gap-2 text-cyan-200 text-sm font-medium mb-2">
          <Sparkles size={16} />
          {t('pipeline.badge')}
        </div>
        <h2 className="text-2xl md:text-3xl font-bold tracking-tight">{t('pipeline.pageTitle')}</h2>
        <p className="text-slate-200/90 mt-3 leading-relaxed max-w-2xl">{t('pipeline.pageSubtitle')}</p>
      </div>

      <div className="space-y-3">
        {INVESTIGATION_PIPELINE.map((step, index) => {
          const isOpen = openId === step.id
          const Icon = step.icon
          const title = t(`pipeline.steps.${step.id}.title`)
          const summary = t(`pipeline.steps.${step.id}.summary`)

          return (
            <div
              key={step.id}
              className={`card-soc overflow-hidden transition-shadow ${
                isOpen ? 'ring-2 ring-indigo-200 shadow-md' : ''
              }`}
            >
              <button
                type="button"
                onClick={() => setOpenId(isOpen ? null : step.id)}
                className="w-full flex items-center gap-4 p-5 text-left hover:bg-slate-50/80 transition-colors"
              >
                <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-cyan-500 text-white font-bold shadow-md">
                  {index + 1}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <Icon size={18} className="text-indigo-600 shrink-0" />
                    <h3 className="font-semibold text-slate-900">{title}</h3>
                  </div>
                  <p className="text-sm text-slate-600 mt-1 line-clamp-2">{summary}</p>
                </div>
                {isOpen ? (
                  <ChevronDown className="text-slate-400 shrink-0" size={20} />
                ) : (
                  <ChevronRight className="text-slate-400 shrink-0" size={20} />
                )}
              </button>

              {isOpen && (
                <div className="px-5 pb-5 pt-0 border-t border-slate-100 bg-gradient-to-b from-indigo-50/40 to-white">
                  <div className="grid sm:grid-cols-2 gap-5 pt-4">
                    <div>
                      <p className="text-[10px] font-bold uppercase tracking-wider text-indigo-600 mb-2">
                        {t('pipeline.details')}
                      </p>
                      <ul className="text-sm text-slate-700 space-y-2 list-disc pl-4">
                        {step.details.map((d) => (
                          <li key={d}>{d}</li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <p className="text-[10px] font-bold uppercase tracking-wider text-emerald-700 mb-2">
                        {t('pipeline.produces')}
                      </p>
                      <ul className="text-sm space-y-2">
                        {step.outputs.map((o) => (
                          <li
                            key={o}
                            className="flex items-center gap-2 text-slate-700 bg-white rounded-lg border border-slate-100 px-3 py-2"
                          >
                            <span className="h-2 w-2 rounded-full bg-emerald-500 shrink-0" />
                            {o}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>

      <div className="rounded-2xl bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white p-6 md:p-8 shadow-xl border border-slate-700/50">
        <h3 className="font-semibold text-lg">{t('pipeline.differentiators')}</h3>
        <ul className="mt-3 text-sm text-slate-300 space-y-2">
          <li className="flex gap-2">
            <span className="text-cyan-400">▸</span> Threat relationship graph — APK, domains, certs, families
          </li>
          <li className="flex gap-2">
            <span className="text-cyan-400">▸</span> AI reverse-engineering assistant
          </li>
          <li className="flex gap-2">
            <span className="text-cyan-400">▸</span> Malware story mode & digital twin (₹ fraud impact)
          </li>
        </ul>
        {onStartUpload && (
          <button
            type="button"
            onClick={onStartUpload}
            className="mt-6 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-500 px-5 py-2.5 text-sm font-semibold hover:opacity-95 shadow-lg shadow-cyan-900/30 transition-opacity"
          >
            {t('pipeline.start')}
          </button>
        )}
      </div>
    </div>
  )
}
