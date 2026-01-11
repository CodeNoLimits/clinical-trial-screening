"""
Clinical Trial Eligibility Screening API
Main application entry point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db, get_db, SessionLocal
from .routers import trials, screening, patients
from .models import Trial


# Sample trial data
SAMPLE_TRIAL = {
    "id": "DM2-2024-001",
    "name": "ניסוי קליני לטיפול חדשני בסוכרת סוג 2",
    "phase": "Phase III",
    "sponsor": "מרכז רפואי אקדמי",
    "description": "ניסוי לבדיקת יעילות תרופה חדשנית לטיפול בסוכרת סוג 2",
    "inclusion_criteria": [
        {"id": "INC01", "text": "גיל 18-75 שנים", "field": "age", "min": 18, "max": 75},
        {"id": "INC02", "text": "אבחנת סוכרת סוג 2", "field": "diagnosis", "value": "סוכרת סוג 2"},
        {"id": "INC03", "text": "HbA1c 7.0%-10.0%", "field": "HbA1c", "min": 7.0, "max": 10.0},
        {"id": "INC04", "text": "eGFR > 45", "field": "eGFR", "min": 45}
    ],
    "exclusion_criteria": [
        {"id": "EXC01", "text": "הריון או הנקה", "field": "pregnancy_status", "excludes": ["בהריון", "מניקה"]},
        {"id": "EXC02", "text": "טיפול באינסולין ב-3 חודשים אחרונים", "field": "current_medications", "contains": "אינסולין"},
        {"id": "EXC03", "text": "אי ספיקת לב NYHA III-IV", "field": "comorbidities", "contains": ["NYHA III", "NYHA IV"]},
        {"id": "EXC04", "text": "מחלת כבד פעילה", "field": "comorbidities", "contains": ["שחמת", "מחלת כבד"]}
    ]
}

# Sample patients for testing
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
    },
    {
        "patient_id": "P005",
        "age": 58,
        "gender": "זכר",
        "diagnosis": "סוכרת סוג 2",
        "diagnosis_date": "2017-11-22",
        "HbA1c": 8.8,
        "eGFR": 65,
        "current_medications": ["מטפורמין 1000mg x2", "אינסולין גלרגין 20 יח'"],
        "comorbidities": ["יתר לחץ דם", "נוירופתיה"],
        "pregnancy_status": None,
        "clinical_notes": "מטופל באינסולין מזה 6 חודשים"
    },
    {
        "patient_id": "P006",
        "age": 71,
        "gender": "זכר",
        "diagnosis": "סוכרת סוג 2",
        "diagnosis_date": "2010-04-30",
        "HbA1c": 7.2,
        "eGFR": 42,
        "current_medications": ["מטפורמין 500mg x2", "סיטגליפטין 100mg"],
        "comorbidities": ["אי ספיקת כליות כרונית שלב 3b"],
        "pregnancy_status": None,
        "clinical_notes": "מעקב נפרולוגי, הגבלת מינון מטפורמין"
    },
    {
        "patient_id": "P007",
        "age": 49,
        "gender": "נקבה",
        "diagnosis": "סוכרת סוג 2",
        "diagnosis_date": "2020-09-14",
        "HbA1c": 8.5,
        "eGFR": 88,
        "current_medications": ["מטפורמין 1000mg x2", "אמפגליפלוזין 10mg"],
        "comorbidities": ["יתר לחץ דם", "אי ספיקת לב NYHA III"],
        "pregnancy_status": None,
        "clinical_notes": "אי ספיקת לב מתקדמת, מעקב קרדיולוגי"
    },
    {
        "patient_id": "P008",
        "age": 62,
        "gender": "זכר",
        "diagnosis": "סוכרת סוג 2",
        "diagnosis_date": "2016-02-28",
        "HbA1c": None,
        "eGFR": 75,
        "current_medications": ["מטפורמין 850mg x2"],
        "comorbidities": ["יתר לחץ דם"],
        "pregnancy_status": None,
        "clinical_notes": "לא הגיע לבדיקת HbA1c האחרונה"
    }
]


def seed_database():
    """Seed the database with sample data"""
    db = SessionLocal()
    try:
        # Check if trial already exists
        existing = db.query(Trial).filter(Trial.id == SAMPLE_TRIAL["id"]).first()
        if not existing:
            trial = Trial(
                id=SAMPLE_TRIAL["id"],
                name=SAMPLE_TRIAL["name"],
                phase=SAMPLE_TRIAL["phase"],
                sponsor=SAMPLE_TRIAL["sponsor"],
                description=SAMPLE_TRIAL["description"],
                inclusion_criteria=SAMPLE_TRIAL["inclusion_criteria"],
                exclusion_criteria=SAMPLE_TRIAL["exclusion_criteria"],
            )
            db.add(trial)
            db.commit()
            print(f"✓ Seeded trial: {SAMPLE_TRIAL['id']}")
        else:
            print(f"→ Trial already exists: {SAMPLE_TRIAL['id']}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Initialize database
    init_db()
    print("✓ Database initialized")

    # Seed sample data
    seed_database()

    yield

    # Cleanup (if needed)
    print("→ Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Clinical Trial Screening API",
    description="מערכת לסינון כשירות מטופלים לניסויים קליניים",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(trials.router, prefix="/api")
app.include_router(screening.router, prefix="/api")
app.include_router(patients.router, prefix="/api")


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": "Clinical Trial Screening API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/api/sample-patients")
def get_sample_patients():
    """Get sample patients for testing"""
    return SAMPLE_PATIENTS
