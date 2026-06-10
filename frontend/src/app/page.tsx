'use client'

import { useState } from 'react'
import Header from '@/components/Header'
import Sidebar from '@/components/Sidebar'
import Dashboard from '@/components/Dashboard'
import UploadArea from '@/components/UploadArea'
import InvestigationConsole from '@/components/InvestigationConsole'
import PipelineOverview from '@/components/PipelineOverview'
import StatusAlert from '@/components/StatusAlert'
import type { View } from '@/components/Sidebar'
import { useLanguage } from '@/contexts/LanguageContext'

export default function Home() {
  const { t } = useLanguage()
  const [currentView, setCurrentView] = useState<View>('dashboard' as View)
  const [selectedAPKId, setSelectedAPKId] = useState<string | null>(null)

  const handleNavigation = (view: View) => {
    setCurrentView(view)
    if (view !== 'analysis') setSelectedAPKId(null)
  }

  const goToAnalysis = (apkId: string) => {
    setSelectedAPKId(apkId)
    setCurrentView('analysis')
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar currentView={currentView} onNavigate={handleNavigation} />

      <div className="flex flex-1 flex-col min-w-0 overflow-hidden">
        <Header />

        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          {currentView === 'dashboard' && <Dashboard onAPKSelect={goToAnalysis} />}

          {currentView === 'upload' && <UploadArea onComplete={goToAnalysis} />}

          {currentView === 'pipeline' && (
            <PipelineOverview onStartUpload={() => handleNavigation('upload')} />
          )}

          {currentView === 'analysis' && selectedAPKId && (
            <InvestigationConsole
              apkId={selectedAPKId}
              onBack={() => handleNavigation('dashboard')}
            />
          )}

          {currentView === 'analysis' && !selectedAPKId && (
            <div className="max-w-md space-y-4">
              <StatusAlert
                variant="info"
                title={t('analysis.noApkTitle')}
                message={t('analysis.noApkMessage')}
              />
              <div className="flex gap-4 text-sm">
                <button
                  type="button"
                  onClick={() => handleNavigation('upload')}
                  className="font-semibold text-blue-600 hover:underline"
                >
                  {t('analysis.goUpload')}
                </button>
                <button
                  type="button"
                  onClick={() => handleNavigation('dashboard')}
                  className="font-semibold text-blue-600 hover:underline"
                >
                  {t('analysis.goDashboard')}
                </button>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
