from fastapi import APIRouter, HTTPException
from database.db import execute_query, fetch_one, fetch_all
from services.llm import QuestionGenerator, LLMService
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/{interview_id}/generate")
async def generate_questions(interview_id: int, num_questions: int = 10):
    """Generate interview questions based on resume and JD"""
    try:
        # Get interview details
        interview = fetch_one("SELECT * FROM interviews WHERE id = ?", (interview_id,))
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        # Get resume and JD
        resume = fetch_one("SELECT * FROM resumes WHERE id = ?", (interview['resume_id'],))
        jd = fetch_one("SELECT * FROM job_descriptions WHERE id = ?", (interview['jd_id'],))
        
        if not resume or not jd:
            raise HTTPException(status_code=404, detail="Resume or JD not found")
        
        # Parse resume data
        resume_data = {
            "skills": json.loads(resume['skills']) if resume['skills'] else [],
            "experience_years": resume['experience_years']
        }
        
        # Parse JD data
        jd_data = {
            "required_skills": json.loads(jd['required_skills']) if jd['required_skills'] else [],
            "required_experience_years": jd['required_experience_years']
        }
        
        # Generate questions
        questions = QuestionGenerator.generate_questions(resume_data, jd_data, num_questions)
        
        # Store questions in database
        stored_questions = []
        for idx, q in enumerate(questions, 1):
            query = '''
                INSERT INTO interview_questions 
                (interview_id, question_number, category, question, difficulty)
                VALUES (?, ?, ?, ?, ?)
            '''
            q_id = execute_query(
                query,
                (interview_id, idx, q['category'], q['question'], q['difficulty'])
            )
            q['id'] = q_id
            stored_questions.append(q)
        
        logger.info(f"Generated {len(questions)} questions for interview {interview_id}")
        
        return {
            "interview_id": interview_id,
            "questions_generated": len(questions),
            "questions": stored_questions
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating questions: {e}")
        raise HTTPException(status_code=400, detail=f"Error generating questions: {str(e)}")

@router.get("/{interview_id}")
async def get_interview_questions(interview_id: int):
    """Get all questions for an interview"""
    try:
        questions = fetch_all(
            "SELECT * FROM interview_questions WHERE interview_id = ? ORDER BY question_number",
            (interview_id,)
        )
        
        if not questions:
            raise HTTPException(status_code=404, detail="No questions found for this interview")
        
        return {
            "interview_id": interview_id,
            "total_questions": len(questions),
            "questions": [dict(q) for q in questions]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching questions: {e}")
        raise HTTPException(status_code=400, detail=f"Error fetching questions: {str(e)}")

@router.get("/{question_id}/details")
async def get_question(question_id: int):
    """Get a specific question"""
    try:
        question = fetch_one("SELECT * FROM interview_questions WHERE id = ?", (question_id,))
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        return dict(question)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching question: {e}")
        raise HTTPException(status_code=400, detail=f"Error fetching question: {str(e)}")

@router.get("/check/ollama")
async def check_ollama():
    """Check if Ollama is running"""
    is_running = LLMService.check_ollama_connection()
    
    if is_running:
        return {
            "status": "connected",
            "message": "Ollama is running",
            "url": "http://localhost:11434"
        }
    else:
        return {
            "status": "disconnected",
            "message": "Ollama is not running",
            "instructions": "Install Ollama from https://ollama.ai and run: ollama serve"
        }
