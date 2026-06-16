from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database.db import init_db
from routes import interview, resume, jd, feedback, questions, evaluation
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Mock Interview Application...")
    init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down application")

# Create FastAPI app
app = FastAPI(
    title="Mock Interview AI Agent",
    description="AI-powered mock interview platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(resume.router, prefix="/api/resume", tags=["Resume"])
app.include_router(jd.router, prefix="/api/jd", tags=["Job Description"])
app.include_router(interview.router, prefix="/api/interview", tags=["Interview"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["Feedback"])
app.include_router(questions.router, prefix="/api/questions", tags=["Questions"])
app.include_router(evaluation.router, prefix="/api/evaluation", tags=["Evaluation"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Mock Interview AI Agent",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
