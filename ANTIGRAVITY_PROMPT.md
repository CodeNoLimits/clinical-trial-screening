# Antigravity Deployment Prompt for Clinical Trial Screening System

## Quick Start Prompt for Antigravity

Copy and paste this prompt into Google Antigravity to deploy the existing application:

---

## DEPLOYMENT PROMPT

```
I have a complete Clinical Trial Eligibility Screening System in this folder. 
The application is fully built with:
- Backend: FastAPI (Python 3.11)
- Frontend: React + TypeScript + Tailwind CSS
- Database: SQLite
- AI: Google Gemini API for Hebrew explanations

Please help me:

1. VERIFY THE APPLICATION WORKS LOCALLY:
   - Install backend dependencies (cd backend && pip install -r requirements.txt)
   - Start backend (uvicorn app.main:app --reload --port 8000)
   - Install frontend dependencies (cd frontend && npm install)
   - Start frontend (npm run dev)
   - Test with sample patients at http://localhost:5173

2. DEPLOY TO GOOGLE CLOUD RUN:
   - Build Docker images
   - Push to Google Container Registry
   - Deploy backend to Cloud Run (region: me-west1, 512MB RAM)
   - Deploy frontend to Cloud Run
   - Configure environment variables (GEMINI_API_KEY)
   - Provide public URLs

My Google Cloud Project ID is: [REPLACE_WITH_YOUR_PROJECT_ID]
My Gemini API Key is: [REPLACE_WITH_YOUR_API_KEY]
```

---

## EXPECTED PATIENT RESULTS

When testing with sample patients, expected results are:

| Patient | Expected Decision | Reason |
|---------|------------------|--------|
| P001 | ELIGIBLE | All criteria met |
| P002 | ELIGIBLE | All criteria met |
| P003 | INELIGIBLE | HbA1c too high (11.2 > 10.0) |
| P004 | INELIGIBLE | Pregnant (exclusion) |
| P005 | INELIGIBLE | On insulin (exclusion) |
| P006 | INELIGIBLE | eGFR too low (42 < 45) |
| P007 | INELIGIBLE | NYHA III heart failure (exclusion) |
| P008 | UNCERTAIN | Missing HbA1c data |

---

## ENHANCEMENT PROMPTS FOR ANTIGRAVITY

### Add PDF Export
```
Add PDF export functionality to the ResultsDashboard component:
1. Use html2pdf.js or react-pdf libraries
2. Generate professional PDF with logo
3. Include all criteria results and AI explanation
4. Support Hebrew RTL text
```

### Add Real-time Validation
```
Enhance PatientForm with real-time validation:
1. Show warnings for out-of-range values
2. Highlight missing required fields
3. Preview eligibility before submission
```

### Add User Authentication
```
Add user authentication to the application:
1. Use Firebase Auth or Auth0
2. Add login/logout functionality
3. Associate screenings with user accounts
4. Add admin role for trial management
```

### Connect to External EHR
```
Add integration with FHIR-based EHR systems:
1. Create FHIR client service
2. Map FHIR Patient resources to our schema
3. Add "Import from EHR" button
4. Handle OAuth2 authentication
```

---

## CLOUD RUN DEPLOYMENT COMMANDS (Manual)

If Antigravity MCP is not available, use these commands:

```bash
# Set project
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# Enable APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and push backend
cd backend
gcloud builds submit --tag gcr.io/$PROJECT_ID/clinical-trial-backend
gcloud run deploy clinical-trial-backend \
  --image gcr.io/$PROJECT_ID/clinical-trial-backend \
  --platform managed \
  --region me-west1 \
  --memory 512Mi \
  --allow-unauthenticated \
  --set-env-vars="GEMINI_API_KEY=your-key"

# Build and push frontend (update API URL first)
cd ../frontend
gcloud builds submit --tag gcr.io/$PROJECT_ID/clinical-trial-frontend
gcloud run deploy clinical-trial-frontend \
  --image gcr.io/$PROJECT_ID/clinical-trial-frontend \
  --platform managed \
  --region me-west1 \
  --memory 256Mi \
  --allow-unauthenticated
```

---

## API ENDPOINTS

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/trials/ | List all trials |
| GET | /api/trials/{id} | Get trial details |
| POST | /api/trials/ | Create trial |
| POST | /api/screening/ | Screen single patient |
| POST | /api/screening/batch | Screen multiple patients |
| GET | /api/screening/history | Get audit trail |
| GET | /api/sample-patients | Get test patients |

---

## TROUBLESHOOTING

### Backend won't start
- Check Python version (need 3.11+)
- Verify all dependencies installed
- Check if port 8000 is available

### Frontend build fails
- Check Node version (need 18+)
- Delete node_modules and reinstall
- Check for TypeScript errors

### Gemini API not working
- Verify API key is set in environment
- Check API quotas in Google Cloud Console
- Fallback explanations will be generated

### Cloud Run deployment fails
- Check Docker builds locally first
- Verify IAM permissions
- Check Cloud Run logs for errors
