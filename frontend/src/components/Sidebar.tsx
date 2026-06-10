'use client'

import { useState } from 'react'
import {
  BarChart3,
  ChevronRight,
  Shield,
  Upload,
  Workflow,
  X,
} from 'lucide-react'
import { INVESTIGATION_PIPELINE } from '@/lib/pipeline'
import { useLanguage } from '@/contexts/LanguageContext'

export type View = 'dashboard' | 'upload' | 'analysis' | 'pipeline'

interface SidebarProps {
  currentView: View
  onNavigate: (view: View) => void
}

const operations = [
  { view: 'dashboard' as const, labelKey: 'nav.dashboard', icon: BarChart3 },
  { view: 'upload' as const, labelKey: 'nav.upload', icon: Upload },
  { view: 'pipeline' as const, labelKey: 'nav.pipeline', icon: Workflow },
]

const capabilityIds = [
  'static',
  'dynamic',
  'ai',
  'mitre',
  'intel',
  'story',
  'twin',
  'fraud',
] as const

export default function Sidebar({
  currentView,
  onNavigate,
}: SidebarProps) {
  const { t } = useLanguage()
  const [capabilityId, setCapabilityId] = useState<string | null>(null)

  const selectedStep = INVESTIGATION_PIPELINE.find(
    (s) => s.id === capabilityId
  )

  return (
    <aside className="w-80 shrink-0 flex flex-col border-r border-slate-800/80 overflow-hidden bg-gradient-to-b from-slate-950 via-slate-900 to-indigo-950 text-white">
      {/* Header */}
      <div className="p-5 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-400 to-indigo-500 shadow-lg shadow-indigo-900/50">
            <Shield size={22} className="text-white" aria-hidden />
          </div>

          <div>
            <p className="font-bold text-sm tracking-tight">
              {t('nav.brand')}
            </p>
            <p className="text-xs text-cyan-200/70">
              {t('nav.tagline')}
            </p>
          </div>
        </div>
      </div>

      {/* Operations */}
      <div className="p-3">
        <p className="px-3 mb-2 text-[10px] font-bold uppercase tracking-wider text-slate-500">
          {t('nav.operations')}
        </p>

        <nav className="space-y-1">
          {operations.map(({ view, labelKey, icon: Icon }) => {
            const active =
              currentView === view ||
              (view === 'dashboard' && currentView === 'analysis')

            return (
              <button
                key={view}
                type="button"
                onClick={() => onNavigate(view)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${active
                    ? 'bg-gradient-to-r from-indigo-500 to-cyan-600 text-white shadow-md shadow-indigo-900/40'
                    : 'text-slate-300 hover:bg-white/10 hover:text-white'
                  }`}
              >
                <Icon size={18} aria-hidden />
                {t(labelKey)}
              </button>
            )
          })}
        </nav>
      </div>

      {/* Scrollable Capabilities Area */}
      <div className="flex-1 overflow-y-auto px-3 pb-3">
        <p className="px-3 mb-2 text-[10px] font-bold uppercase tracking-wider text-slate-500">
          {t('nav.capabilities')}
        </p>

        <ul className="space-y-1 px-1">
          {capabilityIds.map((id) => {
            const step = INVESTIGATION_PIPELINE.find((s) => s.id === id)

            if (!step) return null

            const Icon = step.icon
            const isOpen = capabilityId === id

            const title = t(`pipeline.steps.${id}.title`)
            const summary = t(`pipeline.steps.${id}.summary`)

            return (
              <li key={id}>
                <button
                  type="button"
                  onClick={() =>
                    setCapabilityId(isOpen ? null : id)
                  }
                  className={`w-full flex gap-2.5 px-2.5 py-2 rounded-lg text-left transition-colors ${isOpen
                      ? 'bg-white/15 ring-1 ring-cyan-400/40'
                      : 'hover:bg-white/10 text-slate-300'
                    }`}
                >
                  <Icon
                    size={16}
                    className="shrink-0 mt-0.5 text-cyan-300"
                  />

                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-slate-100">
                      {title}
                    </p>

                    <p className="text-[10px] leading-snug text-slate-500 line-clamp-1">
                      {summary}
                    </p>
                  </div>

                  <ChevronRight
                    size={14}
                    className={`shrink-0 mt-1 text-slate-500 transition-transform ${isOpen ? 'rotate-90' : ''
                      }`}
                  />
                </button>
              </li>
            )
          })}
        </ul>

        {/* Expanded Capability Card */}
        {selectedStep && capabilityId && (
          <div className="mt-3 rounded-xl border border-cyan-500/30 bg-slate-900/90 p-3 text-xs shadow-xl">
            <div className="flex items-start justify-between gap-2 mb-2">
              <p className="font-semibold text-cyan-200">
                {t(`pipeline.steps.${capabilityId}.title`)}
              </p>

              <button
                type="button"
                onClick={() => setCapabilityId(null)}
                className="text-slate-500 hover:text-white"
                aria-label={t('common.close')}
              >
                <X size={14} />
              </button>
            </div>

            <p className="text-slate-400 leading-relaxed">
              {t(`pipeline.steps.${capabilityId}.summary`)}
            </p>

            {currentView !== 'pipeline' && (
              <button
                type="button"
                onClick={() => onNavigate('pipeline')}
                className="mt-3 w-full rounded-lg bg-cyan-600/90 py-1.5 text-[11px] font-semibold hover:bg-cyan-500"
              >
                {t('nav.viewFullPipeline')}
              </button>
            )}
          </div>
        )}
      </div>

      {/* Fixed Footer */}
      <div className="shrink-0 p-4 border-t border-white/10 text-[10px] text-slate-500 leading-relaxed bg-slate-950/40">
        {t('nav.footer')}
      </div>
    </aside>
  )
}