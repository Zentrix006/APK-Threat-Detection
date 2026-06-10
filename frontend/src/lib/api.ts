import axios, { AxiosError } from 'axios'

/** Always same-origin so Next.js route handlers proxy to backend at runtime. */
export const api = axios.create({
  baseURL: '',
  timeout: 120000,
})

export function getApiErrorMessage(error: unknown, fallback = 'Something went wrong'): string {
  if (axios.isAxiosError(error)) {
    const ax = error as AxiosError<{ detail?: string | { msg?: string }[]; message?: string }>
    if (!ax.response) {
      return 'Cannot reach the analysis server. Use http://localhost (Docker) and ensure all containers are running.'
    }
    const detail = ax.response.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
    if (ax.response.data?.message) return ax.response.data.message
    if (ax.response.status === 500) {
      return 'Server error (500). Check backend logs: docker logs apk-threat-backend'
    }
    if (ax.response.status === 413) return 'File is too large for upload.'
    if (ax.response.status === 404) return 'Requested resource was not found.'
  }
  if (error instanceof Error && error.message) return error.message
  return fallback
}

export interface ScanProgress {
  apk_id: string
  phase: string
  message: string
  percent: number
  phase_percent?: number
  eta_seconds: number
  status?: string
  error?: string
}

export interface InvestigationFailure {
  message: string
  phase?: string | null
  progress_message?: string | null
  hint?: string
}

export interface InvestigationBundle {
  apk: {
    id: string
    filename: string
    file_hash: string
    package_name?: string
    app_name?: string
    status: string
    error_message?: string
  }
  analysis: {
    id?: string
    status?: string
    risk_score?: number
    risk_level?: string
    findings: Record<string, unknown>
  }
  intelligence: Record<string, unknown>
  threat_graph: { nodes?: unknown[] } | unknown[]
  threat_graph_edges: unknown[]
  artifacts: Array<{ type: string; value: string; suspicious: boolean }>
  threats: Array<{ type: string; severity: string; description: string }>
  reports: Array<{ id: string; status: string; title?: string }>
  failure?: InvestigationFailure | null
}

export async function retryInvestigation(apkId: string): Promise<{ message: string }> {
  const res = await api.post<{ message: string }>(`/api/v1/apks/${apkId}/retry-investigation`)
  return res.data
}

export async function deleteAPK(apkId: string): Promise<{ message: string }> {
  const res = await api.delete<{ message: string }>(`/api/v1/apks/${apkId}`)
  return res.data
}

export interface DashboardStats {
  total_apks: number
  failed_apks: number
  avg_risk_score: number
  critical_threats: number
  analyzed_count: number
}

export interface ApkListItem {
  id: string
  filename: string
  status: string
  upload_date: string
  risk_level: string
  error_message?: string
}
