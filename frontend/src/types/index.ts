// Trial types
export interface CriterionBase {
  id: string;
  text: string;
  field: string;
  min?: number;
  max?: number;
  value?: string;
  contains?: string | string[];
  excludes?: string[];
}

export interface Trial {
  id: string;
  name: string;
  phase: string;
  sponsor: string;
  description?: string;
  inclusion_criteria: CriterionBase[];
  exclusion_criteria: CriterionBase[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TrialListItem {
  id: string;
  name: string;
  phase: string;
  sponsor: string;
  is_active: boolean;
}

// Patient types
export interface Patient {
  patient_id: string;
  age?: number;
  gender?: string;
  diagnosis?: string;
  diagnosis_date?: string;
  HbA1c?: number;
  eGFR?: number;
  creatinine?: number;
  current_medications: string[];
  comorbidities: string[];
  pregnancy_status?: string;
  clinical_notes?: string;
}

// Screening types
export interface CriterionResult {
  criterion_id: string;
  criterion_text: string;
  status: 'MET' | 'NOT_MET' | 'EXCLUDES' | 'CLEAR' | 'UNKNOWN';
  actual_value?: any;
  reason?: string;
}

export interface EligibilityResult {
  decision: 'ELIGIBLE' | 'INELIGIBLE' | 'UNCERTAIN';
  inclusion_results: CriterionResult[];
  exclusion_results: CriterionResult[];
  missing_data: string[];
  ai_explanation?: string;
  recommendation?: string;
}

export interface ScreeningResponse {
  trial_id: string;
  trial_name: string;
  patient_id: string;
  result: EligibilityResult;
  screened_at: string;
}

export interface BatchScreeningResult {
  patient_id: string;
  decision: string;
  summary: string;
}

export interface BatchScreeningResponse {
  trial_id: string;
  total_patients: number;
  eligible_count: number;
  ineligible_count: number;
  uncertain_count: number;
  results: BatchScreeningResult[];
}
