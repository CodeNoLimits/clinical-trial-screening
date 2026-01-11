import { useState, useRef, useCallback } from 'react';
import type { Patient, BatchScreeningResponse, BatchScreeningResult } from '../types';
import { batchScreen } from '../services/api';

interface Props {
  trialId: string;
  trialName: string;
}

type UploadStatus = 'idle' | 'preview' | 'processing' | 'complete' | 'error';

export default function BatchUpload({ trialId, trialName }: Props) {
  const [status, setStatus] = useState<UploadStatus>('idle');
  const [patients, setPatients] = useState<Patient[]>([]);
  const [results, setResults] = useState<BatchScreeningResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const parseCSV = (content: string): Patient[] => {
    const lines = content.trim().split('\n');
    if (lines.length < 2) {
      throw new Error('CSV must have a header row and at least one data row');
    }

    const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
    const patientIdIndex = headers.findIndex(h =>
      h === 'patient_id' || h === 'patientid' || h === 'id'
    );

    if (patientIdIndex === -1) {
      throw new Error('CSV must have a patient_id column');
    }

    const parsedPatients: Patient[] = [];

    for (let i = 1; i < lines.length; i++) {
      const values = parseCSVLine(lines[i]);
      if (values.length === 0 || values.every(v => !v.trim())) continue;

      const patient: Patient = {
        patient_id: values[patientIdIndex] || `P${i}`,
        current_medications: [],
        comorbidities: [],
      };

      headers.forEach((header, idx) => {
        const value = values[idx]?.trim();
        if (!value) return;

        switch (header) {
          case 'age':
            patient.age = parseInt(value) || undefined;
            break;
          case 'gender':
            patient.gender = value;
            break;
          case 'diagnosis':
            patient.diagnosis = value;
            break;
          case 'diagnosis_date':
            patient.diagnosis_date = value;
            break;
          case 'hba1c':
            patient.HbA1c = parseFloat(value) || undefined;
            break;
          case 'egfr':
            patient.eGFR = parseFloat(value) || undefined;
            break;
          case 'creatinine':
            patient.creatinine = parseFloat(value) || undefined;
            break;
          case 'current_medications':
          case 'medications':
            patient.current_medications = value.split(';').map(m => m.trim()).filter(Boolean);
            break;
          case 'comorbidities':
            patient.comorbidities = value.split(';').map(c => c.trim()).filter(Boolean);
            break;
          case 'pregnancy_status':
            patient.pregnancy_status = value;
            break;
          case 'clinical_notes':
          case 'notes':
            patient.clinical_notes = value;
            break;
        }
      });

      parsedPatients.push(patient);
    }

    return parsedPatients;
  };

  const parseCSVLine = (line: string): string[] => {
    const values: string[] = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      if (char === '"') {
        inQuotes = !inQuotes;
      } else if (char === ',' && !inQuotes) {
        values.push(current);
        current = '';
      } else {
        current += char;
      }
    }
    values.push(current);
    return values;
  };

  const parseJSON = (content: string): Patient[] => {
    const parsed = JSON.parse(content);
    if (Array.isArray(parsed)) {
      return parsed.map((p, idx) => ({
        patient_id: p.patient_id || `P${idx + 1}`,
        age: p.age,
        gender: p.gender,
        diagnosis: p.diagnosis,
        diagnosis_date: p.diagnosis_date,
        HbA1c: p.HbA1c,
        eGFR: p.eGFR,
        creatinine: p.creatinine,
        current_medications: p.current_medications || [],
        comorbidities: p.comorbidities || [],
        pregnancy_status: p.pregnancy_status,
        clinical_notes: p.clinical_notes,
      }));
    }
    throw new Error('JSON must be an array of patient objects');
  };

  const handleFileUpload = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setError(null);
    setFileName(file.name);

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string;
        let parsedPatients: Patient[];

        if (file.name.endsWith('.json')) {
          parsedPatients = parseJSON(content);
        } else if (file.name.endsWith('.csv')) {
          parsedPatients = parseCSV(content);
        } else {
          throw new Error('Unsupported file format. Please use CSV or JSON.');
        }

        if (parsedPatients.length === 0) {
          throw new Error('No valid patient data found in file');
        }

        setPatients(parsedPatients);
        setStatus('preview');
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to parse file');
        setStatus('error');
      }
    };

    reader.onerror = () => {
      setError('Failed to read file');
      setStatus('error');
    };

    reader.readAsText(file);
  }, []);

  const handleProcessBatch = async () => {
    if (patients.length === 0) return;

    setStatus('processing');
    setError(null);

    try {
      const response = await batchScreen(trialId, patients, false);
      setResults(response);
      setStatus('complete');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Batch processing failed');
      setStatus('error');
    }
  };

  const handleReset = () => {
    setStatus('idle');
    setPatients([]);
    setResults(null);
    setError(null);
    setFileName('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const exportToCSV = () => {
    if (!results) return;

    const headers = ['Patient ID', 'Decision', 'Summary'];
    const rows = results.results.map((r: BatchScreeningResult) => [
      `"${r.patient_id}"`,
      `"${r.decision}"`,
      `"${r.summary.replace(/"/g, '""')}"`,
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(',')),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `screening_results_${trialId}_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const getDecisionBadgeClass = (decision: string): string => {
    switch (decision.toUpperCase()) {
      case 'ELIGIBLE':
        return 'bg-green-100 text-green-800';
      case 'INELIGIBLE':
        return 'bg-red-100 text-red-800';
      case 'UNCERTAIN':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">Batch Patient Screening</h2>

      {/* File Upload Section */}
      {status === 'idle' && (
        <div className="space-y-4">
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors">
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv,.json"
              onChange={handleFileUpload}
              className="hidden"
              id="batch-file-input"
            />
            <label
              htmlFor="batch-file-input"
              className="cursor-pointer"
            >
              <div className="text-gray-500 mb-2">
                <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <p className="text-gray-600 font-medium">Click to upload CSV or JSON file</p>
              <p className="text-gray-400 text-sm mt-1">or drag and drop</p>
            </label>
          </div>

          <div className="bg-gray-50 rounded p-4 text-sm text-gray-600">
            <p className="font-medium mb-2">Expected CSV format:</p>
            <code className="text-xs bg-gray-200 p-2 rounded block overflow-x-auto">
              patient_id,age,gender,diagnosis,hba1c,egfr,medications,comorbidities
            </code>
            <p className="mt-2 text-xs">
              Use semicolons (;) to separate multiple medications or comorbidities within a cell.
            </p>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <div className="flex items-center gap-2 text-red-700">
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="font-medium">Error:</span>
            <span>{error}</span>
          </div>
          <button
            onClick={handleReset}
            className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
          >
            Try again
          </button>
        </div>
      )}

      {/* Preview Section */}
      {status === 'preview' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between bg-blue-50 rounded-lg p-4">
            <div>
              <p className="font-medium text-blue-800">File: {fileName}</p>
              <p className="text-blue-600 text-sm">{patients.length} patient(s) ready for screening</p>
            </div>
            <button
              onClick={handleReset}
              className="text-blue-600 hover:text-blue-800 text-sm underline"
            >
              Choose different file
            </button>
          </div>

          <div className="border rounded-lg overflow-hidden">
            <div className="bg-gray-50 px-4 py-2 border-b">
              <h3 className="font-medium text-gray-700">Patient Preview</h3>
            </div>
            <div className="max-h-64 overflow-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50 sticky top-0">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Age</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Gender</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Diagnosis</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">HbA1c</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">eGFR</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {patients.slice(0, 10).map((patient, idx) => (
                    <tr key={patient.patient_id || idx} className="hover:bg-gray-50">
                      <td className="px-4 py-2 text-sm text-gray-900">{patient.patient_id}</td>
                      <td className="px-4 py-2 text-sm text-gray-600">{patient.age || '-'}</td>
                      <td className="px-4 py-2 text-sm text-gray-600">{patient.gender || '-'}</td>
                      <td className="px-4 py-2 text-sm text-gray-600">{patient.diagnosis || '-'}</td>
                      <td className="px-4 py-2 text-sm text-gray-600">{patient.HbA1c || '-'}</td>
                      <td className="px-4 py-2 text-sm text-gray-600">{patient.eGFR || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {patients.length > 10 && (
                <div className="px-4 py-2 text-sm text-gray-500 bg-gray-50 border-t">
                  ... and {patients.length - 10} more patient(s)
                </div>
              )}
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleProcessBatch}
              className="flex-1 bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              Screen {patients.length} Patient(s) for {trialName}
            </button>
            <button
              onClick={handleReset}
              className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Processing Section */}
      {status === 'processing' && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 font-medium">Processing {patients.length} patient(s)...</p>
          <p className="text-gray-400 text-sm mt-1">This may take a moment</p>
        </div>
      )}

      {/* Results Section */}
      {status === 'complete' && results && (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-green-50 rounded-lg p-4 text-center">
              <p className="text-3xl font-bold text-green-600">{results.eligible_count}</p>
              <p className="text-green-700 font-medium">Eligible</p>
            </div>
            <div className="bg-red-50 rounded-lg p-4 text-center">
              <p className="text-3xl font-bold text-red-600">{results.ineligible_count}</p>
              <p className="text-red-700 font-medium">Ineligible</p>
            </div>
            <div className="bg-yellow-50 rounded-lg p-4 text-center">
              <p className="text-3xl font-bold text-yellow-600">{results.uncertain_count}</p>
              <p className="text-yellow-700 font-medium">Uncertain</p>
            </div>
          </div>

          {/* Results Table */}
          <div className="border rounded-lg overflow-hidden">
            <div className="bg-gray-50 px-4 py-2 border-b flex items-center justify-between">
              <h3 className="font-medium text-gray-700">
                Screening Results ({results.total_patients} patients)
              </h3>
              <button
                onClick={exportToCSV}
                className="flex items-center gap-2 px-3 py-1 bg-white border border-gray-300 rounded text-sm text-gray-700 hover:bg-gray-50 transition-colors"
              >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Export CSV
              </button>
            </div>
            <div className="max-h-96 overflow-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50 sticky top-0">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Patient ID</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Decision</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Summary</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {results.results.map((result: BatchScreeningResult, idx: number) => (
                    <tr key={result.patient_id || idx} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm font-medium text-gray-900">
                        {result.patient_id}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getDecisionBadgeClass(result.decision)}`}>
                          {result.decision}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {result.summary}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              onClick={exportToCSV}
              className="flex-1 bg-green-600 text-white py-3 rounded-lg font-medium hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download Results (CSV)
            </button>
            <button
              onClick={handleReset}
              className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              New Batch
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
