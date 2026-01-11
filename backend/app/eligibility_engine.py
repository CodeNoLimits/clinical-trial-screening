"""
Core Eligibility Engine - Rule-based evaluation logic
"""
from typing import List, Optional, Any
from .schemas import (
    PatientBase, CriterionBase, CriterionResult, EligibilityResult
)


class EligibilityEngine:
    """
    Rule-based engine for evaluating patient eligibility
    against clinical trial criteria.
    """
    
    def evaluate(
        self,
        patient: PatientBase,
        inclusion_criteria: List[dict],
        exclusion_criteria: List[dict]
    ) -> EligibilityResult:
        """
        Evaluate a patient against trial criteria.
        
        Returns:
            EligibilityResult with decision and detailed results
        """
        # Convert dict criteria to CriterionBase objects
        inclusion = [CriterionBase(**c) for c in inclusion_criteria]
        exclusion = [CriterionBase(**c) for c in exclusion_criteria]
        
        # Evaluate each inclusion criterion
        inclusion_results = []
        for criterion in inclusion:
            result = self._check_inclusion(patient, criterion)
            inclusion_results.append(result)
        
        # Evaluate each exclusion criterion
        exclusion_results = []
        for criterion in exclusion:
            result = self._check_exclusion(patient, criterion)
            exclusion_results.append(result)
        
        # Collect missing data
        missing_data = self._find_missing_data(
            patient, inclusion_results, exclusion_results
        )
        
        # Determine final decision
        decision = self._determine_decision(inclusion_results, exclusion_results)
        
        return EligibilityResult(
            decision=decision,
            inclusion_results=inclusion_results,
            exclusion_results=exclusion_results,
            missing_data=missing_data
        )
    
    def _get_patient_value(self, patient: PatientBase, field: str) -> Any:
        """Get value from patient by field name, handling aliases"""
        # Handle case-insensitive field names
        field_lower = field.lower()
        
        field_mapping = {
            "age": patient.age,
            "gender": patient.gender,
            "diagnosis": patient.diagnosis,
            "diagnosis_date": patient.diagnosis_date,
            "hba1c": patient.HbA1c,
            "egfr": patient.eGFR,
            "creatinine": patient.creatinine,
            "current_medications": patient.current_medications,
            "comorbidities": patient.comorbidities,
            "pregnancy_status": patient.pregnancy_status,
            "clinical_notes": patient.clinical_notes,
        }
        
        return field_mapping.get(field_lower)
    
    def _check_inclusion(
        self,
        patient: PatientBase,
        criterion: CriterionBase
    ) -> CriterionResult:
        """
        Check if patient meets an inclusion criterion.
        
        Returns:
            CriterionResult with status: MET, NOT_MET, or UNKNOWN
        """
        value = self._get_patient_value(patient, criterion.field)
        
        # If value is missing
        if value is None:
            return CriterionResult(
                criterion_id=criterion.id,
                criterion_text=criterion.text,
                status="UNKNOWN",
                actual_value=None,
                reason="נתון חסר"
            )
        
        # Check numeric range (min/max)
        if criterion.min is not None or criterion.max is not None:
            try:
                numeric_value = float(value)
                
                if criterion.min is not None and numeric_value < criterion.min:
                    return CriterionResult(
                        criterion_id=criterion.id,
                        criterion_text=criterion.text,
                        status="NOT_MET",
                        actual_value=numeric_value,
                        reason=f"הערך {numeric_value} נמוך מהמינימום {criterion.min}"
                    )
                
                if criterion.max is not None and numeric_value > criterion.max:
                    return CriterionResult(
                        criterion_id=criterion.id,
                        criterion_text=criterion.text,
                        status="NOT_MET",
                        actual_value=numeric_value,
                        reason=f"הערך {numeric_value} גבוה מהמקסימום {criterion.max}"
                    )
                
                return CriterionResult(
                    criterion_id=criterion.id,
                    criterion_text=criterion.text,
                    status="MET",
                    actual_value=numeric_value,
                    reason="הערך בטווח המותר"
                )
            except (ValueError, TypeError):
                return CriterionResult(
                    criterion_id=criterion.id,
                    criterion_text=criterion.text,
                    status="UNKNOWN",
                    actual_value=value,
                    reason="לא ניתן להמיר לערך מספרי"
                )
        
        # Check exact value match
        if criterion.value is not None:
            if str(value).strip() == str(criterion.value).strip():
                return CriterionResult(
                    criterion_id=criterion.id,
                    criterion_text=criterion.text,
                    status="MET",
                    actual_value=value,
                    reason="התאמה מדויקת"
                )
            else:
                return CriterionResult(
                    criterion_id=criterion.id,
                    criterion_text=criterion.text,
                    status="NOT_MET",
                    actual_value=value,
                    reason=f"הערך '{value}' לא תואם '{criterion.value}'"
                )
        
        # Check array contains (for inclusion, the patient should have the value)
        if criterion.contains is not None:
            if isinstance(value, list):
                contains_list = criterion.contains if isinstance(criterion.contains, list) else [criterion.contains]
                for item in contains_list:
                    if any(item.lower() in str(v).lower() for v in value):
                        return CriterionResult(
                            criterion_id=criterion.id,
                            criterion_text=criterion.text,
                            status="MET",
                            actual_value=value,
                            reason=f"נמצא: {item}"
                        )
                return CriterionResult(
                    criterion_id=criterion.id,
                    criterion_text=criterion.text,
                    status="NOT_MET",
                    actual_value=value,
                    reason="לא נמצא ברשימה"
                )
        
        # Default: if we have a value but no specific check, assume met
        return CriterionResult(
            criterion_id=criterion.id,
            criterion_text=criterion.text,
            status="MET",
            actual_value=value,
            reason="נתון קיים"
        )
    
    def _check_exclusion(
        self,
        patient: PatientBase,
        criterion: CriterionBase
    ) -> CriterionResult:
        """
        Check if patient triggers an exclusion criterion.
        
        Returns:
            CriterionResult with status: CLEAR, EXCLUDES, or UNKNOWN
        """
        value = self._get_patient_value(patient, criterion.field)
        
        # If value is missing for exclusion, it's potentially UNKNOWN
        if value is None:
            # For pregnancy status, None might mean "not pregnant"
            if criterion.field.lower() == "pregnancy_status":
                return CriterionResult(
                    criterion_id=criterion.id,
                    criterion_text=criterion.text,
                    status="CLEAR",
                    actual_value=None,
                    reason="לא דווח על הריון"
                )
            return CriterionResult(
                criterion_id=criterion.id,
                criterion_text=criterion.text,
                status="UNKNOWN",
                actual_value=None,
                reason="נתון חסר"
            )
        
        # Check excludes list (for status values)
        if criterion.excludes is not None:
            if str(value) in criterion.excludes:
                return CriterionResult(
                    criterion_id=criterion.id,
                    criterion_text=criterion.text,
                    status="EXCLUDES",
                    actual_value=value,
                    reason=f"סטטוס '{value}' פוסל מהשתתפות"
                )
            return CriterionResult(
                criterion_id=criterion.id,
                criterion_text=criterion.text,
                status="CLEAR",
                actual_value=value,
                reason="הסטטוס מאפשר השתתפות"
            )
        
        # Check contains (for medications/comorbidities exclusions)
        if criterion.contains is not None:
            if isinstance(value, list):
                contains_list = criterion.contains if isinstance(criterion.contains, list) else [criterion.contains]
                for item in contains_list:
                    if any(item.lower() in str(v).lower() for v in value):
                        return CriterionResult(
                            criterion_id=criterion.id,
                            criterion_text=criterion.text,
                            status="EXCLUDES",
                            actual_value=value,
                            reason=f"נמצא פריט פוסל: {item}"
                        )
                return CriterionResult(
                    criterion_id=criterion.id,
                    criterion_text=criterion.text,
                    status="CLEAR",
                    actual_value=value,
                    reason="לא נמצאו פריטים פוסלים"
                )
        
        # Default: clear
        return CriterionResult(
            criterion_id=criterion.id,
            criterion_text=criterion.text,
            status="CLEAR",
            actual_value=value,
            reason="לא נמצאה פסילה"
        )
    
    def _find_missing_data(
        self,
        patient: PatientBase,
        inclusion_results: List[CriterionResult],
        exclusion_results: List[CriterionResult]
    ) -> List[str]:
        """Collect list of missing data fields"""
        missing = []
        
        for result in inclusion_results + exclusion_results:
            if result.status == "UNKNOWN" and "חסר" in (result.reason or ""):
                missing.append(result.criterion_text)
        
        return missing
    
    def _determine_decision(
        self,
        inclusion_results: List[CriterionResult],
        exclusion_results: List[CriterionResult]
    ) -> str:
        """
        Determine final eligibility decision based on all results.
        
        Logic:
        - If any inclusion criterion is NOT_MET -> INELIGIBLE
        - If any exclusion criterion EXCLUDES -> INELIGIBLE
        - If any criterion is UNKNOWN -> UNCERTAIN
        - Otherwise -> ELIGIBLE
        """
        # Check for definite ineligibility
        for result in inclusion_results:
            if result.status == "NOT_MET":
                return "INELIGIBLE"
        
        for result in exclusion_results:
            if result.status == "EXCLUDES":
                return "INELIGIBLE"
        
        # Check for uncertainty
        for result in inclusion_results + exclusion_results:
            if result.status == "UNKNOWN":
                return "UNCERTAIN"
        
        # All criteria met and no exclusions
        return "ELIGIBLE"


# Singleton instance
eligibility_engine = EligibilityEngine()
