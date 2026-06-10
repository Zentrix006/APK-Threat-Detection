'use client'

import { useCallback, useEffect, useState } from 'react'
import { AlertTriangle, Package, RefreshCw, ShieldAlert, TrendingUp, Trash2 } from 'lucide-react'
import {
  api,
  getApiErrorMessage,
  type ApkListItem,
  type DashboardStats,
  type ScanProgress,
  deleteAPK,
} from '@/lib/api'
import StatusAlert, { statusBadgeClass } from '@/components/StatusAlert'
import ScanProgressBar from '@/components/ScanProgressBar'
import { useLanguage } from '@/contexts/LanguageContext'

interface DashboardProps {
  onAPKSelect: (apkId: string) => void
}

function StatCard({
  label,
  value,
  icon: Icon,
  accent,
}: {
  label: string
  value: string | number
  icon: typeof Package
  accent: string
}) {
  return (
    <div className="card-soc p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">{label}</p>
          <p className="text-3xl font-bold text-slate-900 mt-1 tabular-nums">{value}</p>
        </div>
        <div className={`p-2.5 rounded-lg ${accent}`}>
          <Icon size={22} className="text-white" />
        </div>
      </div>
    </div>
  )
}

export default function Dashboard({ onAPKSelect }: DashboardProps) {
  const { t, statusLabel } = useLanguage()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [apks, setAPKs] = useState<ApkListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeProgress, setActiveProgress] = useState<ScanProgress | null>(null)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null)

  const handleDeleteAPK = useCallback(
    async (apkId: string) => {
      try {
        setDeletingId(apkId)
        await deleteAPK(apkId)
        setDeleteConfirm(null)
        // Refresh the list
        await fetchDashboardData()
      } catch (err) {
        setError(getApiErrorMessage(err, 'Failed to delete APK'))
      } finally {
        setDeletingId(null)
      }
    },
    [],
  )

  const fetchDashboardData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const listRes = await api.get('/api/v1/apks?limit=10')
      setAPKs(listRes.data.apks || [])

      try {
        const statsRes = await api.get<DashboardStats>('/api/v1/apks/stats')
        setStats(statsRes.data)
      } catch {
        setStats({
          total_apks: listRes.data.total ?? 0,
          failed_apks: 0,
          avg_risk_score: 0,
          critical_threats: 0,
          analyzed_count: 0,
        })
      }

      const running = (listRes.data.apks || []).find(
        (a: ApkListItem) => a.status === 'analyzing' || a.status === 'uploaded',
      )
      if (running) {
        const prog = await api.get<ScanProgress>(
          `/api/v1/investigation/${running.id}/progress`,
        )
        setActiveProgress(prog.data)
      } else {
        setActiveProgress(null)
      }
    } catch (err) {
      setError(getApiErrorMessage(err, t('dashboard.loadError')))
    } finally {
      setLoading(false)
    }
  }, [t])

  useEffect(() => {
    fetchDashboardData()
  }, [fetchDashboardData])

  useEffect(() => {
    if (!activeProgress) return
    const t = setInterval(fetchDashboardData, 3000)
    return () => clearInterval(t)
  }, [activeProgress, fetchDashboardData])

  if (loading && !apks.length) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-slate-500">
        <RefreshCw className="animate-spin mb-3" size={28} />
        <p className="text-sm font-medium">{t('dashboard.loading')}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-6xl">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">{t('dashboard.title')}</h2>
          <p className="text-sm text-slate-500 mt-1">{t('dashboard.subtitle')}</p>
        </div>
        <button
          type="button"
          onClick={fetchDashboardData}
          className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
        >
          <RefreshCw size={16} />
          {t('common.refresh')}
        </button>
      </div>

      {error && (
        <StatusAlert
          variant="error"
          title={t('dashboard.unavailable')}
          message={error}
          onRetry={fetchDashboardData}
        />
      )}

      {activeProgress &&
        (activeProgress.status === 'failed' || activeProgress.phase === 'failed' ? (
          <ScanProgressBar progress={activeProgress} />
        ) : (
          activeProgress.status !== 'analyzed' && <ScanProgressBar progress={activeProgress} />
        ))}

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard label={t('dashboard.totalApks')} value={stats?.total_apks ?? 0} icon={Package} accent="bg-blue-600" />
        <StatCard label={t('dashboard.avgRisk')} value={stats?.avg_risk_score ?? 0} icon={TrendingUp} accent="bg-amber-500" />
        <StatCard label={t('dashboard.highCritical')} value={stats?.critical_threats ?? 0} icon={ShieldAlert} accent="bg-red-600" />
      </div>

      <div className="card-soc overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
          <h3 className="font-semibold text-slate-900">{t('dashboard.recent')}</h3>
          {stats && stats.failed_apks > 0 && (
            <span className="inline-flex items-center gap-1 text-xs font-medium text-amber-800 bg-amber-50 px-2 py-1 rounded-full">
              <AlertTriangle size={12} />
              {t('dashboard.failedCount', { count: stats.failed_apks })}
            </span>
          )}
        </div>

        {apks.length === 0 ? (
          <div className="px-5 py-16 text-center">
            <Package className="mx-auto text-slate-300 mb-3" size={40} />
            <p className="text-slate-600 font-medium">{t('dashboard.emptyTitle')}</p>
            <p className="text-sm text-slate-500 mt-1">{t('dashboard.emptyBody')}</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 text-left text-slate-500">
                  <th className="py-3 px-5 font-medium">{t('dashboard.filename')}</th>
                  <th className="py-3 px-5 font-medium">{t('dashboard.status')}</th>
                  <th className="py-3 px-5 font-medium">{t('dashboard.uploaded')}</th>
                  <th className="py-3 px-5 font-medium">{t('dashboard.risk')}</th>
                  <th className="py-3 px-5 font-medium" />
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {apks.map((apk) => (
                  <tr key={apk.id} className="hover:bg-slate-50/80">
                    <td className="py-3 px-5 font-medium text-slate-900 max-w-xs truncate">{apk.filename}</td>
                    <td className="py-3 px-5">
                      <span
                        className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-semibold ring-1 ring-inset ${statusBadgeClass(apk.status)}`}
                      >
                        {statusLabel(apk.status)}
                      </span>
                      {apk.status === 'failed' && apk.error_message && (
                        <p className="text-xs text-red-700 mt-1 max-w-md font-mono line-clamp-2" title={apk.error_message}>
                          {apk.error_message}
                        </p>
                      )}
                    </td>
                    <td className="py-3 px-5 text-slate-600">
                      {apk.upload_date ? new Date(apk.upload_date).toLocaleString() : '—'}
                    </td>
                    <td className="py-3 px-5 capitalize">{apk.risk_level || 'unknown'}</td>
                    <td className="py-3 px-5 text-right space-x-2">
                      <button
                        type="button"
                        onClick={() => onAPKSelect(apk.id)}
                        className="text-blue-600 hover:text-blue-800 font-semibold text-sm"
                      >
                        {t('common.open')}
                      </button>
                      <button
                        type="button"
                        onClick={() => setDeleteConfirm(apk.id)}
                        disabled={deletingId === apk.id}
                        className="text-red-600 hover:text-red-800 font-semibold text-sm disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center gap-1"
                        title="Delete this APK"
                      >
                        <Trash2 size={14} />
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg p-6 max-w-sm mx-4">
            <h3 className="text-lg font-semibold text-slate-900 mb-2">Delete APK?</h3>
            <p className="text-sm text-slate-600 mb-6">
              Are you sure you want to delete this APK and all associated analysis data? This action cannot be undone.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                type="button"
                onClick={() => setDeleteConfirm(null)}
                disabled={deletingId !== null}
                className="px-4 py-2 text-sm font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => {
                  if (deleteConfirm) {
                    handleDeleteAPK(deleteConfirm)
                  }
                }}
                disabled={deletingId !== null}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center gap-2"
              >
                {deletingId ? (
                  <>
                    <RefreshCw size={14} className="animate-spin" />
                    Deleting...
                  </>
                ) : (
                  <>
                    <Trash2 size={14} />
                    Delete APK
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
