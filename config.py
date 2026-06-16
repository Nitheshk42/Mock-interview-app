import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_PATH = os.getenv("DATABASE_PATH", "mock_interview.db")

# API Config
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# LLM Configuration (for Step 2)
# Support for free options
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # Options: ollama, groq, huggingface

# Ollama config (local, completely free)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")  # or llama2, neural-chat, etc.

# Groq config (free tier, requires API key)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# HuggingFace config (free tier)
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")

# Interview Configuration
INTERVIEW_QUESTIONS_PER_TYPE = {
    "full": 10,
    "behavioral": 6,
    "technical": 8,
    "hr": 5
}

DIFFICULTY_LEVELS = {
    "easy": 3,
    "medium": 5,
    "hard": 8
}

# Scoring Configuration (Step 2)
SCORING_WEIGHTS = {
    "communication": 0.20,
    "technical_depth": 0.30,
    "problem_solving": 0.20,
    "experience": 0.15,
    "confidence": 0.15
}

# Improvement Plan Configuration (Step 3)
DAILY_TASK_DURATION_MINUTES = 30  # Time to dedicate daily
IMPROVEMENT_DURATION_DAYS = 14  # Default improvement timeline

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
