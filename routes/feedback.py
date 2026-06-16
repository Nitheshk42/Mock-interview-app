from fastapi import APIRouter, HTTPException
from models import FeedbackResponse
from database.db import execute_query, fetch_one, fetch_all
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/{answer_id}")
async def generate_feedback(answer_id: int, feedback_data: dict):
    """Generate and store feedback for an answer"""
    try:
        # Verify answer exists
        answer = fetch_one("SELECT * FROM candidate_answers WHERE id = ?", (answer_id,))
        if not answer:
            raise HTTPException(status_code=404, detail="Answer not found")
        
        # Insert feedback
        query = '''
            INSERT INTO feedback 
            (answer_id, strengths, weaknesses, model_answer, real_world_examples, improvement_suggestions, final_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        
        feedback_id = execute_query(
            query,
            (
                answer_id,
                feedback_data.get('strengths', ''),
                feedback_data.get('weaknesses', ''),
                feedback_data.get('model_answer', ''),
                json.dumps(feedback_data.get('real_world_examples', [])),
                json.dumps(feedback_data.get('improvement_suggestions', [])),
                feedback_data.get('final_score', 0)
            )
        )
        
        # Update answer with raw score
        execute_query(
            "UPDATE candidate_answers SET raw_score = ? WHERE id = ?",
            (feedback_data.get('final_score', 0), answer_id)
        )
        
        logger.info(f"Feedback {feedback_id} generated for answer {answer_id}")
        
        return {
            "feedback_id": feedback_id,
            "answer_id": answer_id,
            "status": "generated"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating feedback: {e}")
        raise HTTPException(status_code=400, detail=f"Error generating feedback: {str(e)}")

@router.get("/{answer_id}")
async def get_feedback(answer_id: int) -> FeedbackResponse:
    """Get feedback for an answer"""
    try:
        result = fetch_one("SELECT * FROM feedback WHERE answer_id = ?", (answer_id,))
        
        if not result:
            raise HTTPException(status_code=404, detail="Feedback not found")
        
        examples = json.loads(result['real_world_examples']) if result['real_world_examples'] else []
        suggestions = json.loads(result['improvement_suggestions']) if result['improvement_suggestions'] else []
        
        return FeedbackResponse(
            id=result['id'],
            answer_id=result['answer_id'],
            strengths=result['strengths'],
            weaknesses=result['weaknesses'],
            model_answer=result['model_answer'],
            real_world_examples=json.dumps(examples),
            improvement_suggestions=json.dumps(suggestions),
            final_score=result['final_score'],
            created_at=result['created_at']
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching feedback: {e}")
        raise HTTPException(status_code=400, detail=f"Error fetching feedback: {str(e)}")

@router.get("/interview/{interview_id}")
async def get_interview_feedback(interview_id: int):
    """Get all feedback for an interview"""
    try:
        results = fetch_all(
            '''SELECT f.* FROM feedback f
               JOIN candidate_answers ca ON f.answer_id = ca.id
               JOIN interview_questions iq ON ca.question_id = iq.id
               WHERE iq.interview_id = ?
               ORDER BY f.created_at''',
            (interview_id,)
        )
        
        feedback_list = []
        for result in results:
            examples = json.loads(result['real_world_examples']) if result['real_world_examples'] else []
            suggestions = json.loads(result['improvement_suggestions']) if result['improvement_suggestions'] else []
            
            feedback_list.append({
                "id": result['id'],
                "answer_id": result['answer_id'],
                "strengths": result['strengths'],
                "weaknesses": result['weaknesses'],
                "model_answer": result['model_answer'],
                "real_world_examples": examples,
                "improvement_suggestions": suggestions,
                "final_score": result['final_score'],
                "created_at": result['created_at']
            })
        
        # Calculate average score
        avg_score = sum(f['final_score'] for f in feedback_list) / len(feedback_list) if feedback_list else 0
        
        return {
            "interview_id": interview_id,
            "total_feedback": len(feedback_list),
            "average_score": round(avg_score, 2),
            "feedback": feedback_list
        }
    
    except Exception as e:
        logger.error(f"Error fetching interview feedback: {e}")
        raise HTTPException(status_code=400, detail=f"Error fetching feedback: {str(e)}")

@router.get("/user/{user_id}/summary")
async def get_user_feedback_summary(user_id: int):
    """Get feedback summary for all interviews of a user"""
    try:
        interviews = fetch_all(
            "SELECT id, interview_type, total_score FROM interviews WHERE user_id = ? ORDER BY completed_at DESC",
            (user_id,)
        )
        
        summary = []
        for interview in interviews:
            feedback_count = fetch_one(
                '''SELECT COUNT(*) as count FROM feedback f
                   JOIN candidate_answers ca ON f.answer_id = ca.id
                   JOIN interview_questions iq ON ca.question_id = iq.id
                   WHERE iq.interview_id = ?''',
                (interview['id'],)
            )
            
            summary.append({
                "interview_id": interview['id'],
                "interview_type": interview['interview_type'],
                "total_score": interview['total_score'],
                "feedback_count": feedback_count['count']
            })
        
        return {
            "user_id": user_id,
            "total_interviews": len(summary),
            "interviews": summary
        }
    
    except Exception as e:
        logger.error(f"Error fetching user feedback summary: {e}")
        raise HTTPException(status_code=400, detail=f"Error fetching feedback: {str(e)}")
