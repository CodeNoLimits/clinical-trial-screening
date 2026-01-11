import type { ScreeningResponse, CriterionResult } from '../types';

interface Props {
  result: ScreeningResponse | null;
  onClear: () => void;
}

// Status badge component for criterion results
function StatusBadge({ status }: { status: CriterionResult['status'] }) {
  const statusConfig = {
    MET: {
      bg: 'bg-gradient-to-r from-emerald-500 to-green-500',
      text: 'text-white',
      icon: '✓',
      label: 'עומד בקריטריון'
    },
    NOT_MET: {
      bg: 'bg-gradient-to-r from-red-500 to-rose-500',
      text: 'text-white',
      icon: '✗',
      label: 'לא עומד בקריטריון'
    },
    EXCLUDES: {
      bg: 'bg-gradient-to-r from-red-600 to-rose-600',
      text: 'text-white',
      icon: '⊘',
      label: 'מודח'
    },
    CLEAR: {
      bg: 'bg-gradient-to-r from-emerald-500 to-green-500',
      text: 'text-white',
      icon: '✓',
      label: 'תקין'
    },
    UNKNOWN: {
      bg: 'bg-gradient-to-r from-amber-500 to-yellow-500',
      text: 'text-white',
      icon: '?',
      label: 'לא ידוע'
    }
  };

  const config = statusConfig[status];

  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold ${config.bg} ${config.text} shadow-sm`}>
      <span className="text-sm">{config.icon}</span>
      {config.label}
    </span>
  );
}

// Decision banner component
function DecisionBanner({ decision }: { decision: 'ELIGIBLE' | 'INELIGIBLE' | 'UNCERTAIN' }) {
  const decisionConfig = {
    ELIGIBLE: {
      gradient: 'from-emerald-500 via-green-500 to-teal-500',
      glow: 'shadow-[0_0_40px_rgba(16,185,129,0.4)]',
      icon: (
        <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      label: 'כשיר להשתתפות',
      description: 'המטופל עומד בכל קריטריוני ההכללה ואינו עומד בקריטריוני הדחה'
    },
    INELIGIBLE: {
      gradient: 'from-red-500 via-rose-500 to-pink-500',
      glow: 'shadow-[0_0_40px_rgba(239,68,68,0.4)]',
      icon: (
        <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      label: 'לא כשיר להשתתפות',
      description: 'המטופל לא עומד בקריטריוני ההכללה או עומד בקריטריוני הדחה'
    },
    UNCERTAIN: {
      gradient: 'from-amber-500 via-yellow-500 to-orange-500',
      glow: 'shadow-[0_0_40px_rgba(245,158,11,0.4)]',
      icon: (
        <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      label: 'נדרשת בדיקה נוספת',
      description: 'חסר מידע לקביעת כשירות סופית'
    }
  };

  const config = decisionConfig[decision];

  return (
    <div className={`bg-gradient-to-r ${config.gradient} text-white rounded-2xl p-6 ${config.glow} animate-fade-in`}>
      <div className="flex items-center gap-5">
        <div className="w-16 h-16 rounded-2xl bg-white/20 backdrop-blur flex items-center justify-center">
          {config.icon}
        </div>
        <div>
          <h2 className="text-2xl sm:text-3xl font-bold">{config.label}</h2>
          <p className="text-sm opacity-90 mt-1">{config.description}</p>
        </div>
      </div>
    </div>
  );
}

// Criteria table component
function CriteriaTable({
  title,
  results,
  type
}: {
  title: string;
  results: CriterionResult[];
  type: 'inclusion' | 'exclusion'
}) {
  const headerGradient = type === 'inclusion'
    ? 'bg-gradient-to-r from-emerald-500 to-green-500'
    : 'bg-gradient-to-r from-red-500 to-rose-500';
  const iconBg = type === 'inclusion' ? 'bg-emerald-100 text-emerald-600' : 'bg-red-100 text-red-600';

  return (
    <div className="glass-card rounded-2xl overflow-hidden animate-slide-up">
      <div className={`${headerGradient} px-5 py-4 text-white`}>
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-xl ${type === 'inclusion' ? 'bg-white/20' : 'bg-white/20'} flex items-center justify-center`}>
            {type === 'inclusion' ? (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
              </svg>
            )}
          </div>
          <h3 className="font-bold text-lg">{title}</h3>
          <span className="mr-auto text-sm bg-white/20 px-3 py-1 rounded-full">
            {results.length} קריטריונים
          </span>
        </div>
      </div>
      <div className="divide-y divide-gray-100">
        {results.length === 0 ? (
          <div className="px-5 py-8 text-center text-gray-500">
            <svg className="w-12 h-12 mx-auto text-gray-300 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            אין קריטריונים
          </div>
        ) : (
          results.map((result, index) => (
            <div key={result.criterion_id || index} className="p-4 hover:bg-gray-50/50 transition-colors">
              <div className="flex items-start gap-4">
                <div className={`w-10 h-10 rounded-xl ${iconBg} flex items-center justify-center flex-shrink-0`}>
                  {result.status === 'MET' || result.status === 'CLEAR' ? (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : result.status === 'NOT_MET' || result.status === 'EXCLUDES' ? (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-3 flex-wrap">
                    <p className="font-medium text-gray-900">{result.criterion_text}</p>
                    <StatusBadge status={result.status} />
                  </div>
                  <div className="mt-2 flex flex-wrap gap-4 text-sm">
                    {result.actual_value !== undefined && result.actual_value !== null && (
                      <div className="bg-gray-100 px-3 py-1 rounded-lg">
                        <span className="text-gray-500">ערך: </span>
                        <span className="font-medium text-gray-700">
                          {Array.isArray(result.actual_value)
                            ? result.actual_value.join(', ')
                            : String(result.actual_value)}
                        </span>
                      </div>
                    )}
                    {result.reason && (
                      <div className="text-gray-500">
                        {result.reason}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default function ResultsDashboard({ result, onClear }: Props) {
  if (!result) {
    return (
      <div className="glass-card rounded-2xl p-12 text-center animate-fade-in">
        <div className="w-24 h-24 mx-auto rounded-3xl bg-sky-100 flex items-center justify-center mb-6">
          <svg className="w-12 h-12 text-sky-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
        </div>
        <h3 className="text-xl font-bold text-gray-900 mb-2">אין תוצאות סינון</h3>
        <p className="text-gray-500">
          בחר ניסוי קליני והזן פרטי מטופל כדי להתחיל בסינון
        </p>
      </div>
    );
  }

  const { trial_name, patient_id, result: eligibilityResult, screened_at } = result;
  const { decision, inclusion_results, exclusion_results, missing_data, ai_explanation, recommendation } = eligibilityResult;

  const handlePrint = () => {
    window.print();
  };

  const handleExport = () => {
    const exportData = {
      trial_name,
      patient_id,
      decision,
      screened_at,
      inclusion_results,
      exclusion_results,
      missing_data,
      ai_explanation,
      recommendation
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `screening-result-${patient_id}-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6 print:space-y-4">
      {/* Header with actions */}
      <div className="flex flex-wrap items-center justify-between gap-4 print:hidden">
        <h2 className="text-xl font-bold gradient-text">תוצאות סינון</h2>
        <div className="flex gap-2">
          <button
            onClick={handlePrint}
            className="inline-flex items-center px-4 py-2.5 rounded-xl text-sm font-medium text-gray-700 bg-white/80 backdrop-blur border border-gray-200 hover:bg-white hover:shadow-md transition-all duration-300"
          >
            <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
            </svg>
            הדפסה
          </button>
          <button
            onClick={handleExport}
            className="inline-flex items-center px-4 py-2.5 rounded-xl text-sm font-medium text-gray-700 bg-white/80 backdrop-blur border border-gray-200 hover:bg-white hover:shadow-md transition-all duration-300"
          >
            <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            ייצוא JSON
          </button>
          <button
            onClick={onClear}
            className="inline-flex items-center px-4 py-2.5 rounded-xl text-sm font-medium text-white bg-gray-600 hover:bg-gray-700 shadow-md hover:shadow-lg transition-all duration-300"
          >
            <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
            נקה
          </button>
        </div>
      </div>

      {/* Trial and patient info */}
      <div className="glass-card rounded-2xl p-5 print:shadow-none print:border animate-fade-in">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-sky-100 flex items-center justify-center">
              <svg className="w-5 h-5 text-sky-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
              </svg>
            </div>
            <div>
              <span className="text-xs text-gray-500 block">ניסוי קליני</span>
              <span className="font-semibold text-gray-900 text-sm">{trial_name}</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-purple-100 flex items-center justify-center">
              <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div>
              <span className="text-xs text-gray-500 block">מזהה מטופל</span>
              <span className="font-semibold text-gray-900 text-sm">{patient_id}</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center">
              <svg className="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <span className="text-xs text-gray-500 block">תאריך סינון</span>
              <span className="font-semibold text-gray-900 text-sm">
                {new Date(screened_at).toLocaleString('he-IL')}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Decision banner */}
      <DecisionBanner decision={decision} />

      {/* Missing data warning */}
      {missing_data && missing_data.length > 0 && (
        <div className="glass-card border border-amber-200 rounded-2xl p-5 animate-fade-in">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-amber-100 flex items-center justify-center flex-shrink-0">
              <svg className="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div>
              <h4 className="font-bold text-amber-800">מידע חסר</h4>
              <ul className="mt-2 space-y-1">
                {missing_data.map((field, index) => (
                  <li key={index} className="flex items-center gap-2 text-sm text-amber-700">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
                    {field}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* AI Explanation */}
      {ai_explanation && (
        <div className="glass-card border border-purple-200 rounded-2xl p-5 animate-fade-in ai-pulse">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-purple-100 flex items-center justify-center flex-shrink-0">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div>
              <h4 className="font-bold text-purple-800 flex items-center gap-2">
                הסבר AI
                <span className="text-xs bg-purple-100 text-purple-600 px-2 py-0.5 rounded-full">Gemini</span>
              </h4>
              <p className="mt-2 text-purple-700 leading-relaxed">{ai_explanation}</p>
            </div>
          </div>
        </div>
      )}

      {/* Recommendation */}
      {recommendation && (
        <div className="glass-card border border-sky-200 rounded-2xl p-5 animate-fade-in">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-sky-100 flex items-center justify-center flex-shrink-0">
              <svg className="w-6 h-6 text-sky-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
              </svg>
            </div>
            <div>
              <h4 className="font-bold text-sky-800">המלצה</h4>
              <p className="mt-2 text-sky-700 leading-relaxed">{recommendation}</p>
            </div>
          </div>
        </div>
      )}

      {/* Criteria tables */}
      <div className="grid grid-cols-1 gap-6 print:grid-cols-1">
        <CriteriaTable
          title="קריטריוני הכללה"
          results={inclusion_results}
          type="inclusion"
        />
        <CriteriaTable
          title="קריטריוני הדחה"
          results={exclusion_results}
          type="exclusion"
        />
      </div>

      {/* Summary stats */}
      <div className="glass-card rounded-2xl p-6 print:shadow-none print:border animate-fade-in">
        <h4 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
          <svg className="w-5 h-5 text-sky-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          סיכום סטטיסטי
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-emerald-50 to-green-100 rounded-2xl p-4 text-center">
            <div className="text-3xl font-bold text-emerald-600">
              {inclusion_results.filter(r => r.status === 'MET').length}
            </div>
            <div className="text-xs text-emerald-700 font-medium mt-1">הכללה מתקיימים</div>
          </div>
          <div className="bg-gradient-to-br from-red-50 to-rose-100 rounded-2xl p-4 text-center">
            <div className="text-3xl font-bold text-red-600">
              {inclusion_results.filter(r => r.status === 'NOT_MET').length}
            </div>
            <div className="text-xs text-red-700 font-medium mt-1">הכללה לא מתקיימים</div>
          </div>
          <div className="bg-gradient-to-br from-emerald-50 to-green-100 rounded-2xl p-4 text-center">
            <div className="text-3xl font-bold text-emerald-600">
              {exclusion_results.filter(r => r.status === 'CLEAR').length}
            </div>
            <div className="text-xs text-emerald-700 font-medium mt-1">הדחה - תקין</div>
          </div>
          <div className="bg-gradient-to-br from-amber-50 to-yellow-100 rounded-2xl p-4 text-center">
            <div className="text-3xl font-bold text-amber-600">
              {[...inclusion_results, ...exclusion_results].filter(r => r.status === 'UNKNOWN').length}
            </div>
            <div className="text-xs text-amber-700 font-medium mt-1">לא ידועים</div>
          </div>
        </div>
      </div>
    </div>
  );
}
