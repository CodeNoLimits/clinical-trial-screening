import axios from 'axios';
import type {
  TrialListItem,
  Trial,
  Patient,
  ScreeningResponse,
  BatchScreeningResponse
} from '../types';

// Use environment variable for production, fallback to relative path for dev
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Trials
export const getTrials = async (): Promise<TrialListItem[]> => {
  const response = await api.get('/trials/');
  return response.data;
};

export const getTrial = async (id: string): Promise<Trial> => {
  const response = await api.get(`/trials/${id}`);
  return response.data;
};

// Screening
export const screenPatient = async (
  trialId: string,
  patient: Patient,
  generateAI: boolean = true
): Promise<ScreeningResponse> => {
  const response = await api.post('/screening/', {
    trial_id: trialId,
    patient: patient,
    generate_ai_explanation: generateAI,
  });
  return response.data;
};

export const batchScreen = async (
  trialId: string,
  patients: Patient[],
  generateAI: boolean = false
): Promise<BatchScreeningResponse> => {
  const response = await api.post('/screening/batch', {
    trial_id: trialId,
    patients: patients,
    generate_ai_explanation: generateAI,
  });
  return response.data;
};

// Sample data
export const getSamplePatients = async (): Promise<Patient[]> => {
  const response = await api.get('/sample-patients');
  return response.data;
};
