"""
Gemini API client for generating Hebrew explanations
Based on System Instructions from: docs/instructions_1_google_ai_studio.md

Uses the new google-genai SDK: https://github.com/google-gemini/python-genai
"""
import os
import logging
from typing import Optional

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from .schemas import PatientBase, EligibilityResult

logger = logging.getLogger(__name__)


# Complete System Instructions from Google AI Studio
# Source: instructions_1_google_ai_studio.md
SYSTEM_INSTRUCTIONS_HEBREW = """
# מערכת סינון מטופלים לניסויים קליניים - סוכרת סוג 2

## זהות המערכת
אתה מערכת תומכת החלטה קלינית (Clinical Decision Support System) לסינון מטופלים לניסויים קליניים בתחום הסוכרת סוג 2. תפקידך לנתח נתוני מטופלים מול קריטריוני ניסוי ולספק המלצה מבוססת עובדות עם הסבר מלא.

## עקרונות פעולה
1. **דיוק מעל הכל** - בדוק כל קריטריון בנפרד, אל תדלג
2. **שקיפות** - הסבר את הנימוק לכל החלטה
3. **זהירות** - אם חסר מידע, ציין "לא ברור" ולא "כשיר"
4. **עקביות** - השתמש תמיד באותו פורמט פלט

## מבנה הקלט שתקבל

### קריטריוני הניסוי:
- **קריטריוני הכללה (Inclusion)**: תנאים שהמטופל חייב לעמוד בהם
- **קריטריוני הדרה (Exclusion)**: תנאים שפוסלים את המטופל

### נתוני מטופל:
נתונים בפורמט JSON הכוללים: גיל, מין, אבחנות, תרופות, בדיקות מעבדה, ועוד.

## תהליך הבדיקה (בצע בסדר הזה!)

### שלב א: בדיקת קריטריוני הכללה
לכל קריטריון הכללה:
1. זהה את הפרמטר הנדרש (למשל: גיל 18-75)
2. מצא את הערך המתאים בנתוני המטופל
3. השווה וקבע: מתקיים ✅ / לא מתקיים ❌ / לא ידוע ⚠️

### שלב ב: בדיקת קריטריוני הדרה
לכל קריטריון הדרה:
1. זהה את המצב הפוסל (למשל: הריון)
2. בדוק אם המצב קיים אצל המטופל
3. קבע: תקין ✅ (לא קיים) / פוסל ❌ (קיים) / לא ידוע ⚠️

### שלב ג: החלטה סופית
- **כשיר ✅**: כל קריטריוני ההכללה מתקיימים וכל קריטריוני ההדרה תקינים
- **לא כשיר ❌**: לפחות קריטריון הכללה אחד לא מתקיים או קריטריון הדרה אחד פוסל
- **לא ברור ⚠️**: חסר מידע קריטי שמונע החלטה

## כללים חשובים

### לגבי ערכים חסרים:
- אם ערך קריטי חסר (כמו HbA1c) → "לא ברור"
- אם ערך משני חסר → ציין אך המשך בהערכה

### לגבי ערכי גבול:
- ערך בדיוק על הגבול (למשל גיל 75 כשהטווח 18-75) → **כשיר**
- ערך מעט מחוץ לגבול → **לא כשיר** עם ציון המרחק

### לגבי תרופות:
- חפש מילות מפתח כמו "אינסולין", "insulin" בכל הווריאציות
- שים לב לתאריכים - "ב-3 החודשים האחרונים" דורש חישוב

### לגבי מחלות נלוות:
- חפש מילות מפתח בתוך רשימת comorbidities
- "אי ספיקת לב NYHA II" ≠ "אי ספיקת לב NYHA III"

## שפה
ענה תמיד בעברית, גם אם הקלט באנגלית.
"""


class GeminiClient:
    """Client for Gemini API to generate eligibility explanations"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None
        self.model_name = "gemini-2.0-flash"  # Fast and accurate
        
        if GEMINI_AVAILABLE and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info("Gemini client initialized successfully with new google-genai SDK")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}")
    
    def is_available(self) -> bool:
        """Check if Gemini API is available"""
        return self.client is not None
    
    async def generate_explanation(
        self,
        patient: PatientBase,
        result: EligibilityResult,
        trial_name: str
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Generate Hebrew explanation for eligibility result.
        
        Returns:
            Tuple of (explanation, recommendation)
        """
        if not self.is_available():
            return self._generate_fallback(result)
        
        prompt = self._build_prompt(patient, result, trial_name)
        
        try:
            # Use the new google-genai SDK
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTIONS_HEBREW,
                    temperature=0.3,  # Low = consistent responses
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=2048
                )
            )
            text = response.text
            
            # Parse response into explanation and recommendation
            explanation, recommendation = self._parse_response(text)
            return explanation, recommendation
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._generate_fallback(result)
    
    def _build_prompt(
        self,
        patient: PatientBase,
        result: EligibilityResult,
        trial_name: str
    ) -> str:
        """Build prompt for Gemini based on AI Studio format"""
        
        decision_hebrew = {
            "ELIGIBLE": "כשיר ✅",
            "INELIGIBLE": "לא כשיר ❌",
            "UNCERTAIN": "לא ברור ⚠️"
        }.get(result.decision, result.decision)
        
        # Build criteria summary
        inclusion_summary = []
        for r in result.inclusion_results:
            status = "✅" if r.status == "MET" else "❌" if r.status == "NOT_MET" else "⚠️"
            inclusion_summary.append(f"| {r.criterion_text} | {r.patient_value or 'N/A'} | {status} |")
        
        exclusion_summary = []
        for r in result.exclusion_results:
            status = "✅ תקין" if r.status == "CLEAR" else "❌ פוסל" if r.status == "EXCLUDES" else "⚠️"
            exclusion_summary.append(f"| {r.criterion_text} | {r.patient_value or 'N/A'} | {status} |")
        
        # Build patient JSON like AI Studio test cases
        patient_json = {
            "patient_id": patient.patient_id,
            "age": patient.age,
            "gender": patient.gender,
            "diagnosis": patient.diagnosis,
            "HbA1c": patient.HbA1c,
            "eGFR": patient.eGFR,
            "current_medications": patient.current_medications,
            "comorbidities": patient.comorbidities,
            "pregnancy_status": patient.pregnancy_status,
            "clinical_notes": patient.clinical_notes
        }
        
        prompt = f"""
## קריטריוני ניסוי {trial_name}

### קריטריוני הכללה:
1. גיל 18-75 שנים
2. אבחנת סוכרת סוג 2 מאושרת
3. HbA1c בין 7.0% ל-10.0%
4. eGFR > 45 mL/min/1.73m²

### קריטריוני הדרה:
1. הריון או הנקה
2. טיפול באינסולין ב-3 החודשים האחרונים
3. אי ספיקת לב NYHA Class III או IV
4. מחלת כבד פעילה (כולל שחמת)

---

## נתוני מטופל {patient.patient_id}:
{patient_json}

---

## תוצאות הסינון המחושבות:
**החלטה**: {decision_hebrew}

### בדיקת קריטריוני הכללה:
| קריטריון | ערך המטופל | סטטוס |
|----------|------------|-------|
{chr(10).join(inclusion_summary)}

### בדיקת קריטריוני הדרה:
| קריטריון | ממצא במטופל | סטטוס |
|----------|-------------|-------|
{chr(10).join(exclusion_summary)}

נתונים חסרים: {", ".join(result.missing_data) if result.missing_data else "אין"}

---

## משימה
בהתבסס על הנתונים והתוצאות לעיל, כתוב:
1. **הסבר**: הסבר מקצועי של 3-5 משפטים המפרט את הסיבות להחלטה
2. **המלצה**: המלצה מעשית לצוות הקליני (1-2 משפטים)

פורמט התשובה:
הסבר: [הסבר כאן]
המלצה: [המלצה כאן]
"""
        return prompt
    
    def _parse_response(self, text: str) -> tuple[str, str]:
        """Parse Gemini response into explanation and recommendation"""
        explanation = ""
        recommendation = ""
        
        lines = text.strip().split("\n")
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith("הסבר:"):
                current_section = "explanation"
                explanation = line.replace("הסבר:", "").strip()
            elif line.startswith("המלצה:"):
                current_section = "recommendation"
                recommendation = line.replace("המלצה:", "").strip()
            elif current_section == "explanation" and line:
                explanation += " " + line
            elif current_section == "recommendation" and line:
                recommendation += " " + line
        
        return explanation.strip(), recommendation.strip()
    
    def _generate_fallback(self, result: EligibilityResult) -> tuple[str, str]:
        """Generate fallback explanation when Gemini is unavailable"""
        
        decision_text = {
            "ELIGIBLE": "המטופל עומד בכל קריטריוני ההכללה ואינו פוסל על פי קריטריוני ההדרה.",
            "INELIGIBLE": "המטופל אינו עומד בחלק מקריטריוני ההכללה או שנפסל על פי קריטריוני ההדרה.",
            "UNCERTAIN": "לא ניתן לקבוע את הכשירות בשל נתונים חסרים."
        }.get(result.decision, "")
        
        # Build details
        not_met = [r for r in result.inclusion_results if r.status == "NOT_MET"]
        excludes = [r for r in result.exclusion_results if r.status == "EXCLUDES"]
        
        details = []
        if not_met:
            details.append(f"קריטריונים שלא התמלאו: {', '.join(r.criterion_text for r in not_met)}")
        if excludes:
            details.append(f"קריטריוני הדרה: {', '.join(r.criterion_text for r in excludes)}")
        if result.missing_data:
            details.append(f"נתונים חסרים: {', '.join(result.missing_data)}")
        
        explanation = decision_text
        if details:
            explanation += " " + ". ".join(details)
        
        # Recommendation based on decision
        recommendation = {
            "ELIGIBLE": "מומלץ לקבוע פגישת מיון מקיפה עם המטופל.",
            "INELIGIBLE": "אין להמשיך בתהליך הגיוס לניסוי זה.",
            "UNCERTAIN": "יש להשלים את הנתונים החסרים לפני קבלת החלטה סופית."
        }.get(result.decision, "")
        
        return explanation, recommendation


# Singleton instance
gemini_client = GeminiClient()
