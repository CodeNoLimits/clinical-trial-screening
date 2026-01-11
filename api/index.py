"""
Vercel Serverless Function - Clinical Trial Screening API
Simple HTTP handler for Vercel Python runtime
"""
import os
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# ============== Sample Data ==============

SAMPLE_TRIAL = {
    "id": "DM2-2024-001",
    "name": "ניסוי קליני לטיפול חדשני בסוכרת סוג 2",
    "phase": "Phase III",
    "sponsor": "מרכז רפואי אקדמי",
    "description": "ניסוי לבדיקת יעילות תרופה חדשנית לטיפול בסוכרת סוג 2",
    "is_active": True,
    "created_at": "2026-01-11T00:00:00",
    "updated_at": "2026-01-11T00:00:00",
    "inclusion_criteria": [
        {"id": "INC01", "text": "גיל 18-75 שנים", "field": "age", "min": 18, "max": 75, "value": None, "contains": None, "excludes": None},
        {"id": "INC02", "text": "אבחנת סוכרת סוג 2", "field": "diagnosis", "min": None, "max": None, "value": "סוכרת סוג 2", "contains": None, "excludes": None},
        {"id": "INC03", "text": "HbA1c 7.0%-10.0%", "field": "HbA1c", "min": 7.0, "max": 10.0, "value": None, "contains": None, "excludes": None},
        {"id": "INC04", "text": "eGFR > 45", "field": "eGFR", "min": 45, "max": None, "value": None, "contains": None, "excludes": None}
    ],
    "exclusion_criteria": [
        {"id": "EXC01", "text": "הריון או הנקה", "field": "pregnancy_status", "min": None, "max": None, "value": None, "contains": None, "excludes": ["בהריון", "מניקה"]},
        {"id": "EXC02", "text": "טיפול באינסולין ב-3 חודשים אחרונים", "field": "current_medications", "min": None, "max": None, "value": None, "contains": "אינסולין", "excludes": None},
        {"id": "EXC03", "text": "אי ספיקת לב NYHA III-IV", "field": "comorbidities", "min": None, "max": None, "value": None, "contains": ["NYHA III", "NYHA IV"], "excludes": None},
        {"id": "EXC04", "text": "מחלת כבד פעילה", "field": "comorbidities", "min": None, "max": None, "value": None, "contains": ["שחמת", "מחלת כבד"], "excludes": None}
    ]
}

SAMPLE_PATIENTS = [
    {
        "patient_id": "P001",
        "age": 52,
        "gender": "זכר",
        "diagnosis": "סוכרת סוג 2",
        "diagnosis_date": "2019-03-15",
        "HbA1c": 8.2,
        "eGFR": 78,
        "current_medications": ["מטפורמין 1000mg x2", "אמלודיפין 5mg"],
        "comorbidities": ["יתר לחץ דם"],
        "pregnancy_status": None,
        "clinical_notes": "מטופל יציב, היענות טובה לטיפול"
    },
    {
        "patient_id": "P002",
        "age": 67,
        "gender": "נקבה",
        "diagnosis": "סוכרת סוג 2",
        "diagnosis_date": "2015-08-20",
        "HbA1c": 7.5,
        "eGFR": 55,
        "current_medications": ["מטפורמין 850mg x3", "גליקלזיד 60mg"],
        "comorbidities": ["יתר לחץ דם", "היפרליפידמיה"],
        "pregnancy_status": None,
        "clinical_notes": "תפקוד כליות תקין לגיל"
    },
    {
        "patient_id": "P003",
        "age": 45,
        "gender": "זכר",
        "diagnosis": "סוכרת סוג 2",
        "diagnosis_date": "2021-01-10",
        "HbA1c": 11.2,
        "eGFR": 92,
        "current_medications": ["מטפורמין 500mg x2"],
        "comorbidities": ["השמנה"],
        "pregnancy_status": None,
        "clinical_notes": "HbA1c לא מאוזן, נדרש שיפור טיפולי"
    },
    {
        "patient_id": "P004",
        "age": 34,
        "gender": "נקבה",
        "diagnosis": "סוכרת סוג 2",
        "diagnosis_date": "2022-06-05",
        "HbA1c": 7.8,
        "eGFR": 105,
        "current_medications": ["מטפורמין 1000mg x2"],
        "comorbidities": [],
        "pregnancy_status": "בהריון",
        "clinical_notes": "הריון שבוע 16, מעקב בסיכון גבוה"
    }
]

# ============== Eligibility Engine ==============

def evaluate_criterion(criterion, patient):
    """Evaluate a single criterion against patient data"""
    field = criterion.get("field")
    patient_value = patient.get(field)

    # Check for missing data
    if patient_value is None:
        if criterion.get("excludes") and field == "pregnancy_status":
            return {
                "criterion_id": criterion["id"],
                "criterion_text": criterion["text"],
                "status": "CLEAR",
                "actual_value": None,
                "reason": "לא דווח על הריון"
            }
        if criterion.get("contains") and isinstance(patient.get(field, []), list) and len(patient.get(field, [])) == 0:
            return {
                "criterion_id": criterion["id"],
                "criterion_text": criterion["text"],
                "status": "CLEAR",
                "actual_value": [],
                "reason": "לא נמצאו פריטים פוסלים"
            }
        return {
            "criterion_id": criterion["id"],
            "criterion_text": criterion["text"],
            "status": "UNKNOWN",
            "actual_value": patient_value,
            "reason": "נתון חסר"
        }

    # Range check (min/max)
    if criterion.get("min") is not None or criterion.get("max") is not None:
        try:
            val = float(patient_value) if patient_value else None
            if val is None:
                return {
                    "criterion_id": criterion["id"],
                    "criterion_text": criterion["text"],
                    "status": "UNKNOWN",
                    "actual_value": patient_value,
                    "reason": "נתון חסר"
                }

            min_val = criterion.get("min")
            max_val = criterion.get("max")

            if min_val is not None and val < min_val:
                return {
                    "criterion_id": criterion["id"],
                    "criterion_text": criterion["text"],
                    "status": "NOT_MET",
                    "actual_value": val,
                    "reason": f"הערך {val} נמוך מהמינימום {min_val}"
                }
            if max_val is not None and val > max_val:
                return {
                    "criterion_id": criterion["id"],
                    "criterion_text": criterion["text"],
                    "status": "NOT_MET",
                    "actual_value": val,
                    "reason": f"הערך {val} גבוה מהמקסימום {max_val}"
                }
            return {
                "criterion_id": criterion["id"],
                "criterion_text": criterion["text"],
                "status": "MET",
                "actual_value": val,
                "reason": "הערך בטווח המותר"
            }
        except (ValueError, TypeError):
            return {
                "criterion_id": criterion["id"],
                "criterion_text": criterion["text"],
                "status": "UNKNOWN",
                "actual_value": patient_value,
                "reason": "לא ניתן לבדוק ערך"
            }

    # Exact value match
    if criterion.get("value") is not None:
        if patient_value == criterion["value"]:
            return {
                "criterion_id": criterion["id"],
                "criterion_text": criterion["text"],
                "status": "MET",
                "actual_value": patient_value,
                "reason": "התאמה מדויקת"
            }
        return {
            "criterion_id": criterion["id"],
            "criterion_text": criterion["text"],
            "status": "NOT_MET",
            "actual_value": patient_value,
            "reason": f"הערך '{patient_value}' לא תואם ל-'{criterion['value']}'"
        }

    # Excludes check (for exclusion criteria)
    if criterion.get("excludes"):
        excludes = criterion["excludes"]
        if patient_value in excludes:
            return {
                "criterion_id": criterion["id"],
                "criterion_text": criterion["text"],
                "status": "EXCLUDES",
                "actual_value": patient_value,
                "reason": f"סטטוס '{patient_value}' פוסל מהשתתפות"
            }
        return {
            "criterion_id": criterion["id"],
            "criterion_text": criterion["text"],
            "status": "CLEAR",
            "actual_value": patient_value,
            "reason": "לא דווח על הריון"
        }

    # Contains check (for list fields)
    if criterion.get("contains"):
        contains = criterion["contains"]
        if isinstance(contains, str):
            contains = [contains]

        if isinstance(patient_value, list):
            for item in patient_value:
                for c in contains:
                    if c.lower() in item.lower():
                        return {
                            "criterion_id": criterion["id"],
                            "criterion_text": criterion["text"],
                            "status": "EXCLUDES",
                            "actual_value": patient_value,
                            "reason": f"נמצא פריט פוסל: {c}"
                        }

        return {
            "criterion_id": criterion["id"],
            "criterion_text": criterion["text"],
            "status": "CLEAR",
            "actual_value": patient_value,
            "reason": "לא נמצאו פריטים פוסלים"
        }

    return {
        "criterion_id": criterion["id"],
        "criterion_text": criterion["text"],
        "status": "MET",
        "actual_value": patient_value,
        "reason": "תקין"
    }


def evaluate_eligibility(patient, inclusion_criteria, exclusion_criteria):
    """Evaluate patient eligibility based on criteria"""
    inclusion_results = []
    exclusion_results = []
    missing_data = []

    for criterion in inclusion_criteria:
        result = evaluate_criterion(criterion, patient)
        inclusion_results.append(result)
        if result["status"] == "UNKNOWN":
            missing_data.append(criterion["field"])

    for criterion in exclusion_criteria:
        result = evaluate_criterion(criterion, patient)
        exclusion_results.append(result)
        if result["status"] == "UNKNOWN":
            missing_data.append(criterion["field"])

    has_not_met = any(r["status"] == "NOT_MET" for r in inclusion_results)
    has_excludes = any(r["status"] == "EXCLUDES" for r in exclusion_results)
    has_unknown = any(r["status"] == "UNKNOWN" for r in inclusion_results + exclusion_results)

    if has_excludes or has_not_met:
        decision = "INELIGIBLE"
    elif has_unknown:
        decision = "UNCERTAIN"
    else:
        decision = "ELIGIBLE"

    return {
        "decision": decision,
        "inclusion_results": inclusion_results,
        "exclusion_results": exclusion_results,
        "missing_data": list(set(missing_data)),
        "ai_explanation": None,
        "recommendation": None
    }


def generate_explanation(result, trial_name):
    """Generate explanation based on result"""
    if result["decision"] == "INELIGIBLE":
        not_met = [r for r in result["inclusion_results"] if r["status"] == "NOT_MET"]
        excludes = [r for r in result["exclusion_results"] if r["status"] == "EXCLUDES"]
        parts = []
        if not_met:
            parts.append(f"קריטריוני הכללה: {', '.join(r['criterion_text'] for r in not_met)}")
        if excludes:
            parts.append(f"קריטריוני הדרה: {', '.join(r['criterion_text'] for r in excludes)}")
        return f"המטופל אינו עומד בחלק מקריטריוני ההכללה או שנפסל על פי קריטריוני ההדרה. {'; '.join(parts)}", "אין להמשיך בתהליך הגיוס לניסוי זה."
    elif result["decision"] == "UNCERTAIN":
        return "חסר מידע לקביעת כשירות סופית.", "יש להשלים את הנתונים החסרים לפני קבלת החלטה."
    return "המטופל עומד בכל הקריטריונים לניסוי.", None


# ============== HTTP Handler ==============

class handler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path

        if path == '/api/' or path == '/api':
            self.send_json({
                "name": "Clinical Trial Screening API",
                "version": "1.0.0",
                "status": "running",
                "docs": "/api/docs"
            })

        elif path == '/api/health' or path == '/api/health/':
            self.send_json({"status": "healthy"})

        elif path == '/api/trials/' or path == '/api/trials':
            self.send_json([{
                "id": SAMPLE_TRIAL["id"],
                "name": SAMPLE_TRIAL["name"],
                "phase": SAMPLE_TRIAL["phase"],
                "sponsor": SAMPLE_TRIAL["sponsor"],
                "is_active": SAMPLE_TRIAL["is_active"]
            }])

        elif path.startswith('/api/trials/'):
            trial_id = path.replace('/api/trials/', '').rstrip('/')
            if trial_id == SAMPLE_TRIAL["id"]:
                self.send_json(SAMPLE_TRIAL)
            else:
                self.send_json({"error": "Trial not found"}, 404)

        elif path == '/api/sample-patients' or path == '/api/sample-patients/':
            self.send_json(SAMPLE_PATIENTS)

        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        path = urlparse(self.path).path

        if path == '/api/screening/' or path == '/api/screening':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)

            try:
                data = json.loads(body.decode('utf-8'))
            except json.JSONDecodeError:
                self.send_json({"error": "Invalid JSON"}, 400)
                return

            trial_id = data.get("trial_id")
            patient = data.get("patient", {})
            generate_ai = data.get("generate_ai_explanation", True)

            if trial_id != SAMPLE_TRIAL["id"]:
                self.send_json({"error": "Trial not found"}, 404)
                return

            # Evaluate eligibility
            result = evaluate_eligibility(
                patient=patient,
                inclusion_criteria=SAMPLE_TRIAL["inclusion_criteria"],
                exclusion_criteria=SAMPLE_TRIAL["exclusion_criteria"]
            )

            # Generate explanation
            if generate_ai:
                explanation, recommendation = generate_explanation(result, SAMPLE_TRIAL["name"])
                result["ai_explanation"] = explanation
                result["recommendation"] = recommendation

            response = {
                "trial_id": SAMPLE_TRIAL["id"],
                "trial_name": SAMPLE_TRIAL["name"],
                "patient_id": patient.get("patient_id", "unknown"),
                "result": result,
                "screened_at": datetime.utcnow().isoformat()
            }

            self.send_json(response)

        elif path == '/api/screening/batch' or path == '/api/screening/batch/':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)

            try:
                data = json.loads(body.decode('utf-8'))
            except json.JSONDecodeError:
                self.send_json({"error": "Invalid JSON"}, 400)
                return

            trial_id = data.get("trial_id")
            patients = data.get("patients", [])

            if trial_id != SAMPLE_TRIAL["id"]:
                self.send_json({"error": "Trial not found"}, 404)
                return

            results = []
            eligible_count = 0
            ineligible_count = 0
            uncertain_count = 0

            for patient in patients:
                result = evaluate_eligibility(
                    patient=patient,
                    inclusion_criteria=SAMPLE_TRIAL["inclusion_criteria"],
                    exclusion_criteria=SAMPLE_TRIAL["exclusion_criteria"]
                )

                if result["decision"] == "ELIGIBLE":
                    eligible_count += 1
                    summary = "עומד בכל הקריטריונים"
                elif result["decision"] == "INELIGIBLE":
                    ineligible_count += 1
                    not_met = [r for r in result["inclusion_results"] if r["status"] == "NOT_MET"]
                    excludes = [r for r in result["exclusion_results"] if r["status"] == "EXCLUDES"]
                    parts = []
                    if not_met:
                        parts.append(f"לא עמד ב: {', '.join(r['criterion_id'] for r in not_met)}")
                    if excludes:
                        parts.append(f"נפסל ע\"י: {', '.join(r['criterion_id'] for r in excludes)}")
                    summary = "; ".join(parts) if parts else "INELIGIBLE"
                else:
                    uncertain_count += 1
                    summary = f"נתונים חסרים: {len(result['missing_data'])}"

                results.append({
                    "patient_id": patient.get("patient_id", "unknown"),
                    "decision": result["decision"],
                    "summary": summary
                })

            self.send_json({
                "trial_id": SAMPLE_TRIAL["id"],
                "total_patients": len(patients),
                "eligible_count": eligible_count,
                "ineligible_count": ineligible_count,
                "uncertain_count": uncertain_count,
                "results": results
            })

        else:
            self.send_json({"error": "Not found"}, 404)
