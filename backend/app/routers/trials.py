"""
Trials router - CRUD operations for clinical trials
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Trial
from ..schemas import TrialCreate, TrialResponse, TrialListItem

router = APIRouter(prefix="/trials", tags=["trials"])


@router.get("/", response_model=List[TrialListItem])
def list_trials(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get list of all trials"""
    query = db.query(Trial)
    if active_only:
        query = query.filter(Trial.is_active == True)
    trials = query.all()
    return trials


@router.get("/{trial_id}", response_model=TrialResponse)
def get_trial(trial_id: str, db: Session = Depends(get_db)):
    """Get a specific trial by ID"""
    trial = db.query(Trial).filter(Trial.id == trial_id).first()
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    return trial


@router.post("/", response_model=TrialResponse)
def create_trial(trial: TrialCreate, db: Session = Depends(get_db)):
    """Create a new trial"""
    # Check if trial already exists
    existing = db.query(Trial).filter(Trial.id == trial.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Trial with this ID already exists")
    
    # Convert criteria to dict for JSON storage
    db_trial = Trial(
        id=trial.id,
        name=trial.name,
        phase=trial.phase,
        sponsor=trial.sponsor,
        description=trial.description,
        inclusion_criteria=[c.model_dump() for c in trial.inclusion_criteria],
        exclusion_criteria=[c.model_dump() for c in trial.exclusion_criteria],
    )
    
    db.add(db_trial)
    db.commit()
    db.refresh(db_trial)
    return db_trial


@router.put("/{trial_id}", response_model=TrialResponse)
def update_trial(
    trial_id: str,
    trial: TrialCreate,
    db: Session = Depends(get_db)
):
    """Update an existing trial"""
    db_trial = db.query(Trial).filter(Trial.id == trial_id).first()
    if not db_trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    db_trial.name = trial.name
    db_trial.phase = trial.phase
    db_trial.sponsor = trial.sponsor
    db_trial.description = trial.description
    db_trial.inclusion_criteria = [c.model_dump() for c in trial.inclusion_criteria]
    db_trial.exclusion_criteria = [c.model_dump() for c in trial.exclusion_criteria]
    
    db.commit()
    db.refresh(db_trial)
    return db_trial


@router.delete("/{trial_id}")
def delete_trial(trial_id: str, db: Session = Depends(get_db)):
    """Delete (deactivate) a trial"""
    db_trial = db.query(Trial).filter(Trial.id == trial_id).first()
    if not db_trial:
        raise HTTPException(status_code=404, detail="Trial not found")
    
    db_trial.is_active = False
    db.commit()
    return {"message": "Trial deactivated successfully"}
