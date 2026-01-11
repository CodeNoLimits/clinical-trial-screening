"""
SQLAlchemy models for Clinical Trial Screening
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Boolean
from .database import Base


class Trial(Base):
    """Clinical Trial model"""
    __tablename__ = "trials"
    
    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(500), nullable=False)
    phase = Column(String(50), nullable=False)
    sponsor = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    inclusion_criteria = Column(JSON, nullable=False, default=list)
    exclusion_criteria = Column(JSON, nullable=False, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Patient(Base):
    """Patient model for screening"""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), unique=True, index=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    diagnosis = Column(String(200), nullable=True)
    diagnosis_date = Column(String(50), nullable=True)
    hba1c = Column(Float, nullable=True)
    egfr = Column(Float, nullable=True)
    creatinine = Column(Float, nullable=True)
    current_medications = Column(JSON, default=list)
    comorbidities = Column(JSON, default=list)
    pregnancy_status = Column(String(50), nullable=True)
    clinical_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ScreeningResult(Base):
    """Audit trail for screening results"""
    __tablename__ = "screening_results"
    
    id = Column(Integer, primary_key=True, index=True)
    trial_id = Column(String(50), nullable=False, index=True)
    patient_id = Column(String(50), nullable=False, index=True)
    decision = Column(String(20), nullable=False)  # ELIGIBLE, INELIGIBLE, UNCERTAIN
    inclusion_results = Column(JSON, nullable=False)
    exclusion_results = Column(JSON, nullable=False)
    ai_explanation = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    missing_data = Column(JSON, default=list)
    screened_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
