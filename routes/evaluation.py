from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database.db import execute_query, fetch_one, fetch_all
from services.llm import AnswerEvaluator
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class EvaluateAnswerRequest(BaseModel):
    question_id: int
    answer: str

@router.post("/{answer_id}/evaluate")
async def evaluate_answer(answer_id: int, evaluate_req: EvaluateAnswerRequest):
    """Evaluate a candidate's answer"""
    try:
        # Get answer
        answer = fetch_one("SELECT * FROM candidate_answers WHERE id = ?", (answer_id,))
        if not answer:
            raise HTTPException(status_code=404, detail="Answer not found")
        
        # Get question
        question = fetch_one("SELECT * FROM interview_questions WHERE id = ?", (answer['question_id'],))
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Evaluate
        evaluation = AnswerEvaluator.evaluate_answer(
            question['question'],
            answer['answer']
        )
        
        # Store evaluation in feedback table
        query = '''
            INSERT INTO feedback 
            (answer_id, strengths, weaknesses, model_answer, real_world_examples, improvement_suggestions, final_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        
        feedback_id = execute_query(
            query,
            (
                answer_id,
                json.dumps(evaluation['strengths']),
                json.dumps(evaluation['weaknesses']),
                json.dumps(evaluation['model_answer']),
                json.dumps(evaluation['improvement_suggestions']),
                json.dumps(evaluation['improvement_suggestions']),
                evaluation['final_score']
            )
        )
        
        # Update answer with score
        execute_query(
            "UPDATE candidate_answers SET raw_score = ? WHERE id = ?",
            (evaluation['final_score'], answer_id)
        )
        
        logger.info(f"Evaluated answer {answer_id} with score {evaluation['final_score']}")
        
        return {
            "answer_id": answer_id,
            "feedback_id": feedback_id,
            "evaluation": evaluation
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error evaluating answer: {e}")
        raise HTTPException(status_code=400, detail=f"Error evaluating answer: {str(e)}")

@router.get("/answer/{answer_id}")
async def get_answer_with_evaluation(answer_id: int):
    """Get answer with evaluation"""
    try:
        answer = fetch_one("SELECT * FROM candidate_answers WHERE id = ?", (answer_id,))
        if not answer:
            raise HTTPException(status_code=404, detail="Answer not found")
        
        feedback = fetch_one("SELECT * FROM feedback WHERE answer_id = ?", (answer_id,))
        
        result = {
            "answer_id": answer['id'],
            "question_id": answer['question_id'],
            "answer": answer['answer'],
            "score": answer['raw_score'],
            "answered_at": answer['answered_at']
        }
        
        if feedback:
            result["feedback"] = {
                "strengths": json.loads(feedback['strengths']) if feedback['strengths'] else [],
                "weaknesses": json.loads(feedback['weaknesses']) if feedback['weaknesses'] else [],
                "suggestions": json.loads(feedback['improvement_suggestions']) if feedback['improvement_suggestions'] else [],
                "final_score": feedback['final_score']
            }
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching answer: {e}")
        raise HTTPException(status_code=400, detail=f"Error fetching answer: {str(e)}")

@router.get("/interview/{interview_id}/summary")
async def get_interview_evaluation_summary(interview_id: int):
    """Get evaluation summary for interview"""
    try:
        # Get all answers for interview
        answers = fetch_all(
            '''SELECT ca.* FROM candidate_answers ca
               JOIN interview_questions iq ON ca.question_id = iq.id
               WHERE iq.interview_id = ?''',
            (interview_id,)
        )
        
        if not answers:
            return {
                "interview_id": interview_id,
                "total_answers": 0,
                "summary": None
            }
        
        total_score = sum(a['raw_score'] or 0 for a in answers) / len(answers)
        
        # Get all feedback
        feedback_list = fetch_all(
            '''SELECT f.* FROM feedback f
               JOIN candidate_answers ca ON f.answer_id = ca.id
               JOIN interview_questions iq ON ca.question_id = iq.id
               WHERE iq.interview_id = ?''',
            (interview_id,)
        )
        
        # Aggregate strengths and weaknesses
        all_strengths = []
        all_weaknesses = []
        all_suggestions = []
        
        for fb in feedback_list:
            if fb['strengths']:
                all_strengths.extend(json.loads(fb['strengths']))
            if fb['weaknesses']:
                all_weaknesses.extend(json.loads(fb['weaknesses']))
            if fb['improvement_suggestions']:
                all_suggestions.extend(json.loads(fb['improvement_suggestions']))
        
        # Remove duplicates and get top items
        all_strengths = list(set(all_strengths))[:5]
        all_weaknesses = list(set(all_weaknesses))[:5]
        all_suggestions = list(set(all_suggestions))[:5]
        
        return {
            "interview_id": interview_id,
            "total_answers": len(answers),
            "average_score": round(total_score, 2),
            "summary": {
                "top_strengths": all_strengths,
                "areas_for_improvement": all_weaknesses,
                "action_items": all_suggestions
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting evaluation summary: {e}")
        raise HTTPException(status_code=400, detail=f"Error getting summary: {str(e)}")
