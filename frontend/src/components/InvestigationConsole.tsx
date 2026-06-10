'use client'

import { useCallback, useEffect, useState } from 'react'
import {
  ArrowLeft,
  BookOpen,
  Brain,
  FileText,
  GitBranch,
  Loader2,
  Network,
  RotateCcw,
  Shield,
  Skull,
  Wallet,
} from 'lucide-react'
import {
  api,
  getApiErrorMessage,
  retryInvestigation,
  type InvestigationBundle,
} from '@/lib/api'
import { useScanProgress } from '@/hooks/useScanProgress'
import StatusAlert, { statusBadgeClass } from '@/components/StatusAlert'
import ScanProgressBar from '@/components/ScanProgressBar'
import ThreatGraphView from '@/components/ThreatGraphView'
import InvestigationPipelineStrip from '@/components/InvestigationPipelineStrip'
import type { PipelineTabId } from '@/lib/pipeline'
import { useLanguage } from '@/contexts/LanguageContext'
import { formatINRRange } from '@/lib/i18n'

const TABS = [
  { id: 'overview', label: 'SOC Overview', icon: Shield },
  { id: 'static', label: 'Static', icon: FileText },
  { id: 'dynamic', label: 'Dynamic', icon: Network },
  { id: 'mitre', label: 'MITRE ATT&CK', icon: Skull },
  { id: 'graph', label: 'Threat Graph', icon: GitBranch },
  { id: 'story', label: 'Malware Story', icon: BookOpen },
  { id: 'twin', label: 'Digital Twin', icon: Brain },
  { id: 'fraud', label: 'Fraud Impact', icon: Wallet },
  { id: 'reverse', label: 'RE Assistant', icon: Brain },
] as const

type TabId = (typeof TABS)[number]['id']

interface InvestigationConsoleProps {
  apkId: string
  onBack?: () => void
}

export default function InvestigationConsole({ apkId, onBack }: InvestigationConsoleProps) {
  const { locale, t, statusLabel, impactLevelLabel } = useLanguage()
  const [data, setData] = useState<InvestigationBundle | null>(null)
  const [tab, setTab] = useState<TabId>('overview')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [reportBusy, setReportBusy] = useState(false)
  const [reportMsg, setReportMsg] = useState<string | null>(null)
  const [retryBusy, setRetryBusy] = useState(false)
  const { progress, isRunning, isFailed, refresh: refreshProgress } = useScanProgress(apkId)

  const load = useCallback(async () => {
    setError(null)
    try {
      const res = await api.get<InvestigationBundle>(`/api/v1/investigation/${apkId}`)
      setData(res.data)
    } catch (e) {
      setError(getApiErrorMessage(e))
    } finally {
      setLoading(false)
    }
  }, [apkId])

  useEffect(() => {
    setLoading(true)
    load()
  }, [load])

  useEffect(() => {
    if (!data || data.apk.status === 'failed') return
    if (data.apk.status !== 'analyzing' && data.apk.status !== 'uploaded') return
    const t = setInterval(load, 5000)
    return () => clearInterval(t)
  }, [data?.apk.status, load, data])

  const handleRetry = async () => {
    setRetryBusy(true)
    setError(null)
    try {
      await retryInvestigation(apkId)
      setLoading(true)
      await refreshProgress()
      await load()
    } catch (e) {
      setError(getApiErrorMessage(e, 'Could not restart investigation.'))
    } finally {
      setRetryBusy(false)
    }
  }

  const generateReport = async () => {
    setReportBusy(true)
    setReportMsg(null)
    try {
      const res = await api.post(`/api/v1/reports/generate/${apkId}`)
      setReportMsg(res.data.message || 'SOC report queued.')
      load()
    } catch (e) {
      setReportMsg(getApiErrorMessage(e, 'Report generation failed.'))
    } finally {
      setReportBusy(false)
    }
  }

  if (loading && !data) {
    return (
      <div className="space-y-4 max-w-2xl">
        {progress && isRunning && <ScanProgressBar progress={progress} />}
        <div className="flex flex-col items-center py-12 text-slate-500">
          <Loader2 className="animate-spin mb-3" size={32} />
          <p className="font-medium">{t('analysis.running')}</p>
        </div>
      </div>
    )
  }

  if (error && !data) {
    return (
      <StatusAlert
        variant="error"
        title={t('analysis.unavailable')}
        message={error}
        onRetry={load}
        retryLabel={t('common.tryAgain')}
      />
    )
  }

  if (!data) return null

  const intel = (data.intelligence || {}) as InvestigationBundle['intelligence'] & {
    threat_reasoning?: { analyst_narrative?: string; capabilities?: string[] }
    threat_graph?: { nodes?: unknown[]; edges?: unknown[] }
    malware_story?: { chapters?: Array<{ phase: string; title: string; narrative: string }> }
    digital_twin?: { predictions?: Array<{ behavior: string; likelihood: number; timeframe: string }> }
    fraud_impact?: {
      currency?: string
      estimated_loss_per_device?: { low: number; high: number }
      organizational_impact?: string
      recommended_actions?: string[]
      risk_factors?: string[]
      remediation_priority?: string
    }
    reverse_engineering?: { explanations?: Array<{ category: string; explanation: string }> }
    ti_correlation?: { correlations?: Array<{ source: string; match: string; indicator: string }> }
    mitre_mappings?: Array<{ tactic: string; technique: string }>
  }
  const reasoning = intel.threat_reasoning
  const graphNodes = Array.isArray(data.threat_graph)
    ? data.threat_graph
    : (data.threat_graph as { nodes?: unknown[] })?.nodes || intel.threat_graph?.nodes || []
  const graphEdges = data.threat_graph_edges?.length
    ? data.threat_graph_edges
    : intel.threat_graph?.edges || []

  const failed = data.apk.status === 'failed'
  const failure = data.failure
  const failureMessage =
    failure?.message || data.apk.error_message || progress?.error || progress?.message

  const riskClass =
    (data.analysis.risk_score ?? 0) >= 60
      ? 'risk-glow-high'
      : (data.analysis.risk_score ?? 0) >= 30
        ? ''
        : 'risk-glow-low'

  const openTab = (t: PipelineTabId) => setTab(t)

  return (
    <div className="space-y-6 max-w-6xl">
      <InvestigationPipelineStrip activePhase={progress?.phase} onOpenTab={openTab} />

      <div className={`card-soc p-5 flex flex-wrap items-start justify-between gap-4 ${riskClass}`}>
        <div>
          {onBack && (
            <button
              type="button"
              onClick={onBack}
              className="inline-flex items-center gap-1 text-sm text-indigo-600 hover:text-indigo-800 mb-2 font-medium"
            >
              <ArrowLeft size={16} /> {t('analysis.backDashboard')}
            </button>
          )}
          <h2 className="text-2xl font-bold text-slate-900">{data.apk.filename}</h2>
          <p className="text-xs font-mono text-slate-500 mt-1 break-all">{data.apk.file_hash}</p>
          <span
            className={`inline-flex mt-2 px-2.5 py-0.5 rounded-full text-xs font-semibold ring-1 ring-inset ${statusBadgeClass(data.apk.status)}`}
          >
            {statusLabel(data.apk.status)}
          </span>
        </div>
        <div className="text-right">
          <p className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-cyan-600 bg-clip-text text-transparent tabular-nums">
            {data.analysis.risk_score?.toFixed(0) ?? '—'}
          </p>
          <p className="text-sm text-slate-500 uppercase tracking-wide font-medium">
            {t('analysis.riskLabel', { level: data.analysis.risk_level || 'pending' })}
          </p>
          <button
            type="button"
            onClick={generateReport}
            disabled={reportBusy || data.apk.status !== 'analyzed'}
            className="mt-3 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 px-4 py-2 text-sm font-semibold text-white hover:opacity-95 disabled:opacity-50 shadow-md"
          >
            {reportBusy ? t('analysis.generating') : t('analysis.generateReport')}
          </button>
          {reportMsg && <p className="text-xs text-slate-600 mt-2 max-w-xs ml-auto">{reportMsg}</p>}
        </div>
      </div>

      {failed && failureMessage && (
        <div className="space-y-2">
          <StatusAlert
            variant="error"
            title={t('analysis.failedTitle')}
            message={failureMessage}
            onRetry={handleRetry}
            retryLabel={t('common.tryAgain')}
          />
          {failure?.hint && (
            <p className="text-sm text-slate-600 bg-slate-50 border border-slate-200 rounded-lg px-4 py-3">
              {failure.hint}
            </p>
          )}
        </div>
      )}

      {failed && (
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={handleRetry}
            disabled={retryBusy}
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
          >
            <RotateCcw size={16} className={retryBusy ? 'animate-spin' : ''} />
            {retryBusy ? t('analysis.retrying') : t('analysis.retry')}
          </button>
          {failure?.phase && (
            <span className="text-xs text-slate-500 self-center">
              {t('analysis.failedPhase', { phase: failure.phase })}
            </span>
          )}
        </div>
      )}

      {progress && (isRunning || isFailed) && <ScanProgressBar progress={progress} />}

      <div className="flex flex-wrap gap-1 border-b border-slate-200/80 pb-1 bg-white/50 rounded-t-xl px-1 pt-1">
        {TABS.map(({ id, icon: Icon }) => (
          <button
            key={id}
            type="button"
            onClick={() => setTab(id)}
            className={`inline-flex items-center gap-1.5 px-3 py-2 text-sm font-medium rounded-t-lg transition-colors -mb-px ${
              tab === id ? 'tab-active' : 'tab-inactive'
            }`}
          >
            <Icon size={14} />
            {t(`analysis.tabs.${id}`)}
          </button>
        ))}
      </div>

      <div className="card-soc p-6 min-h-[320px]">
        {tab === 'overview' && (
          <div className="space-y-4">
            <h3 className="font-semibold text-slate-900">{t('analysis.aiReasoning')}</h3>
            <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">
              {reasoning?.analyst_narrative || t('analysis.reasoningPending')}
            </p>
            {reasoning?.capabilities && (
              <div className="flex flex-wrap gap-2">
                {reasoning.capabilities.map((c) => (
                  <span key={c} className="px-2 py-1 bg-red-50 text-red-800 text-xs rounded-full font-medium">
                    {c}
                  </span>
                ))}
              </div>
            )}
            <h3 className="font-semibold text-slate-900 pt-4">{t('analysis.tiCorrelation')}</h3>
            <ul className="text-sm space-y-2">
              {(intel.ti_correlation?.correlations || []).map((c, i) => (
                <li key={i} className="border-l-2 border-blue-500 pl-3 text-slate-700">
                  <span className="font-medium text-slate-900">{c.source}</span>: {c.match}
                  <span className="text-slate-500 block text-xs">{c.indicator}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {tab === 'static' && (
          <div className="grid sm:grid-cols-2 gap-4 text-sm">
            <IocList title={t('analysis.permissions')} items={(data.analysis.findings.permissions as string[]) || []} noneLabel={t('common.none')} />
            <IocList title={t('analysis.urls')} items={(data.analysis.findings.urls as string[]) || []} noneLabel={t('common.none')} />
            <IocList title={t('analysis.ips')} items={(data.analysis.findings.ips as string[]) || []} noneLabel={t('common.none')} />
            <IocList title={t('analysis.domains')} items={(data.analysis.findings.domains as string[]) || []} noneLabel={t('common.none')} />
          </div>
        )}

        {tab === 'dynamic' && (
          <pre className="text-xs bg-slate-50 p-4 rounded-lg overflow-auto max-h-96">
            {JSON.stringify(data.analysis.findings.dynamic || { note: t('analysis.dynamicNote') }, null, 2)}
          </pre>
        )}

        {tab === 'mitre' && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-500 border-b">
                  <th className="py-2">{t('analysis.tactic')}</th>
                  <th className="py-2">{t('analysis.technique')}</th>
                </tr>
              </thead>
              <tbody>
                {(intel.mitre_mappings || []).map((m, i) => (
                  <tr key={i} className="border-b border-slate-100">
                    <td className="py-2 font-medium">{m.tactic}</td>
                    <td className="py-2">{m.technique}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {tab === 'graph' && (
          <ThreatGraphView
            nodes={graphNodes as { id: string; type: string; label: string; data?: Record<string, unknown> }[]}
            edges={graphEdges as { source: string; target: string }[]}
          />
        )}

        {tab === 'story' &&
          (intel.malware_story?.chapters || []).map((ch, i) => (
            <div key={i} className="mb-6 last:mb-0">
              <p className="text-xs font-bold text-blue-600 uppercase">{ch.phase}</p>
              <h4 className="font-semibold text-slate-900">{ch.title}</h4>
              <p className="text-sm text-slate-600 mt-1 leading-relaxed">{ch.narrative}</p>
            </div>
          ))}

        {tab === 'twin' && (
          <ul className="space-y-3">
            {(intel.digital_twin?.predictions || []).map((p, i) => (
              <li key={i} className="rounded-lg border border-slate-100 p-4">
                <p className="font-medium text-slate-900">{p.behavior}</p>
                <p className="text-sm text-slate-500 mt-1">
                  {t('analysis.likelihood', {
                    pct: (p.likelihood * 100).toFixed(0),
                    timeframe: p.timeframe,
                  })}
                </p>
              </li>
            ))}
          </ul>
        )}

        {tab === 'fraud' && intel.fraud_impact && (
          <div className="space-y-4 text-sm">
            <div className="rounded-xl bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200/80 p-4">
              <p className="text-slate-600">{t('analysis.fraud.lossPerDevice')}</p>
              <p className="text-2xl font-bold text-slate-900 mt-1 tabular-nums">
                {formatINRRange(
                  intel.fraud_impact.estimated_loss_per_device?.low ?? 0,
                  intel.fraud_impact.estimated_loss_per_device?.high ?? 0,
                  locale,
                  intel.fraud_impact.currency,
                )}
              </p>
            </div>
            <p>
              {t('analysis.fraud.orgImpact')}:{' '}
              <span className="font-semibold text-red-700 uppercase">
                {impactLevelLabel(intel.fraud_impact.organizational_impact || '')}
              </span>
            </p>
            {intel.fraud_impact.remediation_priority && (
              <p>
                {t('analysis.fraud.remediation')}:{' '}
                <strong>{intel.fraud_impact.remediation_priority}</strong>
              </p>
            )}
            {(intel.fraud_impact.risk_factors || []).length > 0 && (
              <div>
                <p className="font-semibold text-slate-800 mb-2">{t('analysis.fraud.riskFactors')}</p>
                <ul className="list-disc pl-5 space-y-1 text-slate-700">
                  {intel.fraud_impact.risk_factors!.map((f, i) => (
                    <li key={i}>{f}</li>
                  ))}
                </ul>
              </div>
            )}
            <div>
              <p className="font-semibold text-slate-800 mb-2">{t('analysis.fraud.recommended')}</p>
              <ul className="list-disc pl-5 space-y-1 text-slate-700">
                {(intel.fraud_impact.recommended_actions || []).map((a, i) => (
                  <li key={i}>{a}</li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {tab === 'reverse' && (
          <ul className="space-y-3">
            {(intel.reverse_engineering?.explanations || []).map((ex, i) => (
              <li key={i} className="rounded-lg bg-slate-50 p-4 border border-slate-100">
                <span className="text-xs font-bold uppercase text-slate-500">{ex.category}</span>
                <p className="text-sm text-slate-800 mt-1">{ex.explanation}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

function IocList({
  title,
  items,
  noneLabel,
}: {
  title: string
  items: string[]
  noneLabel: string
}) {
  return (
    <div>
      <h4 className="font-semibold text-slate-800 mb-2">
        {title} ({items.length})
      </h4>
      <ul className="max-h-40 overflow-y-auto text-slate-600 space-y-1 font-mono text-xs">
        {items.length ? items.slice(0, 30).map((x) => <li key={x}>{x}</li>) : <li>{noneLabel}</li>}
      </ul>
    </div>
  )
}
