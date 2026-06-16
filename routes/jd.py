from fastapi import APIRouter, HTTPException
from models import JobDescriptionCreate, JobDescriptionResponse
from database.db import execute_query, fetch_one, fetch_all
from services.parser import JDParser
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/upload")
async def upload_jd(jd: JobDescriptionCreate) -> JobDescriptionResponse:
    """Upload and parse job description"""
    try:
        # Parse JD
        parsed_data = JDParser.parse_jd(jd.content)
        
        # Convert lists to JSON strings for storage
        skills_json = json.dumps(parsed_data['required_skills'])
        
        # Insert into database
        query = '''
            INSERT INTO job_descriptions (user_id, title, company, content, required_skills, required_experience_years)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        jd_id = execute_query(
            query,
            (
                jd.user_id,
                jd.title,
                jd.company,
                jd.content,
                skills_json,
                parsed_data['required_experience_years']
            )
        )
        
        logger.info(f"JD {jd_id} uploaded for user {jd.user_id}")
        
        return JobDescriptionResponse(
            id=jd_id,
            title=jd.title,
            company=jd.company,
            content=jd.content,
            required_skills=parsed_data['required_skills'],
            required_experience_years=parsed_data['required_experience_years']
        )
    
    except Exception as e:
        logger.error(f"Error uploading JD: {e}")
        raise HTTPException(status_code=400, detail=f"Error uploading JD: {str(e)}")

@router.get("/{jd_id}")
async def get_jd(jd_id: int) -> JobDescriptionResponse:
    """Get JD by ID"""
    try:
        result = fetch_one("SELECT * FROM job_descriptions WHERE id = ?", (jd_id,))
        
        if not result:
            raise HTTPException(status_code=404, detail="Job description not found")
        
        skills = json.loads(result['required_skills']) if result['required_skills'] else []
        
        return JobDescriptionResponse(
            id=result['id'],
            title=result['title'],
            company=result['company'],
            content=result['content'],
            required_skills=skills,
            required_experience_years=result['required_experience_years']
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching JD: {e}")
        raise HTTPException(status_code=400, detail=f"Error fetching JD: {str(e)}")

@router.get("/user/{user_id}")
async def get_user_jds(user_id: int):
    """Get all JDs for a user"""
    try:
        results = fetch_all(
            "SELECT * FROM job_descriptions WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        
        jds = []
        for result in results:
            skills = json.loads(result['required_skills']) if result['required_skills'] else []
            jds.append(JobDescriptionResponse(
                id=result['id'],
                title=result['title'],
                company=result['company'],
                content=result['content'],
                required_skills=skills,
                required_experience_years=result['required_experience_years']
            ))
        
        return {"count": len(jds), "job_descriptions": jds}
    
    except Exception as e:
        logger.error(f"Error fetching user JDs: {e}")
        raise HTTPException(status_code=400, detail=f"Error fetching JDs: {str(e)}")

@router.delete("/{jd_id}")
async def delete_jd(jd_id: int):
    """Delete a JD"""
    try:
        execute_query("DELETE FROM job_descriptions WHERE id = ?", (jd_id,))
        return {"message": "Job description deleted successfully"}
    
    except Exception as e:
        logger.error(f"Error deleting JD: {e}")
        raise HTTPException(status_code=400, detail=f"Error deleting JD: {str(e)}")
