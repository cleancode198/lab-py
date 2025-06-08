import json
from typing import Dict, List
from datetime import datetime
import openai  # Optional: for AI-powered customization

class ResumeCustomizer:
    def __init__(self, candidate_profile_path: str):
        """Initialize with candidate's master profile"""
        with open(candidate_profile_path, 'r') as f:
            self.master_profile = json.load(f)
        
        # Templates for different sections
        self.summary_templates = {
            'frontend': "Experienced Frontend Developer with {years} years of expertise in {skills}. Passionate about creating responsive, user-friendly web applications with modern JavaScript frameworks.",
            'backend': "Backend Developer with {years} years of experience building scalable server-side applications using {skills}. Strong focus on API design, database optimization, and system architecture.",
            'fullstack': "Full Stack Developer with {years} years of experience in both frontend and backend development. Proficient in {skills} with a track record of delivering end-to-end solutions.",
            'general': "Software Developer with {years} years of experience in {skills}. Committed to writing clean, maintainable code and delivering high-quality software solutions."
        }

    def customize_resume(self, job_requirements: Dict) -> Dict:
        """Create a customized resume based on job requirements"""
        customized_resume = {
            'name': self.master_profile['name'],
            'contact': self.master_profile['contact'],
            'summary': self._customize_summary(job_requirements),
            'skills': self._prioritize_skills(job_requirements),
            'experience': self._customize_experience(job_requirements),
            'education': self.master_profile['education'],
            'projects': self._select_relevant_projects(job_requirements),
            'keywords': self._extract_keywords(job_requirements)
        }
        
        return customized_resume

    def _customize_summary(self, job_requirements: Dict) -> str:
        """Create a tailored professional summary"""
        # Determine job type
        skills = job_requirements['skills']['technical']
        job_type = 'general'
        
        if any(skill in skills for skill in ['react', 'angular', 'vue', 'frontend']):
            job_type = 'frontend'
        elif any(skill in skills for skill in ['node', 'django', 'backend', 'api']):
            job_type = 'backend'
        elif len(set(skills) & {'frontend', 'backend', 'fullstack'}) > 1:
            job_type = 'fullstack'
        
        # Get relevant skills for the summary
        relevant_skills = self._get_matching_skills(job_requirements)[:3]
        skills_str = ', '.join(relevant_skills) if relevant_skills else 'modern technologies'
        
        summary = self.summary_templates[job_type].format(
            years=self.master_profile['experience_years'],
            skills=skills_str
        )
        
        # Add specific requirements mentioned in job
        if job_requirements.get('must_have'):
            key_requirement = job_requirements['must_have'][0] if job_requirements['must_have'] else ''
            if key_requirement:
                summary += f" {key_requirement}"
        
        return summary

    def _prioritize_skills(self, job_requirements: Dict) -> Dict[str, List[str]]:
        """Reorder skills to match job requirements"""
        required_skills = set(job_requirements['skills']['technical'])
        
        prioritized_skills = {
            'primary': [],
            'secondary': [],
            'other': []
        }
        
        # First, add all matching required skills
        for skill in self.master_profile['skills']:
            if skill.lower() in required_skills:
                prioritized_skills['primary'].append(skill)
        
        # Add related skills
        for skill in self.master_profile['skills']:
            if skill not in prioritized_skills['primary']:
                if self._is_related_skill(skill, required_skills):
                    prioritized_skills['secondary'].append(skill)
                else:
                    prioritized_skills['other'].append(skill)
        
        # Limit the number of skills shown
        return {
            'primary': prioritized_skills['primary'][:6],
            'secondary': prioritized_skills['secondary'][:4],
            'other': prioritized_skills['other'][:3]
        }

    def _customize_experience(self, job_requirements: Dict) -> List[Dict]:
        """Customize experience descriptions to match job requirements"""
        customized_experience = []
        required_skills = set(job_requirements['skills']['technical'])
        key_responsibilities = job_requirements.get('responsibilities', [])
        
        for exp in self.master_profile['experience']:
            customized_exp = exp.copy()
            
            # Rewrite bullet points to emphasize relevant skills
            new_bullets = []
            for bullet in exp['bullets']:
                # Check if bullet contains relevant skills
                bullet_lower = bullet.lower()
                relevance_score = sum(1 for skill in required_skills if skill in bullet_lower)
                
                if relevance_score > 0:
                    # Enhance bullet point with keywords
                    enhanced_bullet = self._enhance_bullet_point(bullet, required_skills)
                    new_bullets.append((enhanced_bullet, relevance_score + 10))
                else:
                    new_bullets.append((bullet, relevance_score))
            
            # Sort bullets by relevance and take top ones
            new_bullets.sort(key=lambda x: x[1], reverse=True)
            customized_exp['bullets'] = [bullet[0] for bullet in new_bullets[:4]]
            
            # Add a new bullet if we have matching responsibilities
            if key_responsibilities and len(customized_exp['bullets']) < 5:
                for resp in key_responsibilities:
                    if self._can_claim_experience(resp, exp['role']):
                        customized_exp['bullets'].append(self._create_bullet_from_responsibility(resp))
                        break
            
            customized_experience.append(customized_exp)
        
        return customized_experience

    def _select_relevant_projects(self, job_requirements: Dict) -> List[Dict]:
        """Select projects that best match job requirements"""
        required_skills = set(job_requirements['skills']['technical'])
        selected_projects = []
        
        for project in self.master_profile.get('projects', []):
            # Calculate relevance score
            project_skills = set(project.get('technologies', []))
            relevance_score = len(project_skills & required_skills)
            
            if relevance_score > 0:
                # Customize project description
                customized_project = project.copy()
                customized_project['relevance_score'] = relevance_score
                
                # Highlight matching technologies
                customized_project['highlighted_tech'] = list(project_skills & required_skills)
                
                selected_projects.append(customized_project)
        
        # Sort by relevance and return top projects
        selected_projects.sort(key=lambda x: x['relevance_score'], reverse=True)
        return selected_projects[:3]

    def _extract_keywords(self, job_requirements: Dict) -> List[str]:
        """Extract important keywords for ATS optimization"""
        keywords = []
        
        # Add all required technical skills
        keywords.extend(job_requirements['skills']['technical'])
        
        # Add important soft skills
        keywords.extend(job_requirements['skills']['soft'][:3])
        
        # Extract keywords from must-have requirements
        for requirement in job_requirements.get('must_have', []):
            # Extract technical terms from requirements
            words = requirement.lower().split()
            for word in words:
                if len(word) > 3 and word not in ['with', 'using', 'have', 'must']:
                    keywords.append(word)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        return unique_keywords[:15]

    def _get_matching_skills(self, job_requirements: Dict) -> List[str]:
        """Get candidate skills that match job requirements"""
        required_skills = set(job_requirements['skills']['technical'])
        matching = []
        
        for skill in self.master_profile['skills']:
            if skill.lower() in required_skills:
                matching.append(skill)
        
        return matching

    def _is_related_skill(self, skill: str, required_skills: set) -> bool:
        """Check if a skill is related to required skills"""
        skill_relations = {
            'react': ['redux', 'react native', 'next.js', 'gatsby'],
            'angular': ['rxjs', 'ngrx', 'typescript'],
            'vue': ['vuex', 'nuxt', 'vuetify'],
            'python': ['django', 'flask', 'fastapi', 'pandas', 'numpy'],
            'javascript': ['typescript', 'es6', 'node.js'],
            'java': ['spring', 'hibernate', 'maven', 'gradle']
        }
        
        skill_lower = skill.lower()
        for req_skill in required_skills:
            if req_skill in skill_relations:
                if skill_lower in skill_relations[req_skill]:
                    return True
            # Check reverse relation
            for base_skill, related in skill_relations.items():
                if skill_lower == base_skill and req_skill in related:
                    return True
        
        return False

    def _enhance_bullet_point(self, bullet: str, required_skills: set) -> str:
        """Enhance bullet point with relevant keywords"""
        # This is a simple implementation
        # Could be enhanced with NLP/AI
        for skill in required_skills:
            if skill not in bullet.lower():
                # Try to naturally insert the skill if contextually appropriate
                if 'developed' in bullet.lower() and 'using' not in bullet.lower():
                    bullet = bullet.replace('developed', f'developed using {skill}')
                    break
        
        return bullet

    def _can_claim_experience(self, responsibility: str, role: str) -> bool:
        """Check if we can claim experience with a responsibility based on role"""
        # Simple keyword matching - could be enhanced with NLP
        role_keywords = {
            'frontend': ['ui', 'user interface', 'responsive', 'design'],
            'backend': ['api', 'database', 'server', 'infrastructure'],
            'fullstack': ['end-to-end', 'full stack', 'entire'],
            'lead': ['team', 'mentor', 'guide', 'coordinate'],
            'senior': ['architect', 'design', 'optimize', 'strategy']
        }
        
        resp_lower = responsibility.lower()
        role_lower = role.lower()
        
        for role_type, keywords in role_keywords.items():
            if role_type in role_lower:
                return any(keyword in resp_lower for keyword in keywords)
        
        return True  # Default to true for generic responsibilities

    def _create_bullet_from_responsibility(self, responsibility: str) -> str:
        """Create a bullet point from a job responsibility"""
        # Add action verb if not present
        action_verbs = ['Developed', 'Implemented', 'Designed', 'Built', 'Created', 
                       'Managed', 'Led', 'Optimized', 'Delivered', 'Architected']
        
        resp_capitalized = responsibility[0].upper() + responsibility[1:]
        
        # Check if it already starts with an action verb
        if not any(resp_capitalized.startswith(verb) for verb in action_verbs):
            # Add appropriate action verb
            if 'api' in responsibility.lower():
                return f"Developed {responsibility}"
            elif 'team' in responsibility.lower():
                return f"Led {responsibility}"
            else:
                return f"Implemented {responsibility}"
        
        return resp_capitalized

    def generate_custom_resume_text(self, customized_resume: Dict) -> str:
        """Generate formatted resume text"""
        resume_text = f"""
{customized_resume['name']}
{customized_resume['contact']['email']} | {customized_resume['contact']['phone']} | {customized_resume['contact']['linkedin']}

PROFESSIONAL SUMMARY
{customized_resume['summary']}

TECHNICAL SKILLS
Primary: {', '.join(customized_resume['skills']['primary'])}
Secondary: {', '.join(customized_resume['skills']['secondary'])}
Additional: {', '.join(customized_resume['skills']['other'])}

PROFESSIONAL EXPERIENCE
"""
        
        for exp in customized_resume['experience']:
            resume_text += f"\n{exp['company']} | {exp['role']} | {exp['duration']}\n"
            for bullet in exp['bullets']:
                resume_text += f"• {bullet}\n"
        
        resume_text += "\nPROJECTS\n"
        for project in customized_resume['projects']:
            resume_text += f"\n{project['name']}\n"
            resume_text += f"Technologies: {', '.join(project['highlighted_tech'])}\n"
            resume_text += f"{project['description']}\n"
        
        resume_text += f"\nEDUCATION\n"
        for edu in customized_resume['education']:
            resume_text += f"{edu['degree']} - {edu['institution']} ({edu['year']})\n"
        
        return resume_text

    def save_customized_resume(self, customized_resume: Dict, job_title: str, company: str):
        """Save customized resume for a specific job"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resume_{company}_{job_title}_{timestamp}.json"
        
        with open(f"data/customized_resumes/{filename}", 'w') as f:
            json.dump(customized_resume, f, indent=2)
        
        # Also save as text
        text_filename = filename.replace('.json', '.txt')
        with open(f"data/customized_resumes/{text_filename}", 'w') as f:
            f.write(self.generate_custom_resume_text(customized_resume))
        
        return filename
