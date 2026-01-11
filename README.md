# Clinical Trial Eligibility Screening System

A web application for clinical coordinators to screen patients for Type 2 Diabetes clinical trial eligibility.

## 🏥 Features

- **Trial Management**: CRUD operations for clinical trials with inclusion/exclusion criteria
- **Patient Screening**: Form-based and JSON input for patient data
- **Eligibility Engine**: Rule-based evaluation with decision logic
- **AI Explanations**: Gemini-powered Hebrew explanations
- **Batch Processing**: CSV/JSON upload for multiple patients
- **Audit Trail**: Complete history of all screenings

## 🛠️ Tech Stack

- **Backend**: Python 3.11+ / FastAPI
- **Frontend**: React 18 / TypeScript / Vite
- **Database**: SQLite
- **AI**: Google Gemini API
- **Styling**: Tailwind CSS (RTL support)
- **Deployment**: Docker + Google Cloud Run

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (optional)

### Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Add your Gemini API key to .env
GEMINI_API_KEY=your_key_here
```

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker-compose up --build
```

## 📁 Project Structure

```
clinical-trial-screening/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── database.py          # Database connection
│   │   ├── eligibility_engine.py # Core logic
│   │   ├── gemini_client.py     # AI integration
│   │   └── routers/             # API routes
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── services/            # API client
│   │   └── types/               # TypeScript types
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🧪 Sample Data

The application comes pre-loaded with:
- **Trial**: DM2-2024-001 (Type 2 Diabetes Phase III)
- **8 Test Patients** with varying eligibility statuses

## 📝 License

MIT License
