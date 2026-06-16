from fastapi import APIRouter, HTTPException
from models import ResumeUpload, ResumeResponse
from database.db import execute_query, fetch_one, fetch_all
from services.parser import ResumeParser
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/upload")
async def upload_resume(resume: ResumeUpload) -> ResumeResponse:
    """Upload and parse resume"""
    try:
        # Parse resume
        parsed_data = ResumeParser.parse_resume(resume.content)
        
        # Convert lists to JSON strings for storage
        skills_json = json.dumps(parsed_data['skills'])
        
        # Insert into database
        query = '''
            INSERT INTO resumes (user_id, content, file_name, skills, experience_years)
            VALUES (?, ?, ?, ?, ?)
        '''
        resume_id = execute_query(
            query,
            (
                resume.user_id,
                resume.content,
                resume.file_name,
                skills_json,
                parsed_data['experience_years']
            )
        )
        
        logger.info(f"Resume {resume_id} uploaded for user {resume.user_id}")
        
        return ResumeResponse(
            id=resume_id,
            user_id=resume.user_id,
            content=resume.content,
            skills=parsed_data['skills'],
            experience_years=parsed_data['experience_years'],
            created_at=str(__import__('datetime').datetime.now())
        )
    
    except Exception as e:
        logger.error(f"Error uploading resume: {e}")
        raise HTTPException(status_code=400, detail=f"Error uploading resume: {str(e)}")

@router.get("/{resume_id}")
async def get_resume(resume_id: int) -> ResumeResponse:
    """Get resume by ID"""
    try:
        result = fetch_one("SELECT * FROM resumes WHERE id = ?", (resume_id,))
        
        if not result:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        skills = json.loads(result['skills']) if result['skills'] else []
        
        return ResumeResponse(
            id=result['id'],
            user_id=result['user_id'],
            content=result['content'],
            skills=skills,
            experience_years=result['experience_years'],
            created_at=result['created_at']
        )
    
    except Exception as e:
        logger.error(f"Error fetching resume: {e}")
        raise HTTPException(status_code=400, detail=f"Error fetching resume: {str(e)}")

@router.get("/user/{user_id}")
async def get_user_resumes(user_id: int):
    """Get all resumes for a user"""
    try:
        results = fetch_all("SELECT * FROM resumes WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        
        resumes = []
        for result in results:
            skills = json.loads(result['skills']) if result['skills'] else []
            resumes.append(ResumeResponse(
                id=result['id'],
                user_id=result['user_id'],
                content=result['content'],
                skills=skills,
                experience_years=result['experience_years'],
                created_at=result['created_at']
            ))
        
        return {"count": len(resumes), "resumes": resumes}
    
    except Exception as e:
        logger.error(f"Error fetching user resumes: {e}")
        raise HTTPException(status_code=400, detail=f"Error fetching resumes: {str(e)}")

@router.delete("/{resume_id}")
async def delete_resume(resume_id: int):
    """Delete a resume"""
    try:
        execute_query("DELETE FROM resumes WHERE id = ?", (resume_id,))
        return {"message": "Resume deleted successfully"}
    
    except Exception as e:
        logger.error(f"Error deleting resume: {e}")
        raise HTTPException(status_code=400, detail=f"Error deleting resume: {str(e)}")
