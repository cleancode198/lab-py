import re
import spacy
from collections import Counter
from typing import List, Dict, Set

class JobDescriptionAnalyzer:
    def __init__(self):
        # Load spaCy model (install with: python -m spacy download en_core_web_sm)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("Please install spacy model: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Common skill keywords by category
        self.skill_categories = {
            'languages': {
                'python', 'javascript', 'java', 'c++', 'c#', 'ruby', 'go', 'rust',
                'typescript', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab'
            },
            'frontend': {
                'react', 'angular', 'vue', 'svelte', 'jquery', 'bootstrap',
                'tailwind', 'sass', 'less', 'webpack', 'babel', 'npm', 'yarn',
                'html', 'css', 'html5', 'css3', 'responsive', 'flexbox', 'grid'
            },
            'backend': {
                'node', 'nodejs', 'express', 'django', 'flask', 'spring', 'rails',
                'laravel', 'asp.net', 'fastapi', 'nestjs', 'graphql', 'rest', 'api'
            },
            'databases': {
                'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
                'cassandra', 'dynamodb', 'firebase', 'sqlite', 'oracle', 'nosql'
            },
            'cloud': {
                'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes',
                'jenkins', 'ci/cd', 'terraform', 'ansible', 'cloudformation'
            },
            'tools': {
                'git', 'github', 'gitlab', 'bitbucket', 'jira', 'confluence',
                'slack', 'agile', 'scrum', 'kanban', 'devops', 'linux', 'bash'
            }
        }
        
        # Soft skills keywords
        self.soft_skills = {
            'communication', 'teamwork', 'leadership', 'problem-solving',
            'analytical', 'creative', 'detail-oriented', 'self-motivated',
            'collaborative', 'innovative', 'adaptable', 'organized'
        }

    def extract_skills(self, job_description: str) -> Dict[str, List[str]]:
        """Extract technical and soft skills from job description"""
        description_lower = job_description.lower()
        found_skills = {
            'technical': [],
            'soft': [],
            'languages': [],
            'frameworks': [],
            'tools': []
        }
        
        # Extract technical skills by category
        for category, skills in self.skill_categories.items():
            for skill in skills:
                if skill in description_lower:
                    if category == 'languages':
                        found_skills['languages'].append(skill)
                    elif category in ['frontend', 'backend']:
                        found_skills['frameworks'].append(skill)
                    else:
                        found_skills['tools'].append(skill)
                    found_skills['technical'].append(skill)
        
        # Extract soft skills
        for skill in self.soft_skills:
            if skill in description_lower:
                found_skills['soft'].append(skill)
        
        return found_skills

    def extract_requirements(self, job_description: str) -> Dict[str, any]:
        """Extract key requirements from job description"""
        requirements = {
            'experience_years': self._extract_experience_years(job_description),
            'education': self._extract_education(job_description),
            'skills': self.extract_skills(job_description),
            'responsibilities': self._extract_responsibilities(job_description),
            'must_have': self._extract_must_have(job_description),
            'nice_to_have': self._extract_nice_to_have(job_description)
        }
        return requirements

    def _extract_experience_years(self, text: str) -> int:
        """Extract required years of experience"""
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*years?\s*(?:of\s*)?professional',
            r'(\d+)\+?\s*yrs?\s*experience'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return 0

    def _extract_education(self, text: str) -> List[str]:
        """Extract education requirements"""
        education_keywords = [
            'bachelor', 'master', 'phd', 'degree', 'computer science',
            'engineering', 'mathematics', 'statistics', 'mba'
        ]
        
        found = []
        text_lower = text.lower()
        for keyword in education_keywords:
            if keyword in text_lower:
                found.append(keyword)
        return found

    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract main responsibilities"""
        # Look for sections that typically contain responsibilities
        patterns = [
            r'responsibilities:?\s*(.*?)(?:requirements|qualifications|skills|$)',
            r'you will:?\s*(.*?)(?:requirements|qualifications|skills|$)',
            r'duties:?\s*(.*?)(?:requirements|qualifications|skills|$)'
        ]
        
        responsibilities = []
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                resp_text = match.group(1)
                # Split by bullet points or newlines
                items = re.split(r'[\n•·-]+', resp_text)
                responsibilities.extend([item.strip() for item in items if item.strip()])
        
        return responsibilities[:5]  # Return top 5

    def _extract_must_have(self, text: str) -> List[str]:
        """Extract must-have requirements"""
        patterns = [
            r'must have:?\s*(.*?)(?:nice to have|preferred|$)',
            r'required:?\s*(.*?)(?:nice to have|preferred|$)',
            r'requirements:?\s*(.*?)(?:nice to have|preferred|responsibilities|$)'
        ]
        
        must_have = []
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                text_segment = match.group(1)
                items = re.split(r'[\n•·-]+', text_segment)
                must_have.extend([item.strip() for item in items if item.strip()])
        
        return must_have[:5]

    def _extract_nice_to_have(self, text: str) -> List[str]:
        """Extract nice-to-have requirements"""
        patterns = [
            r'nice to have:?\s*(.*?)(?:$)',
            r'preferred:?\s*(.*?)(?:$)',
            r'bonus:?\s*(.*?)(?:$)'
        ]
        
        nice_to_have = []
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                text_segment = match.group(1)
                items = re.split(r'[\n•·-]+', text_segment)
                nice_to_have.extend([item.strip() for item in items if item.strip()])
        
        return nice_to_have[:3]

    def calculate_match_score(self, job_requirements: Dict, candidate_profile: Dict) -> float:
        """Calculate how well candidate matches job requirements"""
        score = 0.0
        max_score = 100.0
        
        # Experience match (20 points)
        required_exp = job_requirements.get('experience_years', 0)
        candidate_exp = candidate_profile.get('experience_years', 0)
        if candidate_exp >= required_exp:
            score += 20
        else:
            score += max(0, 20 * (candidate_exp / required_exp))
        
        # Skills match (40 points)
        required_skills = set(job_requirements['skills']['technical'])
        candidate_skills = set(candidate_profile.get('skills', []))
        if required_skills:
            skill_match = len(required_skills & candidate_skills) / len(required_skills)
            score += 40 * skill_match
        
        # Education match (20 points)
        required_edu = set(job_requirements.get('education', []))
        candidate_edu = set(candidate_profile.get('education', []))
        if required_edu:
            edu_match = len(required_edu & candidate_edu) / len(required_edu)
            score += 20 * edu_match
        else:
            score += 20  # No specific education required
        
        # Soft skills match (20 points)
        required_soft = set(job_requirements['skills']['soft'])
        candidate_soft = set(candidate_profile.get('soft_skills', []))
        if required_soft:
            soft_match = len(required_soft & candidate_soft) / len(required_soft)
            score += 20 * soft_match
        
        return score
