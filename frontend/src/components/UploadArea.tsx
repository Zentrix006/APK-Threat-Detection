'use client'

import { useState, useRef } from 'react'
import { FileArchive, Upload } from 'lucide-react'
import { api, getApiErrorMessage } from '@/lib/api'
import { useScanProgress } from '@/hooks/useScanProgress'
import StatusAlert from '@/components/StatusAlert'
import ScanProgressBar from '@/components/ScanProgressBar'
import { useLanguage } from '@/contexts/LanguageContext'

const MAX_SIZE_MB = 500
const MAX_BYTES = MAX_SIZE_MB * 1024 * 1024

interface UploadAreaProps {
  onComplete: (apkId: string) => void
}

export default function UploadArea({ onComplete }: UploadAreaProps) {
  const { t } = useLanguage()
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const [message, setMessage] = useState('')
  const [dragOver, setDragOver] = useState(false)
  const [scanApkId, setScanApkId] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const { progress, isRunning } = useScanProgress(scanApkId)

  const validateFile = (selected: File): string | null => {
    if (!selected.name.toLowerCase().endsWith('.apk')) {
      return t('upload.apkOnly')
    }
    if (selected.size === 0) return t('upload.empty')
    if (selected.size > MAX_BYTES) return t('upload.tooLarge', { mb: MAX_SIZE_MB })
    return null
  }

  const selectFile = (selected: File) => {
    const err = validateFile(selected)
    if (err) {
      setStatus('error')
      setMessage(err)
      setFile(null)
      return
    }
    setFile(selected)
    setStatus('idle')
    setMessage('')
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    if (e.dataTransfer.files.length > 0) selectFile(e.dataTransfer.files[0])
  }

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    setStatus('idle')
    setScanApkId(null)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await api.post('/api/v1/apks/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      const apkId = response.data.id as string
      setScanApkId(apkId)
      setStatus('success')
      setMessage(t('upload.successMessage'))
      setFile(null)

      const waitDone = setInterval(async () => {
        try {
          const pr = await api.get(`/api/v1/investigation/${apkId}/progress`)
          if (pr.data.percent >= 100 || pr.data.status === 'analyzed') {
            clearInterval(waitDone)
            onComplete(apkId)
          }
        } catch {
          clearInterval(waitDone)
          onComplete(apkId)
        }
      }, 2500)
    } catch (error) {
      setStatus('error')
      setMessage(getApiErrorMessage(error, t('upload.uploadFailed')))
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">{t('upload.title')}</h2>
        <p className="text-sm text-slate-500 mt-1">{t('upload.pageSubtitle')}</p>
      </div>

      <div
        onDrop={handleDrop}
        onDragOver={(e) => {
          e.preventDefault()
          setDragOver(true)
        }}
        onDragLeave={() => setDragOver(false)}
        onClick={() => fileInputRef.current?.click()}
        className={`rounded-xl border-2 border-dashed p-12 text-center cursor-pointer transition-all ${
          dragOver ? 'border-blue-500 bg-blue-50' : 'border-slate-300 bg-white hover:border-blue-400'
        }`}
      >
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-slate-100">
          {file ? <FileArchive className="text-blue-600" size={28} /> : <Upload className="text-slate-400" size={28} />}
        </div>
        <h3 className="text-lg font-semibold text-slate-900">
          {file ? file.name : t('upload.dropHint')}
        </h3>
        <p className="text-sm text-slate-500 mt-2">
          {file
            ? `${(file.size / (1024 * 1024)).toFixed(2)} MB`
            : t('upload.sizeHint', { mb: MAX_SIZE_MB })}
        </p>
        <input
          ref={fileInputRef}
          type="file"
          accept=".apk"
          onChange={(e) => e.target.files?.[0] && selectFile(e.target.files[0])}
          className="hidden"
        />
      </div>

      {status === 'error' && (
        <StatusAlert
          variant="error"
          title={t('upload.uploadFailed')}
          message={message}
          onRetry={handleUpload}
          retryLabel={t('common.tryAgain')}
        />
      )}
      {status === 'success' && !isRunning && (
        <StatusAlert variant="success" title={t('upload.uploadCompleteTitle')} message={message} />
      )}
      {uploading && (
        <StatusAlert
          variant="loading"
          title={t('upload.uploadingTitle')}
          message={t('upload.uploadingMessage')}
        />
      )}

      {progress && isRunning && <ScanProgressBar progress={progress} />}

      <button
        type="button"
        onClick={handleUpload}
        disabled={!file || uploading || isRunning}
        className="w-full rounded-xl bg-blue-600 py-3.5 text-white font-semibold shadow-md hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed"
      >
        {uploading
          ? t('upload.uploading')
          : isRunning
            ? t('upload.investigationRunning')
            : t('upload.uploadBtn')}
      </button>
    </div>
  )
}
