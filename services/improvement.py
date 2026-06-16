import json
import logging
from typing import List, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ImprovementPlanGenerator:
    """Generate personalized daily improvement plans"""
    
    # Task templates for different skill areas
    SKILL_IMPROVEMENT_TASKS = {
        "communication": [
            {
                "title": "STAR Method Practice",
                "description": "Practice answering 3 questions using STAR method (Situation, Task, Action, Result)",
                "duration_minutes": 30,
                "resources": ["STAR framework guide", "Sample interview questions"],
                "difficulty": 1
            },
            {
                "title": "Record & Review",
                "description": "Record yourself answering a question, then review for clarity and structure",
                "duration_minutes": 25,
                "resources": ["Voice recorder app", "Interview question set"],
                "difficulty": 2
            },
            {
                "title": "Storytelling Workshop",
                "description": "Write 5 different stories about your achievements with clear structure",
                "duration_minutes": 40,
                "resources": ["Story template", "Past projects list"],
                "difficulty": 2
            }
        ],
        "technical_depth": [
            {
                "title": "Deep Dive Study",
                "description": "Study one technology in depth - read docs, watch tutorials",
                "duration_minutes": 45,
                "resources": ["Official documentation", "YouTube tutorials"],
                "difficulty": 3
            },
            {
                "title": "Code Review & Analysis",
                "description": "Analyze 3 code samples using the weak technology, explain what they do",
                "duration_minutes": 35,
                "resources": ["GitHub repositories", "Code examples"],
                "difficulty": 2
            },
            {
                "title": "Build Mini Project",
                "description": "Build a small project using the technology you're weak in",
                "duration_minutes": 60,
                "resources": ["Tutorial", "Documentation"],
                "difficulty": 3
            }
        ],
        "problem_solving": [
            {
                "title": "Problem Analysis Practice",
                "description": "Take 2 problems and write down your approach before coding",
                "duration_minutes": 30,
                "resources": ["LeetCode easy problems", "Problem analysis template"],
                "difficulty": 1
            },
            {
                "title": "Algorithm Study",
                "description": "Study one algorithm or data structure deeply",
                "duration_minutes": 40,
                "resources": ["Algorithm course", "Visualization tools"],
                "difficulty": 2
            },
            {
                "title": "Whiteboard Simulation",
                "description": "Solve 1 problem on whiteboard/paper like in interview",
                "duration_minutes": 35,
                "resources": ["Whiteboard", "Problem set"],
                "difficulty": 2
            }
        ],
        "experience": [
            {
                "title": "Project Documentation",
                "description": "Document 2 of your past projects with metrics and impact",
                "duration_minutes": 30,
                "resources": ["Project list", "Documentation template"],
                "difficulty": 1
            },
            {
                "title": "Case Study Writing",
                "description": "Write 3 case studies of problems you solved",
                "duration_minutes": 40,
                "resources": ["Case study template", "Past projects"],
                "difficulty": 2
            },
            {
                "title": "Impact Quantification",
                "description": "Quantify impact of 5 of your projects (% improvement, users affected, etc)",
                "duration_minutes": 25,
                "resources": ["Analytics tools", "Project metrics"],
                "difficulty": 1
            }
        ],
        "confidence": [
            {
                "title": "Mock Interview Practice",
                "description": "Do 1 full mock interview and review your performance",
                "duration_minutes": 50,
                "resources": ["Mock interview platform", "Feedback guide"],
                "difficulty": 3
            },
            {
                "title": "Positive Self-Talk",
                "description": "Write down your strengths and accomplishments, read daily",
                "duration_minutes": 15,
                "resources": ["Notepad", "Strength list"],
                "difficulty": 1
            },
            {
                "title": "Presentation Practice",
                "description": "Present your experiences to a friend or mirror",
                "duration_minutes": 25,
                "resources": ["Presentation template", "Mirror/friend"],
                "difficulty": 1
            }
        ]
    }
    
    SKILL_RESOURCES = {
        "communication": [
            "STAR Method Interview Guide",
            "TED Talks on Public Speaking",
            "Toastmasters Resources",
            "Interview preparation books",
            "Communication courses on Coursera"
        ],
        "technical_depth": [
            "Official technology documentation",
            "YouTube tutorial channels (Tech Lead, Fireship)",
            "GitHub repositories with examples",
            "Online courses (Udemy, Coursera, Pluralsight)",
            "Technical blogs and Medium articles"
        ],
        "problem_solving": [
            "LeetCode (easy → medium difficulty)",
            "HackerRank algorithm section",
            "InterviewBit problems",
            "Algorithms textbooks",
            "YouTube algorithm channels"
        ],
        "experience": [
            "Your portfolio website",
            "GitHub with well-documented projects",
            "LinkedIn profile optimization",
            "Project case study templates",
            "Past performance reviews"
        ],
        "confidence": [
            "Mock interview platforms",
            "Confidence coaching books",
            "Meditation apps (Calm, Headspace)",
            "YouTube confidence building",
            "Mentor/peer feedback sessions"
        ]
    }
    
    @staticmethod
    def generate_plan(interview_summary: Dict, days: int = 14) -> Dict:
        """Generate personalized improvement plan"""
        
        # Identify weak areas
        weak_areas = interview_summary.get("areas_for_improvement", [])
        scores = interview_summary.get("scores", {})
        
        # Map weak areas to improvement categories
        improvement_categories = ImprovementPlanGenerator._map_weaknesses(weak_areas, scores)
        
        # Generate daily tasks
        daily_tasks = ImprovementPlanGenerator._generate_daily_tasks(
            improvement_categories, 
            days
        )
        
        # Generate resources
        resources = ImprovementPlanGenerator._get_resources(improvement_categories)
        
        return {
            "weak_areas": weak_areas,
            "improvement_focus": improvement_categories,
            "duration_days": days,
            "daily_commitment_minutes": 30,
            "daily_tasks": daily_tasks,
            "resources": resources,
            "total_hours_needed": (len(daily_tasks) * 0.5),  # Rough estimate
            "success_metrics": ImprovementPlanGenerator._get_success_metrics(improvement_categories)
        }
    
    @staticmethod
    def _map_weaknesses(weak_areas: List[str], scores: Dict) -> List[str]:
        """Map interview weaknesses to improvement categories"""
        categories = []
        
        weaknesses_lower = [w.lower() for w in weak_areas]
        
        if any(word in str(weaknesses_lower) for word in ['communication', 'clarity', 'articulate', 'structure']):
            categories.append("communication")
        
        if any(word in str(weaknesses_lower) for word in ['technical', 'depth', 'details', 'technology']):
            categories.append("technical_depth")
        
        if any(word in str(weaknesses_lower) for word in ['problem', 'solving', 'approach', 'algorithm']):
            categories.append("problem_solving")
        
        if any(word in str(weaknesses_lower) for word in ['experience', 'project', 'example', 'specific']):
            categories.append("experience")
        
        if any(word in str(weaknesses_lower) for word in ['confident', 'confidence', 'professional', 'filler']):
            categories.append("confidence")
        
        return categories if categories else ["communication", "technical_depth"]
    
    @staticmethod
    def _generate_daily_tasks(categories: List[str], days: int) -> List[Dict]:
        """Generate daily tasks rotating through categories"""
        daily_tasks = []
        task_cycle = categories * (days // len(categories) + 1)
        
        for day in range(1, days + 1):
            category = task_cycle[day - 1]
            available_tasks = ImprovementPlanGenerator.SKILL_IMPROVEMENT_TASKS.get(category, [])
            
            if available_tasks:
                task_index = (day - 1) % len(available_tasks)
                task = available_tasks[task_index].copy()
                
                daily_tasks.append({
                    "day": day,
                    "category": category,
                    "title": task["title"],
                    "description": task["description"],
                    "duration_minutes": task["duration_minutes"],
                    "resources": task["resources"],
                    "difficulty": task["difficulty"],
                    "completed": False
                })
        
        return daily_tasks[:days]
    
    @staticmethod
    def _get_resources(categories: List[str]) -> Dict:
        """Get curated resources for improvement areas"""
        resources = {}
        
        for category in categories:
            resources[category] = ImprovementPlanGenerator.SKILL_RESOURCES.get(category, [])
        
        return resources
    
    @staticmethod
    def _get_success_metrics(categories: List[str]) -> List[str]:
        """Define success metrics for each category"""
        metrics = []
        
        for category in categories:
            if category == "communication":
                metrics.append("Answer structure: Problem → Solution → Results")
                metrics.append("Use 3+ specific examples per interview")
                metrics.append("Eliminate filler words (um, uh, like)")
            elif category == "technical_depth":
                metrics.append("Mention 5+ technical details per answer")
                metrics.append("Explain trade-offs and design decisions")
                metrics.append("Reference specific metrics (performance, scale)")
            elif category == "problem_solving":
                metrics.append("Always explain your thought process")
                metrics.append("Solve 2+ problems per day")
                metrics.append("Discuss different approaches and pick best")
            elif category == "experience":
                metrics.append("Have 5 solid project stories ready")
                metrics.append("Quantify impact (% improvement, user count)")
                metrics.append("Map experience to job requirements")
            elif category == "confidence":
                metrics.append("Complete 3+ mock interviews")
                metrics.append("Speak with conviction, avoid hedging language")
                metrics.append("Maintain professional tone throughout")
        
        return metrics if metrics else ["Improve interview score by 10%", "Get positive feedback on practice interviews"]


class WeeklyProgressTracker:
    """Track progress through improvement plan"""
    
    @staticmethod
    def get_progress_summary(completed_tasks: List[Dict], total_tasks: int) -> Dict:
        """Get progress summary"""
        completed = len(completed_tasks)
        completion_rate = (completed / total_tasks * 100) if total_tasks > 0 else 0
        
        # Calculate by category
        by_category = {}
        for task in completed_tasks:
            category = task.get("category", "unknown")
            by_category[category] = by_category.get(category, 0) + 1
        
        return {
            "total_completed": completed,
            "total_tasks": total_tasks,
            "completion_rate": round(completion_rate, 2),
            "by_category": by_category,
            "next_task_day": completed + 1
        }
    
    @staticmethod
    def get_improvement_estimate(interview_scores_before: Dict, days_completed: int) -> Dict:
        """Estimate improvement based on daily effort"""
        
        # Simple model: 0.5% improvement per day (conservative)
        estimated_improvement_per_day = 0.5
        estimated_final_score = min(
            100,
            sum(interview_scores_before.values()) / len(interview_scores_before) + 
            (days_completed * estimated_improvement_per_day)
        )
        
        return {
            "original_average_score": round(sum(interview_scores_before.values()) / len(interview_scores_before), 2),
            "days_of_effort": days_completed,
            "estimated_improvement": round(days_completed * estimated_improvement_per_day, 2),
            "estimated_new_score": round(estimated_final_score, 2)
        }
