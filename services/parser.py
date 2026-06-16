import re
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class ResumeParser:
    """Parse resume and extract skills, experience, and key information"""
    
    # Common technical skills
    TECH_SKILLS = {
        'languages': ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'go', 'rust', 'kotlin'],
        'frontend': ['react', 'vue', 'angular', 'html', 'css', 'typescript', 'next.js', 'svelte'],
        'backend': ['django', 'flask', 'fastapi', 'spring', 'express', 'node.js', 'rails', 'asp.net'],
        'databases': ['sql', 'mongodb', 'postgresql', 'mysql', 'redis', 'cassandra', 'dynamodb'],
        'tools': ['git', 'docker', 'kubernetes', 'jenkins', 'aws', 'gcp', 'azure', 'terraform'],
        'data': ['pandas', 'numpy', 'tensorflow', 'pytorch', 'scikit-learn', 'spark', 'hadoop'],
        'other': ['rest', 'graphql', 'microservices', 'ci/cd', 'agile', 'scrum', 'linux', 'windows']
    }
    
    @staticmethod
    def extract_skills(text: str) -> List[str]:
        """Extract technical skills from resume"""
        text_lower = text.lower()
        found_skills = []
        
        for category, skills in ResumeParser.TECH_SKILLS.items():
            for skill in skills:
                if skill in text_lower:
                    if skill not in found_skills:
                        found_skills.append(skill)
        
        return found_skills
    
    @staticmethod
    def extract_experience_years(text: str) -> float:
        """Extract years of experience from resume"""
        # Look for patterns like "5 years", "3 yrs", etc.
        patterns = [
            r'(\d+)\s*\+?\s*years?\s+of\s+experience',
            r'(\d+)\s*\+?\s*yrs?\s+experience',
            r'total\s+experience:?\s*(\d+)\s*\+?\s*years?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        # Count job durations as fallback
        date_pattern = r'(\d{4})\s*[-–]\s*(?:(\d{4})|present|current)'
        matches = re.findall(date_pattern, text, re.IGNORECASE)
        
        if matches:
            total_years = 0
            current_year = 2024
            for start_year, end_year in matches:
                start = int(start_year)
                end = int(end_year) if end_year else current_year
                total_years += (end - start)
            
            return total_years / len(matches) if matches else 0
        
        return 0.0
    
    @staticmethod
    def extract_job_titles(text: str) -> List[str]:
        """Extract job titles from resume"""
        # Common job title patterns
        job_patterns = [
            r'(?:position|title|role):\s*([^\n]+)',
            r'^([A-Z][a-z\s]+(?:Engineer|Developer|Manager|Analyst|Architect|Lead|Senior|Junior)[^\n]*)',
        ]
        
        titles = []
        for pattern in job_patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
            titles.extend([m.strip() for m in matches if m.strip()])
        
        return list(set(titles))
    
    @staticmethod
    def extract_email(text: str) -> str:
        """Extract email from resume"""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(pattern, text)
        return match.group(0) if match else None
    
    @staticmethod
    def extract_phone(text: str) -> str:
        """Extract phone number from resume"""
        patterns = [
            r'\+?\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return None
    
    @staticmethod
    def parse_resume(resume_text: str) -> Dict:
        """Main function to parse resume"""
        return {
            'skills': ResumeParser.extract_skills(resume_text),
            'experience_years': ResumeParser.extract_experience_years(resume_text),
            'job_titles': ResumeParser.extract_job_titles(resume_text),
            'email': ResumeParser.extract_email(resume_text),
            'phone': ResumeParser.extract_phone(resume_text),
        }


class JDParser:
    """Parse job description and extract requirements"""
    
    @staticmethod
    def extract_required_skills(text: str) -> List[str]:
        """Extract required skills from JD"""
        skills = ResumeParser.extract_skills(text)
        
        # Also look for "skills" section
        skills_section = re.search(
            r'(?:required\s+)?skills?:?\s*(.*?)(?:\n\n|responsibilities|requirements|about)',
            text,
            re.IGNORECASE | re.DOTALL
        )
        
        if skills_section:
            section_text = skills_section.group(1)
            # Extract items from lists
            items = re.findall(r'[-•]\s*([^\n]+)', section_text)
            skills.extend([item.strip().lower() for item in items])
        
        return list(set(skills))
    
    @staticmethod
    def extract_experience_requirement(text: str) -> float:
        """Extract required years of experience"""
        patterns = [
            r'(\d+)\s*\+?\s*years?\s+of\s+(?:experience|work)',
            r'require[ds]:\s*(\d+)\s*\+?\s*years?',
            r'(\d+)\s*\+?\s*years?\s+(?:in|with)\s+(?:software|web|backend|frontend)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        return 0.0
    
    @staticmethod
    def extract_job_title(text: str) -> str:
        """Extract job title from JD"""
        # Usually in the beginning or marked with "Position:"
        patterns = [
            r'^.*?([A-Z][a-z\s]*(?:Engineer|Developer|Manager|Analyst|Architect)[^\n]*)',
            r'(?:position|role|title):\s*([^\n]+)',
            r'^# ([^\n]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Software Engineer"
    
    @staticmethod
    def extract_responsibilities(text: str) -> List[str]:
        """Extract key responsibilities"""
        resp_section = re.search(
            r'(?:responsibilities?|duties?|what\s+you\'?ll?\s+do):\s*(.*?)(?:\n\n|requirements|qualifications)',
            text,
            re.IGNORECASE | re.DOTALL
        )
        
        if resp_section:
            section_text = resp_section.group(1)
            items = re.findall(r'[-•]\s*([^\n]+)', section_text)
            return [item.strip() for item in items]
        
        return []
    
    @staticmethod
    def parse_jd(jd_text: str) -> Dict:
        """Main function to parse JD"""
        return {
            'job_title': JDParser.extract_job_title(jd_text),
            'required_skills': JDParser.extract_required_skills(jd_text),
            'required_experience_years': JDParser.extract_experience_requirement(jd_text),
            'responsibilities': JDParser.extract_responsibilities(jd_text),
        }


class SkillMatcher:
    """Match resume skills with JD requirements"""
    
    @staticmethod
    def match_skills(resume_skills: List[str], jd_skills: List[str]) -> Dict:
        """Compare resume skills with JD requirements"""
        resume_skills_lower = [s.lower() for s in resume_skills]
        jd_skills_lower = [s.lower() for s in jd_skills]
        
        matched = [s for s in resume_skills_lower if s in jd_skills_lower]
        missing = [s for s in jd_skills_lower if s not in resume_skills_lower]
        extra = [s for s in resume_skills_lower if s not in jd_skills_lower]
        
        match_percentage = (len(matched) / len(jd_skills_lower) * 100) if jd_skills_lower else 0
        
        return {
            'matched_skills': matched,
            'missing_skills': missing,
            'extra_skills': extra,
            'match_percentage': round(match_percentage, 2),
            'total_matched': len(matched),
            'total_required': len(jd_skills_lower),
        }
    
    @staticmethod
    def get_interview_focus_areas(resume_data: Dict, jd_data: Dict) -> List[str]:
        """Determine which areas to focus on in interview"""
        skill_match = SkillMatcher.match_skills(resume_data['skills'], jd_data['required_skills'])
        
        focus_areas = []
        
        # Missing critical skills
        if skill_match['missing_skills']:
            focus_areas.append(f"Deep dive into: {', '.join(skill_match['missing_skills'][:3])}")
        
        # Experience gap
        resume_exp = resume_data.get('experience_years', 0)
        jd_exp = jd_data.get('required_experience_years', 0)
        if resume_exp < jd_exp:
            focus_areas.append(f"Highlight {resume_exp} years of relevant experience for {jd_exp} year role")
        
        # Behavioral aspects from JD
        if jd_data.get('responsibilities'):
            focus_areas.append("Behavioral questions on key responsibilities")
        
        return focus_areas
