import { useState, useEffect } from 'react';
import type { TrialListItem, Trial } from '../types';
import { getTrials, getTrial } from '../services/api';

interface Props {
  onTrialSelect: (trial: Trial | null) => void;
  selectedTrial: Trial | null;
}

export default function TrialSelector({ onTrialSelect, selectedTrial }: Props) {
  const [trials, setTrials] = useState<TrialListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTrials();
  }, []);

  const loadTrials = async () => {
    try {
      setLoading(true);
      const data = await getTrials();
      setTrials(data);
    } catch (err) {
      setError('Failed to load trials');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = async (trialId: string) => {
    if (!trialId) {
      onTrialSelect(null);
      return;
    }
    try {
      const trial = await getTrial(trialId);
      onTrialSelect(trial);
    } catch (err) {
      setError('Failed to load trial details');
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-10 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">בחירת ניסוי קליני</h2>
      
      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded mb-4">
          {error}
        </div>
      )}
      
      <select
        className="w-full border border-gray-300 rounded-lg p-3 text-gray-700 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        value={selectedTrial?.id || ''}
        onChange={(e) => handleSelect(e.target.value)}
      >
        <option value="">-- בחר ניסוי --</option>
        {trials.map((trial) => (
          <option key={trial.id} value={trial.id}>
            {trial.name} ({trial.phase})
          </option>
        ))}
      </select>

      {selectedTrial && (
        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-medium text-blue-900">{selectedTrial.name}</h3>
          <p className="text-sm text-blue-700 mt-1">
            {selectedTrial.phase} | {selectedTrial.sponsor}
          </p>
          <div className="mt-3 grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium text-green-700">קריטריוני הכללה:</span>
              <span className="mr-2 text-gray-600">
                {selectedTrial.inclusion_criteria.length}
              </span>
            </div>
            <div>
              <span className="font-medium text-red-700">קריטריוני הדחה:</span>
              <span className="mr-2 text-gray-600">
                {selectedTrial.exclusion_criteria.length}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
