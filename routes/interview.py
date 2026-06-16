from fastapi import APIRouter, HTTPException
from models import InterviewStart, InterviewResponse, CandidateAnswerSubmit
from database.db import execute_query, fetch_one, fetch_all
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/start")
async def start_interview(interview_req: InterviewStart):
    """Start a new interview session"""
    try:
        # Validate resume and JD exist
        resume = fetch_one("SELECT id FROM resumes WHERE id = ?", (interview_req.resume_id,))
        jd = fetch_one("SELECT id FROM job_descriptions WHERE id = ?", (interview_req.jd_id,))
        
        if not resume or not jd:
            raise HTTPException(status_code=404, detail="Resume or JD not found")
        
        # Create interview record
        query = '''
            INSERT INTO interviews (user_id, resume_id, jd_id, interview_type, status)
            VALUES (?, ?, ?, ?, 'in_progress')
        '''
        interview_id = execute_query(
            query,
            (interview_req.user_id, interview_req.resume_id, interview_req.jd_id, interview_req.interview_type)
        )
        
        logger.info(f"Interview {interview_id} started for user {interview_req.user_id}")
        
        return {
            "interview_id": interview_id,
            "status": "in_progress",
            "message": "Interview started. Waiting for questions to be generated..."
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting interview: {e}")
        raise HTTPException(status_code=400, detail=f"Error starting interview: {str(e)}")

@router.get("/{interview_id}")
async def get_interview(interview_id: int):
    """Get interview details"""
    try:
        result = fetch_one("SELECT * FROM interviews WHERE id = ?", (interview_id,))
        
        if not result:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        # Fetch questions
        questions = fetch_all(
            "SELECT * FROM interview_questions WHERE interview_id = ? ORDER BY question_number",
            (interview_id,)
        )
        
        return {
            "id": result['id'],
            "user_id": result['user_id'],
            "resume_id": result['resume_id'],
            "jd_id": result['jd_id'],
            "interview_type": result['interview_type'],
            "status": result['status'],
            "total_score": result['total_score'],
            "started_at": result['started_at'],
            "completed_at": result['completed_at'],
            "questions_count": len(questions)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching interview: {e}")
        raise HTTPException(status_code=400, detail=f"Error fetching interview: {str(e)}")

@router.post("/{interview_id}/add-question")
async def add_question(interview_id: int, question_data: dict):
    """Add a question to interview"""
    try:
        # Verify interview exists
        interview = fetch_one("SELECT id FROM interviews WHERE id = ?", (interview_id,))
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        # Get next question number
        last_q = fetch_one(
            "SELECT MAX(question_number) as max_q FROM interview_questions WHERE interview_id = ?",
            (interview_id,)
        )
        next_num = (last_q['max_q'] or 0) + 1
        
        query = '''
            INSERT INTO interview_questions 
            (interview_id, question_number, category, question, expected_answer, difficulty)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        
        q_id = execute_query(
            query,
            (
                interview_id,
                next_num,
                question_data.get('category', 'general'),
                question_data['question'],
                question_data.get('expected_answer', ''),
                question_data.get('difficulty', 5.0)
            )
        )
        
        logger.info(f"Question {q_id} added to interview {interview_id}")
        
        return {
            "question_id": q_id,
            "question_number": next_num,
            "status": "added"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding question: {e}")
        raise HTTPException(status_code=400, detail=f"Error adding question: {str(e)}")

@router.post("/{interview_id}/submit-answer")
async def submit_answer(interview_id: int, answer: CandidateAnswerSubmit):
    """Submit answer to interview question"""
    try:
        # Verify question belongs to interview
        question = fetch_one(
            '''SELECT iq.id, iq.interview_id 
               FROM interview_questions iq 
               WHERE iq.id = ? AND iq.interview_id = ?''',
            (answer.question_id, interview_id)
        )
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found in this interview")
        
        # Insert answer
        query = '''
            INSERT INTO candidate_answers (question_id, answer, answer_duration_seconds)
            VALUES (?, ?, ?)
        '''
        
        answer_id = execute_query(
            query,
            (answer.question_id, answer.answer, answer.answer_duration_seconds)
        )
        
        logger.info(f"Answer {answer_id} submitted for question {answer.question_id}")
        
        return {
            "answer_id": answer_id,
            "question_id": answer.question_id,
            "status": "submitted"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting answer: {e}")
        raise HTTPException(status_code=400, detail=f"Error submitting answer: {str(e)}")

@router.post("/{interview_id}/complete")
async def complete_interview(interview_id: int):
    """Mark interview as complete and calculate final score"""
    try:
        interview = fetch_one("SELECT * FROM interviews WHERE id = ?", (interview_id,))
        
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        # Calculate average score from all answers
        scores = fetch_all(
            '''SELECT raw_score FROM candidate_answers ca
               JOIN interview_questions iq ON ca.question_id = iq.id
               WHERE iq.interview_id = ? AND ca.raw_score IS NOT NULL''',
            (interview_id,)
        )
        
        avg_score = sum(s['raw_score'] for s in scores) / len(scores) if scores else 0
        
        # Update interview
        execute_query(
            '''UPDATE interviews 
               SET status = 'completed', total_score = ?, completed_at = CURRENT_TIMESTAMP
               WHERE id = ?''',
            (avg_score, interview_id)
        )
        
        logger.info(f"Interview {interview_id} completed with score {avg_score}")
        
        return {
            "interview_id": interview_id,
            "status": "completed",
            "total_score": avg_score
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing interview: {e}")
        raise HTTPException(status_code=400, detail=f"Error completing interview: {str(e)}")
