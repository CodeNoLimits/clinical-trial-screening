import { useState, useEffect } from 'react';
import type { Patient } from '../types';
import { getSamplePatients } from '../services/api';

interface Props {
  onSubmit: (patient: Patient) => void;
  loading: boolean;
}

const emptyPatient: Patient = {
  patient_id: '',
  age: undefined,
  gender: '',
  diagnosis: '',
  diagnosis_date: '',
  HbA1c: undefined,
  eGFR: undefined,
  creatinine: undefined,
  current_medications: [],
  comorbidities: [],
  pregnancy_status: '',
  clinical_notes: '',
};

export default function PatientForm({ onSubmit, loading }: Props) {
  const [patient, setPatient] = useState<Patient>(emptyPatient);
  const [medications, setMedications] = useState('');
  const [comorbidities, setComorbidities] = useState('');
  const [samplePatients, setSamplePatients] = useState<Patient[]>([]);
  const [jsonMode, setJsonMode] = useState(false);
  const [jsonInput, setJsonInput] = useState('');
  const [jsonError, setJsonError] = useState<string | null>(null);

  useEffect(() => {
    loadSamplePatients();
  }, []);

  const loadSamplePatients = async () => {
    try {
      const patients = await getSamplePatients();
      setSamplePatients(patients);
    } catch (err) {
      console.error('Failed to load sample patients:', err);
    }
  };

  const handleChange = (field: keyof Patient, value: any) => {
    setPatient(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (jsonMode) {
      try {
        const parsed = JSON.parse(jsonInput);
        setJsonError(null);
        onSubmit(parsed);
      } catch {
        setJsonError('JSON invalid');
        return;
      }
    } else {
      const patientData: Patient = {
        ...patient,
        current_medications: medications.split(',').map(m => m.trim()).filter(Boolean),
        comorbidities: comorbidities.split(',').map(c => c.trim()).filter(Boolean),
      };
      onSubmit(patientData);
    }
  };

  const loadSample = (samplePatient: Patient) => {
    setPatient(samplePatient);
    setMedications(samplePatient.current_medications.join(', '));
    setComorbidities(samplePatient.comorbidities.join(', '));
    setJsonInput(JSON.stringify(samplePatient, null, 2));
  };

  return (
    <div className="glass-card rounded-2xl shadow-card p-6 animate-fade-in">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          <div className="bg-sky-100 rounded-xl p-2">
            <svg className="w-5 h-5 text-sky-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <h2 className="text-lg font-bold text-gray-800">Patient Data</h2>
        </div>
        <div className="flex gap-1 bg-gray-100 p-1 rounded-xl">
          <button
            type="button"
            onClick={() => setJsonMode(false)}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${!jsonMode ? 'bg-white text-sky-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
          >
            Form
          </button>
          <button
            type="button"
            onClick={() => setJsonMode(true)}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${jsonMode ? 'bg-white text-sky-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
          >
            JSON
          </button>
        </div>
      </div>

      {samplePatients.length > 0 && (
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Load Sample Patient
          </label>
          <select
            className="w-full border border-gray-300 rounded p-2 text-sm"
            onChange={(e) => {
              const p = samplePatients.find(sp => sp.patient_id === e.target.value);
              if (p) loadSample(p);
            }}
            value=""
          >
            <option value="">-- Select Patient --</option>
            {samplePatients.map(p => (
              <option key={p.patient_id} value={p.patient_id}>
                {p.patient_id} - Age {p.age}, {p.diagnosis}
              </option>
            ))}
          </select>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {jsonMode ? (
          <div>
            <textarea
              className="w-full border border-gray-300 rounded p-3 font-mono text-sm h-64"
              value={jsonInput}
              onChange={(e) => setJsonInput(e.target.value)}
              placeholder='{"patient_id": "P001", "age": 52, ...}'
              dir="ltr"
            />
            {jsonError && (
              <p className="text-red-500 text-sm mt-1">{jsonError}</p>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Patient ID *
                </label>
                <input
                  type="text"
                  required
                  className="w-full border border-gray-300 rounded p-2"
                  value={patient.patient_id}
                  onChange={(e) => handleChange('patient_id', e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Age
                </label>
                <input
                  type="number"
                  className="w-full border border-gray-300 rounded p-2"
                  value={patient.age || ''}
                  onChange={(e) => handleChange('age', e.target.value ? parseInt(e.target.value) : undefined)}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Gender
                </label>
                <select
                  className="w-full border border-gray-300 rounded p-2"
                  value={patient.gender || ''}
                  onChange={(e) => handleChange('gender', e.target.value)}
                >
                  <option value="">Not specified</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Diagnosis
                </label>
                <input
                  type="text"
                  className="w-full border border-gray-300 rounded p-2"
                  value={patient.diagnosis || ''}
                  onChange={(e) => handleChange('diagnosis', e.target.value)}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  HbA1c (%)
                </label>
                <input
                  type="number"
                  step="0.1"
                  className="w-full border border-gray-300 rounded p-2"
                  value={patient.HbA1c || ''}
                  onChange={(e) => handleChange('HbA1c', e.target.value ? parseFloat(e.target.value) : undefined)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  eGFR (ml/min)
                </label>
                <input
                  type="number"
                  className="w-full border border-gray-300 rounded p-2"
                  value={patient.eGFR || ''}
                  onChange={(e) => handleChange('eGFR', e.target.value ? parseFloat(e.target.value) : undefined)}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Current Medications (comma-separated)
              </label>
              <input
                type="text"
                className="w-full border border-gray-300 rounded p-2"
                value={medications}
                onChange={(e) => setMedications(e.target.value)}
                placeholder="Metformin 1000mg, Amlodipine 5mg"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Comorbidities (comma-separated)
              </label>
              <input
                type="text"
                className="w-full border border-gray-300 rounded p-2"
                value={comorbidities}
                onChange={(e) => setComorbidities(e.target.value)}
                placeholder="Hypertension, Hyperlipidemia"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Pregnancy Status
              </label>
              <select
                className="w-full border border-gray-300 rounded p-2"
                value={patient.pregnancy_status || ''}
                onChange={(e) => handleChange('pregnancy_status', e.target.value || undefined)}
              >
                <option value="">Not applicable</option>
                <option value="Pregnant">Pregnant</option>
                <option value="Nursing">Nursing</option>
                <option value="Not pregnant">Not pregnant</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Clinical Notes
              </label>
              <textarea
                className="w-full border border-gray-300 rounded p-2"
                rows={2}
                value={patient.clinical_notes || ''}
                onChange={(e) => handleChange('clinical_notes', e.target.value)}
              />
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="mt-6 w-full btn-primary py-4 rounded-xl font-semibold text-base flex items-center justify-center gap-3"
        >
          {loading ? (
            <>
              <span className="spinner"></span>
              <span>Analyzing with AI...</span>
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>Check Eligibility</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}
