# Modified section of l.py to include resume customization

import time, math, random, os
import utils, constants, config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import prRed, prYellow, prGreen

# Import our new modules
from job_analyzer import JobDescriptionAnalyzer
from resume_customizer import ResumeCustomizer

class LinkedinEnhanced:
    def __init__(self):
        # Existing initialization code...
        self.driver = webdriver.Firefox(options=utils.browserOptions())
        
        # Initialize resume customization components
        self.job_analyzer = JobDescriptionAnalyzer()
        self.resume_customizer = ResumeCustomizer('data/candidate_profile.json')
        
        # Track which resumes we've customized
        self.customized_resumes = {}

    def getJobDescription(self):
        """Extract full job description from the job posting"""
        try:
            # Click "Show more" button if it exists
            try:
                show_more = self.driver.find_element(By.CSS_SELECTOR, 
                    "button[aria-label='Click to see more description']")
                show_more.click()
                time.sleep(1)
            except:
                pass
            
            # Get job description text
            job_desc_element = self.driver.find_element(By.CSS_SELECTOR, 
                "div.jobs-description__content")
            job_description = job_desc_element.text
            
            return job_description
        except Exception as e:
            prYellow(f"Warning: Could not extract job description: {str(e)}")
            return ""

    def customizeResumeForJob(self, job_title, job_company, job_description):
        """Create a customized resume for this specific job"""
        try:
            # Analyze job requirements
            prYellow(f"Analyzing job requirements for {job_title} at {job_company}...")
            job_requirements = self.job_analyzer.extract_requirements(job_description)
            
            # Calculate match score
            match_score = self.job_analyzer.calculate_match_score(
                job_requirements, 
                self.resume_customizer.master_profile
            )
            prGreen(f"Match score: {match_score:.1f}%")
            
            # Create customized resume
            prYellow("Creating customized resume...")
            customized_resume = self.resume_customizer.customize_resume(job_requirements)
            
            # Save customized resume
            filename = self.resume_customizer.save_customized_resume(
                customized_resume, 
                job_title.replace('/', '-'), 
                job_company.replace('/', '-')
            )
            
            # Store reference for later use
            job_key = f"{job_company}_{job_title}"
            self.customized_resumes[job_key] = {
                'filename': filename,
                'match_score': match_score,
                'keywords': customized_resume['keywords']
            }
            
            prGreen(f"✅ Resume customized and saved: {filename}")
            
            return customized_resume, match_score
            
        except Exception as e:
            prRed(f"Error customizing resume: {str(e)}")
            return None, 0

    def fillApplicationForm(self, customized_resume=None):
        """Enhanced application form filling with customized content"""
        try:
            # Check if there's a summary/cover letter field
            try:
                summary_field = self.driver.find_element(By.CSS_SELECTOR, 
                    "textarea[aria-label*='summary'], textarea[aria-label*='cover']")
                
                if customized_resume:
                    # Create a tailored cover letter intro using the customized summary
                    cover_letter = f"""
{customized_resume['summary']}

I am particularly excited about this opportunity because my experience with {', '.join(customized_resume['skills']['primary'][:3])} aligns perfectly with your requirements.

{self._generate_relevant_achievement(customized_resume)}

I look forward to discussing how my skills and experience can contribute to your team.
"""
                    summary_field.clear()
                    summary_field.send_keys(cover_letter)
                    prGreen("✅ Filled customized cover letter")
            except:
                pass
            
            # Check for skills assessment questions
            self._fill_skills_questions(customized_resume)
            
            # Check for years of experience questions
            self._fill_experience_questions(customized_resume)
            
        except Exception as e:
            prYellow(f"Warning in form filling: {str(e)}")

    def _generate_relevant_achievement(self, customized_resume):
        """Generate a relevant achievement from experience"""
        if customized_resume['experience']:
            # Get the most relevant bullet point from recent experience
            recent_exp = customized_resume['experience'][0]
            if recent_exp['bullets']:
                return f"In my current role, I have {recent_exp['bullets'][0].lower()}"
        return "I have a proven track record of delivering high-quality solutions."

    def _fill_skills_questions(self, customized_resume):
        """Fill skill-related assessment questions"""
        if not customized_resume:
            return
            
        try:
            # Look for skill assessment questions
            skill_questions = self.driver.find_elements(By.CSS_SELECTOR, 
                "div[data-test-form-element]")
            
            for question in skill_questions:
                question_text = question.text.lower()
                
                # Check if it's asking about specific skills
                for skill in customized_resume['skills']['primary']:
                    if skill.lower() in question_text:
                        # Look for radio buttons or checkboxes
                        try:
                            yes_option = question.find_element(By.CSS_SELECTOR, 
                                "input[value='Yes'], label:contains('Yes')")
                            yes_option.click()
                            prGreen(f"✅ Answered 'Yes' to {skill} experience")
                        except:
                            pass
        except:
            pass

    def _fill_experience_questions(self, customized_resume):
        """Fill experience-related questions"""
        if not customized_resume:
            return
            
        try:
            # Look for experience year dropdowns or inputs
            exp_inputs = self.driver.find_elements(By.CSS_SELECTOR, 
                "input[aria-label*='years'], select[aria-label*='experience']")
            
            for exp_input in exp_inputs:
                if exp_input.tag_name == 'input':
                    exp_input.clear()
                    exp_input.send_keys(str(self.resume_customizer.master_profile['experience_years']))
                elif exp_input.tag_name == 'select':
                    # Handle dropdown selection
                    from selenium.webdriver.support.ui import Select
                    select = Select(exp_input)
                    select.select_by_visible_text(f"{self.resume_customizer.master_profile['experience_years']} years")
                    
                prGreen(f"✅ Filled experience years")
        except:
            pass

    def applyProcess(self, percentage, offerPage):
        """Enhanced apply process with resume customization"""
        # Get job details for this specific application
        job_title = self.current_job_title
        job_company = self.current_job_company
        job_key = f"{job_company}_{job_title}"
        
        # Check if we have a customized resume for this job
        customized_resume = None
        if job_key in self.customized_resumes:
            resume_data = self.customized_resumes[job_key]
            # Load the customized resume
            with open(f"data/customized_resumes/{resume_data['filename']}", 'r') as f:
                import json
                customized_resume = json.load(f)
        
        applyPages = math.floor(100 / percentage)
        result = ""
        
        try:
            for pages in range(applyPages - 2):
                # Check current page for form fields that need customization
                self.fillApplicationForm(customized_resume)
                
                # Continue to next page
                self.driver.find_element(By.CSS_SELECTOR, 
                    "button[aria-label='Continue to next step']").click()
                time.sleep(random.uniform(1, constants.botSpeed))
            
            # Review page
            self.driver.find_element(By.CSS_SELECTOR, 
                "button[aria-label='Review your application']").click()
            time.sleep(random.uniform(1, constants.botSpeed))
            
            # Submit
            self.driver.find_element(By.CSS_SELECTOR, 
                "button[aria-label='Submit application']").click()
            time.sleep(random.uniform(1, constants.botSpeed))
            
            result = f"* 🥳 Applied with customized resume (Match: {self.customized_resumes.get(job_key, {}).get('match_score', 0):.1f}%)"
        
        except Exception as e:
            result = f"* 🥵 Could not complete application: {str(e)}"
        
        return result

    def linkJobApply(self):
        """Enhanced main application loop"""
        self.generateUrls()
        countApplied = 0
        countJobs = 0
        
        # Create directories for customized resumes
        os.makedirs('data/customized_resumes', exist_ok=True)
        
        urlData = utils.getUrlDataFile()
        
        for url in urlData:
            self.driver.get(url)
            
            # Existing code for getting total jobs, pages, etc...
            totalJobs = self.driver.find_element(By.XPATH, '//small').text
            totalPages = utils.jobsToPages(totalJobs)
            
            for page in range(totalPages):
                # Existing code for getting job offers...
                
                for jobID in offerIds:
                    offerPage = 'https://www.linkedin.com/jobs/view/' + str(jobID)
                    self.driver.get(offerPage)
                    time.sleep(random.uniform(1, constants.botSpeed))
                    
                    # Get job properties
                    jobTitle, jobCompany, jobLocation, jobWorkPlace, jobPostedDate, jobApplications = self.getJobProperties()
                    
                    # Store current job info for apply process
                    self.current_job_title = jobTitle
                    self.current_job_company = jobCompany
                    
                    # Existing blacklist and filter checks...
                    
                    # NEW: Get job description and customize resume
                    job_description = self.getJobDescription()
                    if job_description and config.enableResumeCustomization:
                        customized_resume, match_score = self.customizeResumeForJob(
                            jobTitle, jobCompany, job_description
                        )
                        
                        # Skip if match score is too low
                        if match_score < config.minimumMatchScore:
                            lineToWrite = f"{jobProperties} | * 🥵 Low match score: {match_score:.1f}%"
                            self.displayWriteResults(lineToWrite)
                            continue
                    
                    # Continue with existing application process...
                    button = self.easyApplyButton()
                    if button is not False:
                        button.click()
                        # Rest of application process...

# Add to config.py:
# enableResumeCustomization = True
# minimumMatchScore = 60.0  # Minimum match percentage to apply
