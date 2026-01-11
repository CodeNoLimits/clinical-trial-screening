"""
Screening router - Core eligibility screening endpoints
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Trial, ScreeningResult
from ..schemas import (
    ScreeningRequest, ScreeningResponse, 
    BatchScreeningRequest, BatchScreeningResponse, BatchScreeningResult,
    AuditRecord, PatientBase
)
from ..eligibility_engine import eligibility_engine
from ..gemini_client import gemini_client

router = APIRouter(prefix="/screening", tags=["screening"])


@router.post("/", response_model=ScreeningResponse)
async def screen_patient(
    request: ScreeningRequest,
    db: Session = Depends(get_db)
):
    """
    Screen a single patient for trial eligibility.
    
    This is the main screening endpoint that:
    1. Validates the patient data
    2. Runs rule-based eligibility evaluation
    3. Generates AI explanation (optional)
    4. Stores result in audit trail
    """
    # Get trial
    trial = db.query(Trial).filter(Trial.id == request.trial_id).first()
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    # Run eligibility evaluation
    result = eligibility_engine.evaluate(
        patient=request.patient,
        inclusion_criteria=trial.inclusion_criteria,
        exclusion_criteria=trial.exclusion_criteria
    )
    
    # Generate AI explanation if requested
    if request.generate_ai_explanation:
        explanation, recommendation = await gemini_client.generate_explanation(
            patient=request.patient,
            result=result,
            trial_name=trial.name
        )
        result.ai_explanation = explanation
        result.recommendation = recommendation
    
    # Store in audit trail
    audit_record = ScreeningResult(
        trial_id=trial.id,
        patient_id=request.patient.patient_id,
        decision=result.decision,
        inclusion_results=[r.model_dump() for r in result.inclusion_results],
        exclusion_results=[r.model_dump() for r in result.exclusion_results],
        ai_explanation=result.ai_explanation,
        recommendation=result.recommendation,
        missing_data=result.missing_data
    )
    db.add(audit_record)
    db.commit()
    
    return ScreeningResponse(
        trial_id=trial.id,
        trial_name=trial.name,
        patient_id=request.patient.patient_id,
        result=result,
        screened_at=datetime.utcnow()
    )


@router.post("/batch", response_model=BatchScreeningResponse)
async def batch_screen(
    request: BatchScreeningRequest,
    db: Session = Depends(get_db)
):
    """
    Screen multiple patients at once.
    
    For batch processing, AI explanations are disabled by default
    to improve performance.
    """
    # Get trial
    trial = db.query(Trial).filter(Trial.id == request.trial_id).first()
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    results = []
    eligible_count = 0
    ineligible_count = 0
    uncertain_count = 0
    
    for patient_data in request.patients:
        # Convert BatchPatient to PatientBase
        patient = PatientBase(
            patient_id=patient_data.patient_id,
            age=patient_data.age,
            gender=patient_data.gender,
            diagnosis=patient_data.diagnosis,
            HbA1c=patient_data.HbA1c,
            eGFR=patient_data.eGFR,
            current_medications=patient_data.current_medications,
            comorbidities=patient_data.comorbidities,
            pregnancy_status=patient_data.pregnancy_status
        )
        
        # Run eligibility evaluation
        result = eligibility_engine.evaluate(
            patient=patient,
            inclusion_criteria=trial.inclusion_criteria,
            exclusion_criteria=trial.exclusion_criteria
        )
        
        # Optional AI explanation for batch
        explanation = None
        recommendation = None
        if request.generate_ai_explanation:
            explanation, recommendation = await gemini_client.generate_explanation(
                patient=patient,
                result=result,
                trial_name=trial.name
            )
            result.ai_explanation = explanation
            result.recommendation = recommendation
        
        # Store in audit trail
        audit_record = ScreeningResult(
            trial_id=trial.id,
            patient_id=patient.patient_id,
            decision=result.decision,
            inclusion_results=[r.model_dump() for r in result.inclusion_results],
            exclusion_results=[r.model_dump() for r in result.exclusion_results],
            ai_explanation=result.ai_explanation,
            missing_data=result.missing_data
        )
        db.add(audit_record)
        
        # Count decisions
        if result.decision == "ELIGIBLE":
            eligible_count += 1
        elif result.decision == "INELIGIBLE":
            ineligible_count += 1
        else:
            uncertain_count += 1
        
        # Build summary
        summary_parts = []
        not_met = [r for r in result.inclusion_results if r.status == "NOT_MET"]
        excludes = [r for r in result.exclusion_results if r.status == "EXCLUDES"]
        
        if not_met:
            summary_parts.append(f"לא עמד ב: {', '.join(r.criterion_id for r in not_met)}")
        if excludes:
            summary_parts.append(f"נפסל ע\"י: {', '.join(r.criterion_id for r in excludes)}")
        if result.missing_data:
            summary_parts.append(f"נתונים חסרים: {len(result.missing_data)}")
        
        if result.decision == "ELIGIBLE":
            summary = "עומד בכל הקריטריונים"
        else:
            summary = "; ".join(summary_parts) if summary_parts else result.decision
        
        results.append(BatchScreeningResult(
            patient_id=patient.patient_id,
            decision=result.decision,
            summary=summary
        ))
    
    db.commit()
    
    return BatchScreeningResponse(
        trial_id=trial.id,
        total_patients=len(request.patients),
        eligible_count=eligible_count,
        ineligible_count=ineligible_count,
        uncertain_count=uncertain_count,
        results=results
    )


@router.get("/history", response_model=List[AuditRecord])
def get_screening_history(
    trial_id: str = None,
    patient_id: str = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get screening audit trail"""
    query = db.query(ScreeningResult)
    
    if trial_id:
        query = query.filter(ScreeningResult.trial_id == trial_id)
    if patient_id:
        query = query.filter(ScreeningResult.patient_id == patient_id)
    
    records = query.order_by(ScreeningResult.created_at.desc()).limit(limit).all()
    return records


@router.get("/history/{record_id}", response_model=AuditRecord)
def get_screening_record(record_id: int, db: Session = Depends(get_db)):
    """Get a specific screening record"""
    record = db.query(ScreeningResult).filter(ScreeningResult.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record
