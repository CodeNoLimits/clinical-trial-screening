"""
Patients router - Patient management
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Patient
from ..schemas import PatientCreate, PatientResponse

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/", response_model=List[PatientResponse])
def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get list of patients with pagination"""
    patients = db.query(Patient).offset(skip).limit(limit).all()
    return patients


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    """Get a specific patient by ID"""
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.post("/", response_model=PatientResponse)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """Create or update a patient"""
    # Check if patient exists
    existing = db.query(Patient).filter(Patient.patient_id == patient.patient_id).first()
    
    if existing:
        # Update existing patient
        existing.age = patient.age
        existing.gender = patient.gender
        existing.diagnosis = patient.diagnosis
        existing.diagnosis_date = patient.diagnosis_date
        existing.hba1c = patient.HbA1c
        existing.egfr = patient.eGFR
        existing.creatinine = patient.creatinine
        existing.current_medications = patient.current_medications
        existing.comorbidities = patient.comorbidities
        existing.pregnancy_status = patient.pregnancy_status
        existing.clinical_notes = patient.clinical_notes
        
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new patient
    db_patient = Patient(
        patient_id=patient.patient_id,
        age=patient.age,
        gender=patient.gender,
        diagnosis=patient.diagnosis,
        diagnosis_date=patient.diagnosis_date,
        hba1c=patient.HbA1c,
        egfr=patient.eGFR,
        creatinine=patient.creatinine,
        current_medications=patient.current_medications,
        comorbidities=patient.comorbidities,
        pregnancy_status=patient.pregnancy_status,
        clinical_notes=patient.clinical_notes,
    )
    
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@router.delete("/{patient_id}")
def delete_patient(patient_id: str, db: Session = Depends(get_db)):
    """Delete a patient"""
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    db.delete(patient)
    db.commit()
    return {"message": "Patient deleted successfully"}
