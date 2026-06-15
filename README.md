# Mock Interview AI Agent - Backend (Step 1)

A Python FastAPI backend for an AI-powered mock interview application.

## What's Included in Step 1

✅ **Core Backend Structure**
- FastAPI application with proper routing
- SQLite database with complete schema
- Resume & JD parser (skills, experience extraction)
- API endpoints for resume/JD management
- Interview session management
- Answer submission framework
- Feedback storage system

✅ **Database Models** (8 Tables)
- Users
- Resumes (with parsed skills & experience)
- Job Descriptions (with required skills)
- Interviews (session tracking)
- Interview Questions
- Candidate Answers
- Feedback (for each answer)
- Improvement Plans (prepared for Step 2)

✅ **API Endpoints**

**Resume Management:**
- `POST /api/resume/upload` - Upload & parse resume
- `GET /api/resume/{resume_id}` - Get resume details
- `GET /api/resume/user/{user_id}` - Get all user resumes
- `DELETE /api/resume/{resume_id}` - Delete resume

**Job Description Management:**
- `POST /api/jd/upload` - Upload & parse JD
- `GET /api/jd/{jd_id}` - Get JD details
- `GET /api/jd/user/{user_id}` - Get all user JDs
- `DELETE /api/jd/{jd_id}` - Delete JD

**Interview Management:**
- `POST /api/interview/start` - Start new interview
- `GET /api/interview/{interview_id}` - Get interview status
- `POST /api/interview/{interview_id}/add-question` - Add question
- `POST /api/interview/{interview_id}/submit-answer` - Submit answer
- `POST /api/interview/{interview_id}/complete` - Complete interview

**Feedback Management:**
- `POST /api/feedback/{answer_id}` - Generate feedback
- `GET /api/feedback/{answer_id}` - Get feedback
- `GET /api/feedback/interview/{interview_id}` - Get all feedback
- `GET /api/feedback/user/{user_id}/summary` - Get summary

## Project Structure

```
mock-interview-app/
├── main.py                      # FastAPI app entry point
├── models.py                    # Pydantic models
├── requirements.txt
├── README.md
├── database/
│   └── db.py                   # SQLite setup & queries
├── services/
│   └── parser.py               # Resume & JD parsing
└── routes/
    ├── resume.py               # Resume endpoints
    ├── jd.py                   # JD endpoints
    ├── interview.py            # Interview endpoints
    └── feedback.py             # Feedback endpoints
```

## Installation & Setup

### 1. Create Virtual Environment
```bash
cd mock-interview-app
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Run the Application
```bash
python main.py
```

Server will start at `http://localhost:8000`

### 4. API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Database

SQLite database (`mock_interview.db`) is created automatically on first run.

To reset database, delete `mock_interview.db` and restart.

## Testing Step 1

### Example: Create User & Upload Resume

```bash
# In routes, add a user endpoint first, or use:
curl -X POST "http://localhost:8000/api/resume/upload" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "file_name": "my_resume.txt",
    "content": "Senior Software Engineer with 5 years of experience in Python, React, Docker, AWS..."
  }'
```

### Response:
```json
{
  "id": 1,
  "user_id": 1,
  "content": "Senior Software Engineer with 5 years...",
  "skills": ["python", "react", "docker", "aws"],
  "experience_years": 5.0,
  "created_at": "2024-01-15T10:30:00"
}
```

## Next Steps (Step 2)

After you confirm Step 1 is working:

1. ✅ Question Generator (using free LLM)
2. Answer Evaluator & Scorer
3. Improvement Engine
4. Daily Task Generator

## Notes

- Resume parser uses regex patterns (works offline)
- Database uses SQLite (no setup needed)
- All dependencies are free/open-source
- Ready to integrate with free LLMs in Step 2

## Next: Confirm Step 1 Complete ✅

Please test the endpoints above and let me know:
1. Did the server start successfully?
2. Can you upload a resume?
3. Can you upload a JD?
4. Any errors?

Then we'll move to **Step 2: Question Generator** 🚀
