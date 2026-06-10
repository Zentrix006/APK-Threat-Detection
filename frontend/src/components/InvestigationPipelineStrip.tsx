'use client'

import { useState } from 'react'
import { ChevronDown, ChevronRight, ExternalLink } from 'lucide-react'
import { INVESTIGATION_PIPELINE, type PipelineTabId } from '@/lib/pipeline'
import { useLanguage } from '@/contexts/LanguageContext'

interface InvestigationPipelineStripProps {
  activePhase?: string | null
  onOpenTab?: (tab: PipelineTabId) => void
}

export default function InvestigationPipelineStrip({
  activePhase,
  onOpenTab,
}: InvestigationPipelineStripProps) {
  const { t } = useLanguage()
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const toggle = (id: string) => {
    setExpandedId((prev) => (prev === id ? null : id))
  }

  return (
    <div className="card-soc overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-200/80 bg-gradient-to-r from-slate-50 to-indigo-50/60">
        <h3 className="text-sm font-bold text-slate-800 tracking-tight">{t('analysis.pipelineTitle')}</h3>
        <p className="text-xs text-slate-500 mt-0.5">{t('analysis.pipelineHint')}</p>
      </div>

      <div className="flex flex-wrap gap-2 p-3">
        {INVESTIGATION_PIPELINE.map((step, index) => {
          const isActive = step.phase != null && activePhase === step.phase
          const isExpanded = expandedId === step.id
          const Icon = step.icon
          const title = t(`pipeline.steps.${step.id}.title`)

          return (
            <div key={step.id} className="w-full sm:w-auto sm:flex-1 sm:min-w-[140px]">
              <button
                type="button"
                onClick={() => toggle(step.id)}
                className={`w-full flex items-center gap-2 rounded-lg border px-3 py-2.5 text-left transition-all ${
                  isActive
                    ? 'border-cyan-400 bg-cyan-50 shadow-sm shadow-cyan-100 ring-1 ring-cyan-200'
                    : isExpanded
                      ? 'border-indigo-300 bg-indigo-50/80'
                      : 'border-slate-200 bg-white hover:border-indigo-200 hover:bg-slate-50'
                }`}
              >
                <span
                  className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-md text-xs font-bold ${
                    isActive ? 'bg-cyan-600 text-white' : 'bg-slate-100 text-slate-600'
                  }`}
                >
                  {index + 1}
                </span>
                <span className="flex-1 min-w-0">
                  <span className="flex items-center gap-1">
                    <Icon size={14} className="shrink-0 text-indigo-600" />
                    <span className="text-xs font-semibold text-slate-800 truncate">{title}</span>
                  </span>
                </span>
                {isExpanded ? (
                  <ChevronDown size={14} className="text-slate-400 shrink-0" />
                ) : (
                  <ChevronRight size={14} className="text-slate-400 shrink-0" />
                )}
              </button>
            </div>
          )
        })}
      </div>

      {expandedId && (
        <PipelineDetailPanel
          stepId={expandedId}
          onOpenTab={onOpenTab}
          onClose={() => setExpandedId(null)}
        />
      )}
    </div>
  )
}

function PipelineDetailPanel({
  stepId,
  onOpenTab,
  onClose,
}: {
  stepId: string
  onOpenTab?: (tab: PipelineTabId) => void
  onClose: () => void
}) {
  const { t } = useLanguage()
  const step = INVESTIGATION_PIPELINE.find((s) => s.id === stepId)
  if (!step) return null
  const Icon = step.icon
  const title = t(`pipeline.steps.${stepId}.title`)
  const summary = t(`pipeline.steps.${stepId}.summary`)

  return (
    <div className="border-t border-indigo-100 bg-gradient-to-b from-indigo-50/50 to-white px-4 py-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-md">
            <Icon size={20} />
          </div>
          <div>
            <h4 className="font-semibold text-slate-900">{title}</h4>
            <p className="text-sm text-slate-600 mt-1 max-w-2xl">{summary}</p>
          </div>
        </div>
        <button type="button" onClick={onClose} className="text-xs text-slate-500 hover:text-slate-800 shrink-0">
          {t('common.close')}
        </button>
      </div>

      <div className="mt-4 grid sm:grid-cols-2 gap-4">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-wider text-indigo-600 mb-2">
            {t('analysis.whatItDoes')}
          </p>
          <ul className="text-sm text-slate-700 space-y-1.5 list-disc pl-4">
            {step.details.map((d) => (
              <li key={d}>{d}</li>
            ))}
          </ul>
        </div>
        <div>
          <p className="text-[10px] font-bold uppercase tracking-wider text-emerald-700 mb-2">
            {t('analysis.outputs')}
          </p>
          <ul className="text-sm text-slate-700 space-y-1">
            {step.outputs.map((o) => (
              <li key={o} className="flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 shrink-0" />
                {o}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {step.tab && onOpenTab && (
        <button
          type="button"
          onClick={() => onOpenTab(step.tab!)}
          className="mt-4 inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 transition-colors"
        >
          <ExternalLink size={16} />
          {t('common.viewResults', { title })}
        </button>
      )}
    </div>
  )
}
