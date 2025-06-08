import openai
from typing import List, Dict

class AIResumeEnhancer:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        
    def enhance_bullet_point(self, original_bullet: str, job_requirements: Dict) -> str:
        """Use AI to rewrite bullet point for specific job"""
        
        required_skills = ', '.join(job_requirements['skills']['technical'][:5])
        
        prompt = f"""
        Rewrite this resume bullet point to better match a job requiring {required_skills}:
        
        Original: {original_bullet}
        
        Requirements:
        - Keep the same core achievement/responsibility
        - Naturally incorporate relevant keywords: {required_skills}
        - Use strong action verbs
        - Include metrics/numbers if possible
        - Keep it under 20 words
        - Make it ATS-friendly
        
        Rewritten bullet point:
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional resume writer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI enhancement failed: {e}")
            return original_bullet
    
    def generate_custom_summary(self, candidate_profile: Dict, job_requirements: Dict) -> str:
        """Generate a completely custom professional summary"""
        
        prompt = f"""
        Write a professional summary for a {candidate_profile['experience_years']} year experienced developer applying for a position requiring:
        
        Required skills: {', '.join(job_requirements['skills']['technical'][:5])}
        Job responsibilities: {'; '.join(job_requirements['responsibilities'][:3])}
        
        Candidate's top skills: {', '.join(candidate_profile['skills'][:5])}
        Current role: {candidate_profile['experience'][0]['role']}
        
        Write a compelling 3-4 sentence summary that:
        1. Highlights relevant experience
        2. Includes key required skills naturally
        3. Shows enthusiasm for the role
        4. Mentions a quantifiable achievement
        
        Professional Summary:
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional resume writer specializing in tech resumes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI summary generation failed: {e}")
            return None
    
    def suggest_missing_skills(self, job_requirements: Dict, candidate_skills: List[str]) -> List[str]:
        """Suggest skills the candidate might have but didn't list"""
        
        required_skills = set(job_requirements['skills']['technical'])
        current_skills = set(skill.lower() for skill in candidate_skills)
        missing_skills = required_skills - current_skills
        
        if not missing_skills:
            return []
        
        prompt = f"""
        A developer with these skills: {', '.join(candidate_skills[:10])}
        
        Is applying for a job requiring: {', '.join(missing_skills)}
        
        What related skills might they have that they forgot to list? For example:
        - If they know React, they might know JSX, Hooks
        - If they know Python, they might know pip, virtualenv
        - If they know AWS, they might know specific AWS services
        
        List up to 5 likely skills they might have (one per line):
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a technical recruiter with deep knowledge of tech stacks."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.6
            )
            
            suggestions = response.choices[0].message.content.strip().split('\n')
            return [s.strip('- ').strip() for s in suggestions if s.strip()][:5]
            
        except Exception as e:
            print(f"AI skill suggestion failed: {e}")
            return []
    
    def create_tailored_project_description(self, project: Dict, job_requirements: Dict) -> str:
        """Rewrite project description to emphasize relevant aspects"""
        
        prompt = f"""
        Rewrite this project description to emphasize skills relevant to a job requiring {', '.join(job_requirements['skills']['technical'][:3])}:
        
        Original project:
        Name: {project['name']}
        Technologies: {', '.join(project['technologies'])}
        Description: {project['description']}
        
        Rewrite to:
        1. Emphasize relevant technologies
        2. Highlight technical challenges solved
        3. Include impact/results if possible
        4. Keep it under 50 words
        
        Rewritten description:
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a technical resume writer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI project enhancement failed: {e}")
            return project['description']
