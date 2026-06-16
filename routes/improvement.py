from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database.db import execute_query, fetch_one, fetch_all
from services.improvement import ImprovementPlanGenerator, WeeklyProgressTracker
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

class GeneratePlanRequest(BaseModel):
    interview_id: int
    days: int = 14

class MarkTaskCompleteRequest(BaseModel):
    task_day: int

@router.post("/generate")
async def generate_improvement_plan(request: GeneratePlanRequest):
    """Generate personalized improvement plan based on interview"""
    try:
        # Get interview evaluation summary
        interview = fetch_one("SELECT * FROM interviews WHERE id = ?", (request.interview_id,))
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        # Get evaluation summary
        feedbacks = fetch_all(
            '''SELECT f.* FROM feedback f
               JOIN candidate_answers ca ON f.answer_id = ca.id
               JOIN interview_questions iq ON ca.question_id = iq.id
               WHERE iq.interview_id = ?''',
            (request.interview_id,)
        )
        
        if not feedbacks:
            raise HTTPException(status_code=400, detail="No evaluations found for interview")
        
        # Build interview summary
        all_weaknesses = []
        all_suggestions = []
        total_score = 0
        
        for fb in feedbacks:
            if fb['weaknesses']:
                weaknesses = json.loads(fb['weaknesses'])
                all_weaknesses.extend(weaknesses)
            if fb['improvement_suggestions']:
                suggestions = json.loads(fb['improvement_suggestions'])
                all_suggestions.extend(suggestions)
            total_score += fb['final_score']
        
        avg_score = total_score / len(feedbacks) if feedbacks else 0
        
        interview_summary = {
            "areas_for_improvement": list(set(all_weaknesses))[:5],
            "action_items": list(set(all_suggestions))[:5],
            "average_score": avg_score,
            "scores": {}
        }
        
        # Generate improvement plan
        improvement_plan = ImprovementPlanGenerator.generate_plan(interview_summary, request.days)
        
        # Store plan in database
        query = '''
            INSERT INTO improvement_plans 
            (user_id, interview_id, weak_areas, daily_tasks, resources, estimated_days_to_improve)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        
        plan_id = execute_query(
            query,
            (
                interview['user_id'],
                request.interview_id,
                json.dumps(improvement_plan['weak_areas']),
                json.dumps(improvement_plan['daily_tasks']),
                json.dumps(improvement_plan['resources']),
                request.days
            )
        )
        
        logger.info(f"Generated improvement plan {plan_id} for interview {request.interview_id}")
        
        return {
            "plan_id": plan_id,
            "interview_id": request.interview_id,
            "plan": improvement_plan
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating improvement plan: {e}")
        raise HTTPException(status_code=400, detail=f"Error generating plan: {str(e)}")

@router.get("/{plan_id}")
async def get_improvement_plan(plan_id: int):
    """Get improvement plan details"""
    try:
        plan = fetch_one("SELECT * FROM improvement_plans WHERE id = ?", (plan_id,))
        
        if not plan:
            raise HTTPException(status_code=404, detail="Improvement plan not found")
        
        daily_tasks = json.loads(plan['daily_tasks']) if plan['daily_tasks'] else []
        resources = json.loads(plan['resources']) if plan['resources'] else {}
        weak_areas = json.loads(plan['weak_areas']) if plan['weak_areas'] else []
        
        return {
            "plan_id": plan['id'],
            "interview_id": plan['interview_id'],
            "weak_areas": weak_areas,
            "daily_tasks": daily_tasks,
            "resources": resources,
            "estimated_days": plan['estimated_days_to_improve'],
            "created_at": plan['created_at']
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching plan: {e}")
        raise HTTPException(status_code=400, detail=f"Error fetching plan: {str(e)}")

@router.get("/{plan_id}/today")
async def get_todays_task(plan_id: int):
    """Get today's task from the improvement plan"""
    try:
        plan = fetch_one("SELECT * FROM improvement_plans WHERE id = ?", (plan_id,))
        
        if not plan:
            raise HTTPException(status_code=404, detail="Improvement plan not found")
        
        daily_tasks = json.loads(plan['daily_tasks']) if plan['daily_tasks'] else []
        
        # Find today's task (day 1, then 2, etc.)
        # For now, return the first incomplete task
        for task in daily_tasks:
            if not task.get('completed', False):
                return {
                    "plan_id": plan_id,
                    "today_task": task,
                    "remaining_tasks": len([t for t in daily_tasks if not t.get('completed', False)])
                }
        
        return {
            "plan_id": plan_id,
            "message": "All tasks completed! Congratulations!",
            "remaining_tasks": 0
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching today's task: {e}")
        raise HTTPException(status_code=400, detail=f"Error fetching task: {str(e)}")

@router.post("/{plan_id}/mark-complete")
async def mark_task_complete(plan_id: int, request: MarkTaskCompleteRequest):
    """Mark a task as complete"""
    try:
        plan = fetch_one("SELECT * FROM improvement_plans WHERE id = ?", (plan_id,))
        
        if not plan:
            raise HTTPException(status_code=404, detail="Improvement plan not found")
        
        daily_tasks = json.loads(plan['daily_tasks']) if plan['daily_tasks'] else []
        
        # Mark task as complete
        for task in daily_tasks:
            if task['day'] == request.task_day:
                task['completed'] = True
                task['completed_at'] = datetime.now().isoformat()
                break
        
        # Update database
        execute_query(
            "UPDATE improvement_plans SET daily_tasks = ? WHERE id = ?",
            (json.dumps(daily_tasks), plan_id)
        )
        
        logger.info(f"Marked task {request.task_day} as complete for plan {plan_id}")
        
        # Calculate progress
        completed = sum(1 for t in daily_tasks if t.get('completed', False))
        
        return {
            "plan_id": plan_id,
            "task_day": request.task_day,
            "status": "completed",
            "progress": f"{completed}/{len(daily_tasks)}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking task complete: {e}")
        raise HTTPException(status_code=400, detail=f"Error updating task: {str(e)}")

@router.get("/{plan_id}/progress")
async def get_plan_progress(plan_id: int):
    """Get progress on improvement plan"""
    try:
        plan = fetch_one("SELECT * FROM improvement_plans WHERE id = ?", (plan_id,))
        
        if not plan:
            raise HTTPException(status_code=404, detail="Improvement plan not found")
        
        daily_tasks = json.loads(plan['daily_tasks']) if plan['daily_tasks'] else []
        
        # Count completed
        completed_tasks = [t for t in daily_tasks if t.get('completed', False)]
        
        # Group by category
        by_category = {}
        for task in daily_tasks:
            category = task['category']
            if category not in by_category:
                by_category[category] = {"total": 0, "completed": 0}
            by_category[category]["total"] += 1
            if task.get('completed', False):
                by_category[category]["completed"] += 1
        
        completion_rate = (len(completed_tasks) / len(daily_tasks) * 100) if daily_tasks else 0
        
        return {
            "plan_id": plan_id,
            "total_tasks": len(daily_tasks),
            "completed_tasks": len(completed_tasks),
            "completion_rate": round(completion_rate, 2),
            "by_category": by_category,
            "next_task": next((t for t in daily_tasks if not t.get('completed', False)), None)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching progress: {e}")
        raise HTTPException(status_code=400, detail=f"Error fetching progress: {str(e)}")

@router.get("/user/{user_id}/plans")
async def get_user_improvement_plans(user_id: int):
    """Get all improvement plans for a user"""
    try:
        plans = fetch_all(
            "SELECT * FROM improvement_plans WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        
        if not plans:
            return {"user_id": user_id, "plans": [], "total_plans": 0}
        
        plans_list = []
        for plan in plans:
            daily_tasks = json.loads(plan['daily_tasks']) if plan['daily_tasks'] else []
            completed = sum(1 for t in daily_tasks if t.get('completed', False))
            
            plans_list.append({
                "plan_id": plan['id'],
                "interview_id": plan['interview_id'],
                "created_at": plan['created_at'],
                "total_tasks": len(daily_tasks),
                "completed_tasks": completed,
                "estimated_days": plan['estimated_days_to_improve']
            })
        
        return {
            "user_id": user_id,
            "total_plans": len(plans_list),
            "plans": plans_list
        }
    
    except Exception as e:
        logger.error(f"Error fetching user plans: {e}")
        raise HTTPException(status_code=400, detail=f"Error fetching plans: {str(e)}")
