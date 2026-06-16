import requests
import json
import logging
from typing import List, Dict
import os

logger = logging.getLogger(__name__)

# Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

class LLMService:
    """Service to interact with local Ollama LLM"""
    
    @staticmethod
    def check_ollama_connection() -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama connection failed: {e}")
            return False
    
    @staticmethod
    def generate_text(prompt: str, max_tokens: int = 500) -> str:
        """Generate text using Ollama"""
        try:
            url = f"{OLLAMA_BASE_URL}/api/generate"
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.7,
            }
            
            response = requests.post(url, json=payload, timeout=60)
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                logger.error(f"Ollama error: {response.status_code}")
                return ""
        except Exception as e:
            logger.error(f"Text generation error: {e}")
            return ""

class QuestionGenerator:
    """Generate interview questions based on JD and Resume"""
    
    QUESTION_TEMPLATES = {
        "behavioral": [
            "Tell me about a time when you had to solve a {skill} problem. What was the challenge?",
            "Describe a situation where you had to work with {skill}. How did you approach it?",
            "Share an example of when you used {skill} to achieve a goal.",
            "Tell me about your experience with {skill}. What challenges did you face?"
        ],
        "technical": [
            "Explain how you would architect a system using {skill}.",
            "What are the key considerations when using {skill} in production?",
            "How would you optimize {skill} performance?",
            "Can you walk me through building something with {skill}?"
        ],
        "situational": [
            "If you had to debug a {skill} issue in production, what's your approach?",
            "How would you handle a {skill} migration in a legacy system?",
            "What would you do if a {skill} library you depend on became unmaintained?",
            "How would you teach {skill} to a junior engineer?"
        ],
        "hr": [
            "Why are you interested in this role?",
            "Where do you see yourself in 3 years?",
            "What's your biggest strength and weakness?",
            "Tell us about a time you failed and what you learned."
        ]
    }
    
    @staticmethod
    def generate_questions(resume_data: Dict, jd_data: Dict, num_questions: int = 10) -> List[Dict]:
        """Generate interview questions"""
        questions = []
        
        # Get skills from both resume and JD
        resume_skills = resume_data.get('skills', [])
        jd_skills = jd_data.get('required_skills', [])
        
        # Match skills
        matched_skills = [s for s in resume_skills if s in jd_skills]
        missing_skills = [s for s in jd_skills if s not in resume_skills]
        
        # Mix of question types
        question_distribution = {
            "behavioral": max(1, num_questions // 3),
            "technical": max(1, num_questions // 3),
            "situational": max(1, num_questions // 4),
            "hr": max(1, num_questions // 6)
        }
        
        question_count = 0
        
        # Behavioral questions on matched skills
        for skill in matched_skills[:question_distribution["behavioral"]]:
            template = QuestionGenerator.QUESTION_TEMPLATES["behavioral"][question_count % len(QuestionGenerator.QUESTION_TEMPLATES["behavioral"])]
            question = template.format(skill=skill)
            questions.append({
                "category": "behavioral",
                "question": question,
                "difficulty": 5,
                "focus_skill": skill
            })
            question_count += 1
        
        # Technical questions on matched and missing skills
        all_skills = matched_skills + missing_skills
        for skill in all_skills[:question_distribution["technical"]]:
            template = QuestionGenerator.QUESTION_TEMPLATES["technical"][question_count % len(QuestionGenerator.QUESTION_TEMPLATES["technical"])]
            question = template.format(skill=skill)
            difficulty = 6 if skill in missing_skills else 5
            questions.append({
                "category": "technical",
                "question": question,
                "difficulty": difficulty,
                "focus_skill": skill
            })
            question_count += 1
        
        # Situational questions
        for skill in matched_skills[:question_distribution["situational"]]:
            template = QuestionGenerator.QUESTION_TEMPLATES["situational"][question_count % len(QuestionGenerator.QUESTION_TEMPLATES["situational"])]
            question = template.format(skill=skill)
            questions.append({
                "category": "situational",
                "question": question,
                "difficulty": 6,
                "focus_skill": skill
            })
            question_count += 1
        
        # HR questions
        for i in range(question_distribution["hr"]):
            question = QuestionGenerator.QUESTION_TEMPLATES["hr"][i % len(QuestionGenerator.QUESTION_TEMPLATES["hr"])]
            questions.append({
                "category": "hr",
                "question": question,
                "difficulty": 4,
                "focus_skill": "general"
            })
            question_count += 1
        
        return questions[:num_questions]

class AnswerEvaluator:
    """Evaluate candidate answers"""
    
    SCORING_WEIGHTS = {
        "communication_clarity": 0.20,
        "technical_depth": 0.30,
        "problem_solving": 0.20,
        "relevant_experience": 0.15,
        "confidence_professionalism": 0.15
    }
    
    @staticmethod
    def evaluate_answer(question: str, answer: str, expected_answer: str = "") -> Dict:
        """Evaluate a candidate's answer"""
        
        evaluation = {
            "answer": answer,
            "scores": {},
            "feedback": {},
            "strengths": [],
            "weaknesses": [],
            "model_answer": "",
            "improvement_suggestions": []
        }
        
        # Score communication clarity (0-10)
        comm_score = AnswerEvaluator._score_communication(answer)
        evaluation["scores"]["communication_clarity"] = comm_score
        
        # Score technical depth (0-10)
        tech_score = AnswerEvaluator._score_technical_depth(answer, question)
        evaluation["scores"]["technical_depth"] = tech_score
        
        # Score problem solving (0-10)
        ps_score = AnswerEvaluator._score_problem_solving(answer)
        evaluation["scores"]["problem_solving"] = ps_score
        
        # Score relevant experience (0-10)
        exp_score = AnswerEvaluator._score_experience(answer)
        evaluation["scores"]["relevant_experience"] = exp_score
        
        # Score confidence (0-10)
        conf_score = AnswerEvaluator._score_confidence(answer)
        evaluation["scores"]["confidence_professionalism"] = conf_score
        
        # Calculate weighted final score
        final_score = sum(
            evaluation["scores"][key] * AnswerEvaluator.SCORING_WEIGHTS[key]
            for key in AnswerEvaluator.SCORING_WEIGHTS
        )
        evaluation["final_score"] = round(final_score, 2)
        
        # Generate feedback
        evaluation["strengths"] = AnswerEvaluator._get_strengths(evaluation["scores"])
        evaluation["weaknesses"] = AnswerEvaluator._get_weaknesses(evaluation["scores"])
        evaluation["improvement_suggestions"] = AnswerEvaluator._get_suggestions(evaluation["scores"])
        
        return evaluation
    
    @staticmethod
    def _score_communication(answer: str) -> float:
        """Score communication clarity (0-10)"""
        score = 5
        
        if len(answer) < 50:
            score -= 2
        elif len(answer) > 300:
            score += 1
        
        # Check for structure (sentences)
        sentences = [s for s in answer.split('.') if len(s.strip()) > 10]
        if len(sentences) >= 3:
            score += 1
        
        # Check for examples
        if any(word in answer.lower() for word in ['example', 'like', 'case', 'situation']):
            score += 1
        
        return min(10, max(0, score))
    
    @staticmethod
    def _score_technical_depth(answer: str, question: str) -> float:
        """Score technical depth (0-10)"""
        score = 4
        
        answer_lower = answer.lower()
        
        # Check for technical terms
        tech_keywords = ['algorithm', 'optimize', 'architecture', 'design', 'implementation', 
                        'performance', 'scalability', 'database', 'api', 'framework']
        keywords_found = sum(1 for kw in tech_keywords if kw in answer_lower)
        score += min(3, keywords_found * 0.5)
        
        # Check for specific details
        if any(word in answer_lower for word in ['milliseconds', 'seconds', 'mb', 'gb', 'percent', '%']):
            score += 1.5
        
        # Longer answers often indicate more depth
        if len(answer) > 200:
            score += 1
        
        return min(10, max(0, score))
    
    @staticmethod
    def _score_problem_solving(answer: str) -> float:
        """Score problem solving approach (0-10)"""
        score = 4
        
        answer_lower = answer.lower()
        
        # Check for problem understanding
        if any(word in answer_lower for word in ['problem', 'challenge', 'issue', 'difficult']):
            score += 1.5
        
        # Check for solution approach
        if any(word in answer_lower for word in ['approach', 'solution', 'method', 'strategy', 'steps']):
            score += 1.5
        
        # Check for outcomes/results
        if any(word in answer_lower for word in ['result', 'outcome', 'improved', 'reduced', 'increased', 'solved']):
            score += 1.5
        
        # Check for iteration/learning
        if any(word in answer_lower for word in ['tried', 'tested', 'learned', 'iterated', 'improved']):
            score += 0.5
        
        return min(10, max(0, score))
    
    @staticmethod
    def _score_experience(answer: str) -> float:
        """Score relevant experience (0-10)"""
        score = 3
        
        answer_lower = answer.lower()
        
        # Check for specific experience indicators
        if any(word in answer_lower for word in ['years', 'experience', 'worked', 'built', 'developed', 'led', 'managed']):
            score += 2
        
        # Check for tangible results
        if any(word in answer_lower for word in ['shipped', 'deployed', 'launched', 'released', 'production']):
            score += 2
        
        # Check for team/scale experience
        if any(word in answer_lower for word in ['team', 'led', 'managed', 'collaborated', 'users', 'customers']):
            score += 1.5
        
        # Check for specific technologies
        if any(word in answer_lower for word in ['python', 'javascript', 'java', 'react', 'node', 'django', 'aws', 'docker']):
            score += 1
        
        return min(10, max(0, score))
    
    @staticmethod
    def _score_confidence(answer: str) -> float:
        """Score confidence and professionalism (0-10)"""
        score = 5
        
        answer_lower = answer.lower()
        
        # Check for uncertain language
        uncertain_words = ['maybe', 'might', 'probably', 'i think', 'sort of', 'kind of', 'um', 'uh']
        uncertain_count = sum(1 for word in uncertain_words if word in answer_lower)
        score -= min(2, uncertain_count * 0.3)
        
        # Check for professional language
        if any(word in answer_lower for word in ['delivered', 'architected', 'optimized', 'scaled', 'mentored']):
            score += 1.5
        
        # Length and structure indicate confidence
        if len(answer) > 150 and answer.count('.') >= 3:
            score += 1
        
        return min(10, max(0, score))
    
    @staticmethod
    def _get_strengths(scores: Dict) -> List[str]:
        """Get strengths based on scores"""
        strengths = []
        
        for criterion, score in scores.items():
            if score >= 7:
                strength_map = {
                    "communication_clarity": "Clear and articulate communication",
                    "technical_depth": "Strong technical understanding",
                    "problem_solving": "Good problem-solving approach",
                    "relevant_experience": "Relevant and applicable experience",
                    "confidence_professionalism": "Confident and professional delivery"
                }
                strengths.append(strength_map.get(criterion, criterion))
        
        return strengths if strengths else ["Good foundation to build upon"]
    
    @staticmethod
    def _get_weaknesses(scores: Dict) -> List[str]:
        """Get weaknesses based on scores"""
        weaknesses = []
        
        for criterion, score in scores.items():
            if score < 5:
                weakness_map = {
                    "communication_clarity": "Could improve clarity and structure",
                    "technical_depth": "Need more technical details and examples",
                    "problem_solving": "Work on explaining problem-solving process",
                    "relevant_experience": "Provide more specific project examples",
                    "confidence_professionalism": "Build confidence in your response"
                }
                weaknesses.append(weakness_map.get(criterion, criterion))
        
        return weaknesses if weaknesses else []
    
    @staticmethod
    def _get_suggestions(scores: Dict) -> List[str]:
        """Get improvement suggestions"""
        suggestions = []
        
        if scores.get("communication_clarity", 0) < 7:
            suggestions.append("Practice structuring your answers: Problem → Approach → Solution → Results")
        
        if scores.get("technical_depth", 0) < 7:
            suggestions.append("Include specific technologies, frameworks, and technical metrics in your answers")
        
        if scores.get("problem_solving", 0) < 7:
            suggestions.append("Always explain your thought process and how you iterate on solutions")
        
        if scores.get("relevant_experience", 0) < 7:
            suggestions.append("Provide concrete examples from your past projects and their impact")
        
        if scores.get("confidence_professionalism", 0) < 7:
            suggestions.append("Avoid filler words, speak with conviction, and take a moment to think before answering")
        
        return suggestions
