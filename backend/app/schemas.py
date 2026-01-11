"""
Pydantic schemas for request/response validation
"""
from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field


# ============== Criterion Schemas ==============

class CriterionBase(BaseModel):
    """Base schema for trial criteria"""
    id: str
    text: str
    field: str
    
    # Numeric range conditions
    min: Optional[float] = None
    max: Optional[float] = None
    
    # Exact value condition
    value: Optional[str] = None
    
    # Array contains conditions
    contains: Optional[Any] = None  # Can be string or list
    excludes: Optional[List[str]] = None


class CriterionResult(BaseModel):
    """Result of evaluating a single criterion"""
    criterion_id: str
    criterion_text: str
    status: str  # MET, NOT_MET, EXCLUDES, CLEAR, UNKNOWN
    actual_value: Optional[Any] = None
    reason: Optional[str] = None


# ============== Trial Schemas ==============

class TrialBase(BaseModel):
    """Base trial schema"""
    name: str
    phase: str
    sponsor: str
    description: Optional[str] = None
    inclusion_criteria: List[CriterionBase]
    exclusion_criteria: List[CriterionBase]


class TrialCreate(TrialBase):
    """Schema for creating a trial"""
    id: str


class TrialResponse(TrialBase):
    """Schema for trial response"""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TrialListItem(BaseModel):
    """Summary for trial list"""
    id: str
    name: str
    phase: str
    sponsor: str
    is_active: bool


# ============== Patient Schemas ==============

class PatientBase(BaseModel):
    """Base patient schema"""
    patient_id: str
    age: Optional[int] = None
    gender: Optional[str] = None
    diagnosis: Optional[str] = None
    diagnosis_date: Optional[str] = None
    HbA1c: Optional[float] = Field(None, alias="hba1c")
    eGFR: Optional[float] = Field(None, alias="egfr")
    creatinine: Optional[float] = None
    current_medications: List[str] = []
    comorbidities: List[str] = []
    pregnancy_status: Optional[str] = None
    clinical_notes: Optional[str] = None
    
    class Config:
        populate_by_name = True


class PatientCreate(PatientBase):
    """Schema for creating a patient"""
    pass


class PatientResponse(PatientBase):
    """Schema for patient response"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== Screening Schemas ==============

class ScreeningRequest(BaseModel):
    """Request to screen a patient"""
    trial_id: str
    patient: PatientBase
    generate_ai_explanation: bool = True


class EligibilityResult(BaseModel):
    """Result of eligibility evaluation"""
    decision: str  # ELIGIBLE, INELIGIBLE, UNCERTAIN
    inclusion_results: List[CriterionResult]
    exclusion_results: List[CriterionResult]
    missing_data: List[str] = []
    ai_explanation: Optional[str] = None
    recommendation: Optional[str] = None


class ScreeningResponse(BaseModel):
    """Full screening response"""
    trial_id: str
    trial_name: str
    patient_id: str
    result: EligibilityResult
    screened_at: datetime


class BatchPatient(BaseModel):
    """Patient data for batch processing"""
    patient_id: str
    age: Optional[int] = None
    gender: Optional[str] = None
    diagnosis: Optional[str] = None
    HbA1c: Optional[float] = None
    eGFR: Optional[float] = None
    current_medications: List[str] = []
    comorbidities: List[str] = []
    pregnancy_status: Optional[str] = None


class BatchScreeningRequest(BaseModel):
    """Request for batch screening"""
    trial_id: str
    patients: List[BatchPatient]
    generate_ai_explanation: bool = False


class BatchScreeningResult(BaseModel):
    """Single result in batch"""
    patient_id: str
    decision: str
    summary: str


class BatchScreeningResponse(BaseModel):
    """Response for batch screening"""
    trial_id: str
    total_patients: int
    eligible_count: int
    ineligible_count: int
    uncertain_count: int
    results: List[BatchScreeningResult]


# ============== Audit Schemas ==============

class AuditRecord(BaseModel):
    """Audit trail record"""
    id: int
    trial_id: str
    patient_id: str
    decision: str
    ai_explanation: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
