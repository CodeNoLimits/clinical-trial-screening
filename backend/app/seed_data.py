"""
Seed data for the Clinical Trial Screening System
Contains sample trial and 8 test patients from Google AI Studio instructions

Based on: docs/instructions_1_google_ai_studio.md
"""


def get_sample_trial():
    """
    Return the sample Type 2 Diabetes trial (DM2-2024-001)
    
    Inclusion Criteria:
    1. Age 18-75 years
    2. Confirmed Type 2 Diabetes diagnosis
    3. HbA1c between 7.0% and 10.0%
    4. eGFR > 45 mL/min/1.73m²
    
    Exclusion Criteria:
    1. Pregnancy or breastfeeding
    2. Insulin treatment in the last 3 months
    3. Heart failure NYHA Class III or IV
    4. Active liver disease (including cirrhosis)
    """
    return {
        "id": "DM2-2024-001",
        "name": "ניסוי קליני לטיפול חדשני בסוכרת סוג 2",
        "phase": "Phase III",
        "sponsor": "מרכז רפואי אקדמי",
        "description": "ניסוי קליני רב-מרכזי לבחינת יעילות ובטיחות של טיפול חדשני בסוכרת סוג 2 במבוגרים.",
        "inclusion_criteria": [
            {
                "id": "INC01",
                "text": "גיל 18-75 שנים",
                "field": "age",
                "min": 18,
                "max": 75
            },
            {
                "id": "INC02",
                "text": "אבחנת סוכרת סוג 2 מאושרת",
                "field": "diagnosis",
                "value": "סוכרת סוג 2"
            },
            {
                "id": "INC03",
                "text": "HbA1c בין 7.0% ל-10.0%",
                "field": "HbA1c",
                "min": 7.0,
                "max": 10.0
            },
            {
                "id": "INC04",
                "text": "eGFR > 45 mL/min/1.73m²",
                "field": "eGFR",
                "min": 45
            }
        ],
        "exclusion_criteria": [
            {
                "id": "EXC01",
                "text": "הריון או הנקה",
                "field": "pregnancy_status",
                "excludes": ["בהריון", "מניקה", "הנקה"]
            },
            {
                "id": "EXC02",
                "text": "טיפול באינסולין ב-3 החודשים האחרונים",
                "field": "current_medications",
                "contains": ["אינסולין", "insulin", "לנטוס", "גלרגין", "Lantus", "Glargine"]
            },
            {
                "id": "EXC03",
                "text": "אי ספיקת לב NYHA Class III או IV",
                "field": "comorbidities",
                "contains": ["NYHA III", "NYHA IV", "NYHA Class III", "NYHA Class IV"]
            },
            {
                "id": "EXC04",
                "text": "מחלת כבד פעילה (כולל שחמת)",
                "field": "comorbidities",
                "contains": ["שחמת", "cirrhosis", "מחלת כבד פעילה", "שחמת כבד"]
            }
        ]
    }


def get_sample_patients():
    """
    Return list of 8 test patients from Google AI Studio instructions.
    These are the exact test cases used to validate the Gemini prompts.
    
    Expected Results:
    | Patient | Expected Result | Reason |
    |---------|-----------------|--------|
    | P001    | ✅ ELIGIBLE     | Meets all criteria |
    | P002    | ❌ INELIGIBLE   | HbA1c 11.5% > 10% |
    | P003    | ❌ INELIGIBLE   | eGFR 38 < 45 + Insulin |
    | P004    | ❌ INELIGIBLE   | Pregnancy |
    | P005    | ✅ ELIGIBLE     | Ideal candidate |
    | P006    | ❌ INELIGIBLE   | Age 77 > 75 |
    | P007    | ❌ INELIGIBLE   | Liver cirrhosis |
    | P008    | ⚠️ UNCERTAIN    | Missing HbA1c |
    """
    return [
        # P001 - Expected: ELIGIBLE ✅ - Meets all criteria
        {
            "patient_id": "P001",
            "age": 52,
            "gender": "זכר",
            "diagnosis": "סוכרת סוג 2",
            "diagnosis_date": "2020-03-15",
            "HbA1c": 8.2,
            "eGFR": 78,
            "creatinine": 1.0,
            "current_medications": ["מטפורמין 1000mg פעמיים ביום", "גליקלזיד 60mg"],
            "comorbidities": ["יתר לחץ דם"],
            "pregnancy_status": None,
            "clinical_notes": "מטופל יציב במעקב רגיל. ללא שינויים משמעותיים בטיפול. אינו משתמש באינסולין.",
            "expected_result": "ELIGIBLE"
        },
        # P002 - Expected: INELIGIBLE ❌ - HbA1c 11.5% > 10%
        {
            "patient_id": "P002",
            "age": 45,
            "gender": "נקבה",
            "diagnosis": "סוכרת סוג 2",
            "diagnosis_date": "2019-08-20",
            "HbA1c": 11.5,
            "eGFR": 82,
            "creatinine": 0.8,
            "current_medications": ["מטפורמין 850mg פעמיים ביום"],
            "comorbidities": [],
            "pregnancy_status": "לא בהריון",
            "clinical_notes": "סוכרת לא מאוזנת. שוקלים הוספת טיפול נוסף.",
            "expected_result": "INELIGIBLE",
            "expected_reason": "HbA1c 11.5% > 10%"
        },
        # P003 - Expected: INELIGIBLE ❌ - eGFR 38 < 45 + Insulin
        {
            "patient_id": "P003",
            "age": 68,
            "gender": "זכר",
            "diagnosis": "סוכרת סוג 2",
            "diagnosis_date": "2015-01-10",
            "HbA1c": 7.8,
            "eGFR": 38,
            "creatinine": 1.8,
            "current_medications": ["אינסולין גלרגין 20 יחידות בערב", "מטפורמין 500mg"],
            "comorbidities": ["אי ספיקת כליות כרונית שלב 3b", "אי ספיקת לב NYHA II"],
            "pregnancy_status": None,
            "clinical_notes": "מטופל עם תחלואה נלווית משמעותית. תפקוד כלייתי ירוד.",
            "expected_result": "INELIGIBLE",
            "expected_reason": "eGFR 38 < 45 and uses insulin"
        },
        # P004 - Expected: INELIGIBLE ❌ - Pregnancy
        {
            "patient_id": "P004",
            "age": 34,
            "gender": "נקבה",
            "diagnosis": "סוכרת סוג 2",
            "diagnosis_date": "2023-06-01",
            "HbA1c": 7.5,
            "eGFR": 95,
            "creatinine": 0.7,
            "current_medications": ["מטפורמין 1000mg פעמיים ביום"],
            "comorbidities": [],
            "pregnancy_status": "בהריון שבוע 12",
            "clinical_notes": "סוכרת הריונית שהתגלתה כסוג 2. במעקב הריון בסיכון.",
            "expected_result": "INELIGIBLE",
            "expected_reason": "Pregnancy"
        },
        # P005 - Expected: ELIGIBLE ✅ - Ideal candidate
        {
            "patient_id": "P005",
            "age": 58,
            "gender": "זכר",
            "diagnosis": "סוכרת סוג 2",
            "diagnosis_date": "2018-11-30",
            "HbA1c": 8.8,
            "eGFR": 65,
            "creatinine": 1.2,
            "current_medications": ["מטפורמין 1000mg פעמיים ביום", "אמפגליפלוזין 10mg"],
            "comorbidities": ["יתר לחץ דם מאוזן", "דיסליפידמיה"],
            "pregnancy_status": None,
            "clinical_notes": "מטופל עם תחלואה נלווית מבוקרת. מועמד מצוין לניסוי.",
            "expected_result": "ELIGIBLE"
        },
        # P006 - Expected: INELIGIBLE ❌ - Age 77 > 75
        {
            "patient_id": "P006",
            "age": 77,
            "gender": "זכר",
            "diagnosis": "סוכרת סוג 2",
            "diagnosis_date": "2010-05-20",
            "HbA1c": 7.2,
            "eGFR": 55,
            "creatinine": 1.4,
            "current_medications": ["מטפורמין 500mg"],
            "comorbidities": ["יתר לחץ דם"],
            "pregnancy_status": None,
            "clinical_notes": "מטופל קשיש, סוכרת מאוזנת.",
            "expected_result": "INELIGIBLE",
            "expected_reason": "Age 77 > 75"
        },
        # P007 - Expected: INELIGIBLE ❌ - Liver cirrhosis
        {
            "patient_id": "P007",
            "age": 49,
            "gender": "נקבה",
            "diagnosis": "סוכרת סוג 2",
            "diagnosis_date": "2021-02-14",
            "HbA1c": 9.1,
            "eGFR": 72,
            "creatinine": 0.9,
            "current_medications": ["מטפורמין 1000mg", "סיטאגליפטין 100mg"],
            "comorbidities": ["שחמת כבד ראשונית"],
            "pregnancy_status": "לא בהריון",
            "clinical_notes": "מחלת כבד פעילה במעקב.",
            "expected_result": "INELIGIBLE",
            "expected_reason": "Liver cirrhosis"
        },
        # P008 - Expected: UNCERTAIN ⚠️ - Missing HbA1c
        {
            "patient_id": "P008",
            "age": 61,
            "gender": "זכר",
            "diagnosis": "סוכרת סוג 2",
            "diagnosis_date": "2017-09-05",
            "HbA1c": None,  # Missing!
            "eGFR": 68,
            "creatinine": 1.1,
            "current_medications": ["מטפורמין 850mg פעמיים ביום"],
            "comorbidities": [],
            "pregnancy_status": None,
            "clinical_notes": "לא נמדד HbA1c ב-3 החודשים האחרונים.",
            "expected_result": "UNCERTAIN",
            "expected_reason": "Missing HbA1c value"
        }
    ]


def get_expected_results_table():
    """
    Return a summary table of expected results for validation.
    This matches the table in the AI Studio instructions document.
    """
    return [
        {"patient_id": "P001", "expected": "ELIGIBLE", "reason": "עומד בכל הקריטריונים"},
        {"patient_id": "P002", "expected": "INELIGIBLE", "reason": "HbA1c 11.5% > 10%"},
        {"patient_id": "P003", "expected": "INELIGIBLE", "reason": "eGFR 38 < 45 + אינסולין"},
        {"patient_id": "P004", "expected": "INELIGIBLE", "reason": "הריון"},
        {"patient_id": "P005", "expected": "ELIGIBLE", "reason": "מועמד אידיאלי"},
        {"patient_id": "P006", "expected": "INELIGIBLE", "reason": "גיל 77 > 75"},
        {"patient_id": "P007", "expected": "INELIGIBLE", "reason": "שחמת כבד"},
        {"patient_id": "P008", "expected": "UNCERTAIN", "reason": "חסר HbA1c"}
    ]
