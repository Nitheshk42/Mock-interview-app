from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ============ RESUME MODELS ============
class ResumeUpload(BaseModel):
    user_id: int
    content: str
    file_name: Optional[str] = None

class ResumeResponse(BaseModel):
    id: int
    user_id: int
    content: str
    skills: Optional[List[str]] = None
    experience_years: Optional[float] = None
    created_at: str

# ============ JOB DESCRIPTION MODELS ============
class JobDescriptionCreate(BaseModel):
    user_id: int
    title: str
    company: str
    content: str

class JobDescriptionResponse(BaseModel):
    id: int
    title: str
    company: str
    content: str
    required_skills: Optional[List[str]] = None
    required_experience_years: Optional[float] = None

# ============ USER MODELS ============
class UserCreate(BaseModel):
    email: str
    name: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    created_at: str

# ============ INTERVIEW MODELS ============
class InterviewStart(BaseModel):
    user_id: int
    resume_id: int
    jd_id: int
    interview_type: str = "full"  # full, technical, behavioral, hr

class InterviewQuestion(BaseModel):
    question_number: int
    category: str  # behavioral, technical, situational, etc.
    question: str
    expected_answer: str
    difficulty: float = 5.0  # 1-10 scale

class InterviewResponse(BaseModel):
    id: int
    user_id: int
    resume_id: int
    jd_id: int
    interview_type: str
    status: str
    total_score: float
    started_at: str
    completed_at: Optional[str] = None
    questions: Optional[List[InterviewQuestion]] = None

# ============ ANSWER MODELS ============
class CandidateAnswerSubmit(BaseModel):
    question_id: int
    answer: str
    answer_duration_seconds: Optional[int] = None

class CandidateAnswerResponse(BaseModel):
    id: int
    question_id: int
    answer: str
    answer_duration_seconds: Optional[int] = None
    raw_score: Optional[float] = None
    answered_at: str

# ============ FEEDBACK MODELS ============
class FeedbackResponse(BaseModel):
    id: int
    answer_id: int
    strengths: str
    weaknesses: str
    model_answer: str
    real_world_examples: str
    improvement_suggestions: str
    final_score: float
    created_at: str

# ============ IMPROVEMENT PLAN MODELS ============
class ImprovementPlanResponse(BaseModel):
    id: int
    user_id: int
    interview_id: int
    weak_areas: List[str]
    daily_tasks: List[str]
    resources: List[str]
    estimated_days_to_improve: int
    created_at: str

class DailyImprovementTask(BaseModel):
    day: int
    task: str
    duration_minutes: int
    resources: List[str]
    description: str
