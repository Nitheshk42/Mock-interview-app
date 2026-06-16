# Quick Start Guide - Step 1

## 1️⃣ Installation (2 minutes)

```bash
# Navigate to project
cd mock-interview-app

# Create virtual environment
python -m venv venv

# Activate it
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 2️⃣ Start the Server

```bash
python main.py
```

You should see:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete [uvicorn]
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 3️⃣ Test the API

Open in browser: **http://localhost:8000/docs**

This opens Swagger UI where you can test all endpoints.

## 4️⃣ Example Flow

### Step 1: Upload Resume
Click "Try it out" on `/api/resume/upload`

Body:
```json
{
  "user_id": 1,
  "file_name": "resume.txt",
  "content": "Senior Software Engineer with 8 years of experience. Expert in Python, JavaScript, React, Node.js, Docker, Kubernetes, AWS. Led teams of 5+ engineers. Built microservices handling 1M+ requests/day."
}
```

Click "Execute" → You'll get:
```json
{
  "id": 1,
  "user_id": 1,
  "skills": ["python", "javascript", "react", "node.js", "docker", "kubernetes", "aws"],
  "experience_years": 8.0
}
```

### Step 2: Upload Job Description
Click `/api/jd/upload`

Body:
```json
{
  "user_id": 1,
  "title": "Senior Backend Engineer",
  "company": "TechCorp",
  "content": "We're hiring a Senior Backend Engineer with 5+ years of experience. Required skills: Python, Django, PostgreSQL, AWS, Docker. You will architect microservices, optimize database queries, and mentor junior engineers. Experience with Kubernetes is a plus."
}
```

### Step 3: Start Interview
Click `/api/interview/start`

Body:
```json
{
  "user_id": 1,
  "resume_id": 1,
  "jd_id": 1,
  "interview_type": "full"
}
```

Response:
```json
{
  "interview_id": 1,
  "status": "in_progress",
  "message": "Interview started. Waiting for questions to be generated..."
}
```

### Step 4: Add Question
Click `/api/interview/{interview_id}/add-question`

Body:
```json
{
  "category": "behavioral",
  "question": "Tell me about a time when you had to optimize a slow database query. What was the problem, what did you do, and what were the results?",
  "expected_answer": "Should mention specific optimization techniques like indexing, query restructuring, or caching",
  "difficulty": 6
}
```

### Step 5: Submit Answer
Click `/api/interview/{interview_id}/submit-answer`

Body:
```json
{
  "question_id": 1,
  "answer": "We had a dashboard query taking 8 seconds. I analyzed the query plan, found we were doing 3 joins without proper indexes. Added composite indexes on user_id and timestamp. Used Redis for frequently accessed metrics. Reduced query time from 8s to 200ms. This improved user experience significantly and reduced database load by 40%.",
  "answer_duration_seconds": 45
}
```

### Step 6: Generate Feedback
Click `/api/feedback/{answer_id}`

Body:
```json
{
  "strengths": "Good technical specificity, mentioned multiple optimization techniques, included metrics",
  "weaknesses": "Could have mentioned testing after optimization",
  "model_answer": "Describe: problem identification, analysis approach, solution implementation, metrics/results, team communication",
  "real_world_examples": ["Query optimization at scale", "Monitoring improvements"],
  "improvement_suggestions": ["Always mention testing", "Include communication with team"],
  "final_score": 8.5
}
```

## 5️⃣ Verify It Works

You should be able to:
✅ Upload resume and see parsed skills
✅ Upload JD and see required skills
✅ Start an interview session
✅ Add questions
✅ Submit answers
✅ Generate feedback

## Troubleshooting

**Port 8000 already in use:**
```bash
python main.py --port 8001
```

**Database error:**
```bash
# Delete and recreate
rm mock_interview.db
python main.py
```

**Import errors:**
```bash
pip install -r requirements.txt --force-reinstall
```

## What's Working in Step 1 ✅

- ✅ Resume parsing (skills, experience extraction)
- ✅ JD parsing (required skills, experience)
- ✅ Database operations (CRUD)
- ✅ Interview session management
- ✅ Question/answer storage
- ✅ Feedback storage

## What's Coming in Step 2 🚀

- ❌ AI Question Generator (using free LLM)
- ❌ Smart Answer Evaluation & Scoring
- ❌ Detailed Feedback Generation
- ❌ Real-world Example Suggestions

---

**Next**: Once you confirm Step 1 works, reply with ✅ and we move to Step 2!
