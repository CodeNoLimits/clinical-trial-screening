import { useState } from 'react';
import type { Trial, Patient, ScreeningResponse } from './types';
import { screenPatient } from './services/api';
import TrialSelector from './components/TrialSelector';
import PatientForm from './components/PatientForm';
import ResultsDashboard from './components/ResultsDashboard';
import BatchUpload from './components/BatchUpload';

type TabType = 'single' | 'batch';

export default function App() {
  const [activeTab, setActiveTab] = useState<TabType>('single');
  const [selectedTrial, setSelectedTrial] = useState<Trial | null>(null);
  const [screeningResult, setScreeningResult] = useState<ScreeningResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTrialSelect = (trial: Trial | null) => {
    setSelectedTrial(trial);
    setScreeningResult(null);
    setError(null);
  };

  const handlePatientSubmit = async (patient: Patient) => {
    if (!selectedTrial) {
      setError('יש לבחור ניסוי קליני תחילה');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await screenPatient(selectedTrial.id, patient, true);
      setScreeningResult(result);
    } catch (err) {
      console.error('Screening failed:', err);
      setError(err instanceof Error ? err.message : 'שגיאה בבדיקת הכשירות');
    } finally {
      setLoading(false);
    }
  };

  const handleClearResults = () => {
    setScreeningResult(null);
    setError(null);
  };

  const tabButtonClass = (tab: TabType) => {
    const baseClass = 'px-8 py-4 font-semibold text-sm rounded-t-2xl transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2';
    if (activeTab === tab) {
      return `${baseClass} glass-card text-sky-700 border-t-4 border-sky-500 -mb-px shadow-lg`;
    }
    return `${baseClass} bg-white/50 text-gray-500 hover:bg-white/80 hover:text-gray-700`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-sky-50 via-white to-sky-100" dir="rtl">
      {/* Header */}
      <header className="header-gradient text-white shadow-xl relative z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
          <div className="flex items-center justify-between">
            <div className="animate-fade-in">
              <div className="flex items-center gap-4 mb-2">
                <div className="w-12 h-12 rounded-2xl bg-white/20 backdrop-blur flex items-center justify-center">
                  <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                </div>
                <div>
                  <h1 className="text-3xl sm:text-4xl font-bold tracking-tight">
                    מערכת סינון לניסויים קליניים
                  </h1>
                  <p className="mt-1 text-sky-200 text-base sm:text-lg">
                    בדיקת כשירות מטופלים אוטומטית מבוססת בינה מלאכותית
                  </p>
                </div>
              </div>
            </div>
            <div className="hidden md:flex items-center gap-4">
              <div className="text-left text-sm">
                <div className="text-sky-200">גרסה 1.0</div>
                <div className="text-white font-medium">MELEA Project</div>
              </div>
              <div className="w-16 h-16 rounded-2xl bg-white/10 backdrop-blur flex items-center justify-center float-animation">
                <svg className="w-10 h-10 text-sky-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 -mt-4 relative z-20">
        {/* Tab Navigation */}
        <div className="flex border-b border-gray-200/50 mb-8">
          <button
            onClick={() => setActiveTab('single')}
            className={tabButtonClass('single')}
          >
            <span className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center transition-colors ${activeTab === 'single' ? 'bg-sky-100 text-sky-600' : 'bg-gray-100 text-gray-400'
                }`}>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div className="text-right">
                <div className="font-bold">מטופל בודד</div>
                <div className={`text-xs ${activeTab === 'single' ? 'text-sky-500' : 'text-gray-400'}`}>בדיקה פרטנית</div>
              </div>
            </span>
          </button>
          <button
            onClick={() => setActiveTab('batch')}
            className={tabButtonClass('batch')}
          >
            <span className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center transition-colors ${activeTab === 'batch' ? 'bg-sky-100 text-sky-600' : 'bg-gray-100 text-gray-400'
                }`}>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <div className="text-right">
                <div className="font-bold">עיבוד קבוצתי</div>
                <div className={`text-xs ${activeTab === 'batch' ? 'text-sky-500' : 'text-gray-400'}`}>העלאת CSV/JSON</div>
              </div>
            </span>
          </button>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 glass-card border border-red-200 rounded-2xl p-5 animate-fade-in">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-red-100 flex items-center justify-center flex-shrink-0">
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <p className="text-red-700 font-medium flex-1">{error}</p>
              <button
                onClick={() => setError(null)}
                className="w-10 h-10 rounded-xl bg-red-50 flex items-center justify-center text-red-600 hover:bg-red-100 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* Single Patient Tab */}
        {activeTab === 'single' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 animate-fade-in">
            {/* Left Column - Trial Selector */}
            <div className="lg:col-span-3">
              <TrialSelector
                onTrialSelect={handleTrialSelect}
                selectedTrial={selectedTrial}
              />
            </div>

            {/* Middle Column - Patient Form */}
            <div className="lg:col-span-4">
              <PatientForm
                onSubmit={handlePatientSubmit}
                loading={loading}
              />
            </div>

            {/* Right Column - Results Dashboard */}
            <div className="lg:col-span-5">
              <ResultsDashboard
                result={screeningResult}
                onClear={handleClearResults}
              />
            </div>
          </div>
        )}

        {/* Batch Processing Tab */}
        {activeTab === 'batch' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 animate-fade-in">
            {/* Left Column - Trial Selector */}
            <div className="lg:col-span-4">
              <TrialSelector
                onTrialSelect={handleTrialSelect}
                selectedTrial={selectedTrial}
              />

              {/* Trial Selection Prompt */}
              {!selectedTrial && (
                <div className="mt-4 glass-card border border-amber-200 rounded-2xl p-5">
                  <div className="flex items-center gap-4 text-amber-700">
                    <div className="w-12 h-12 rounded-xl bg-amber-100 flex items-center justify-center">
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                    </div>
                    <span className="font-semibold">יש לבחור ניסוי קליני כדי להתחיל בעיבוד קבוצתי</span>
                  </div>
                </div>
              )}
            </div>

            {/* Right Column - Batch Upload */}
            <div className="lg:col-span-8">
              {selectedTrial ? (
                <BatchUpload
                  trialId={selectedTrial.id}
                  trialName={selectedTrial.name}
                />
              ) : (
                <div className="glass-card rounded-2xl p-12 text-center">
                  <div className="w-24 h-24 mx-auto rounded-3xl bg-gray-100 flex items-center justify-center mb-6">
                    <svg className="w-12 h-12 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">העלאה קבוצתית</h3>
                  <p className="text-gray-500">
                    בחר ניסוי קליני בצד ימין כדי להפעיל העלאת מטופלים מרובים
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white/50 backdrop-blur border-t border-gray-200/50 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-sm text-gray-500">
              © 2026 MELEA Project - מערכת סינון לניסויים קליניים
            </p>
            <div className="flex items-center gap-2 text-sm text-gray-400">
              <svg className="w-4 h-4 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <span>Powered by Gemini AI</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
