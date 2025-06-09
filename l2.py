import time
import math
import random
import os
import re
import json
import threading
import queue
from typing import List, Dict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from ixbrowser_local_api import IXBrowserClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Import your existing utils and config modules
import utils
import constants
import config


class ProfileSession:
    """Represents a single browser profile session"""
    def __init__(self, profile_id, profile_name=None):
        self.profile_id = profile_id
        self.profile_name = profile_name or f"Profile_{profile_id}"
        self.client = IXBrowserClient()
        self.driver = None
        self.applied_count = 0
        self.is_active = False
        

class LinkedinMultiProfileBot:
    def __init__(self, profiles_config):
        """
        Initialize multi-profile bot
        profiles_config: List of dicts with profile info
        Example: [{"id": 211, "name": "Profile1"}, {"id": 212, "name": "Profile2"}]
        """
        self.profiles = [ProfileSession(p['id'], p.get('name')) for p in profiles_config]
        self.job_queue = queue.Queue()
        self.results_lock = threading.Lock()
        self.applied_jobs = self.load_applied_jobs()
        self.total_applied = 0
        
    def load_applied_jobs(self):
        """Load previously applied jobs to avoid duplicates"""
        applied_file = 'data/applied_jobs.json'
        if os.path.exists(applied_file):
            try:
                with open(applied_file, 'r') as f:
                    return set(json.load(f))
            except:
                return set()
        return set()
    
    def save_applied_jobs(self):
        """Save applied jobs to file"""
        applied_file = 'data/applied_jobs.json'
        with self.results_lock:
            with open(applied_file, 'w') as f:
                json.dump(list(self.applied_jobs), f)
    
    def start_profile_browser(self, profile: ProfileSession):
        """Start browser for a specific profile"""
        try:
            # Open profile using IxBrowser API
            response = profile.client.open_profile(
                profile.profile_id, 
                cookies_backup=False, 
                load_profile_info_page=False
            )
            
            if 'debugging_port' not in response:
                raise Exception("Failed to get debugging port from IxBrowser")
            
            debug_port = response['debugging_port']
            
            # Connect Selenium to the running browser
            options = webdriver.ChromeOptions()
            options.debugger_address = f"127.0.0.1:{debug_port}"
            
            webdriver_path = response.get('webdriver')
            if webdriver_path and os.path.exists(webdriver_path):
                service = Service(executable_path=webdriver_path)
                profile.driver = webdriver.Chrome(service=service, options=options)
            else:
                profile.driver = webdriver.Chrome(options=options)
            
            profile.is_active = True
            utils.prGreen(f"[{profile.profile_name}] Successfully connected!")
            return True
            
        except Exception as e:
            utils.prRed(f"[{profile.profile_name}] Error starting browser: {e}")
            return False
    
    def close_profile_browser(self, profile: ProfileSession):
        """Close browser for a specific profile"""
        try:
            if profile.driver:
                profile.driver.quit()
            profile.client.close_profile(profile.profile_id)
            profile.is_active = False
            utils.prGreen(f"[{profile.profile_name}] Browser closed successfully")
        except Exception as e:
            utils.prRed(f"[{profile.profile_name}] Error closing browser: {e}")
    
    def check_login_status(self, profile: ProfileSession):
        """Check if profile is logged into LinkedIn"""
        try:
            profile.driver.get("https://www.linkedin.com/my-items/saved-jobs/")
            time.sleep(3)
            
            jobs_element = profile.driver.find_elements(By.XPATH, "//div[@class='flex-0 pl1 t-black t-normal']")
            print(jobs_element[0])
            return True
        except:
            return False
    
    def generateUrls(self):
        """Generate job search URLs and populate job queue"""
        if not os.path.exists('data'):
            os.makedirs('data')
            
        all_jobs = []
        
        try: 
            # Generate URLs
            linkedinJobLinks = utils.LinkedinUrlGenerate().generateUrlLinks()
            
            # Save URLs to file
            with open('data/urlData.txt', 'w', encoding="utf-8") as file:
                for url in linkedinJobLinks:
                    file.write(url + "\n")
            
            # Process each URL to get individual jobs
            for url in linkedinJobLinks:
                urlWords = utils.urlToKeywords(url)
                all_jobs.append({
                    'url': url,
                    'category': urlWords[0],
                    'location': urlWords[1]
                })
            
            # Add all jobs to queue
            for job in all_jobs:
                self.job_queue.put(job)
                
            utils.prGreen(f"Generated {len(linkedinJobLinks)} search URLs with jobs to process")
            
        except Exception as e:
            utils.prRed(f"Couldn't generate URLs: {e}")
    
    def process_job_search(self, profile: ProfileSession, search_data: dict):
        """Process a job search URL with a specific profile"""
        url = search_data['url']
        category = search_data['category']
        location = search_data['location']
        
        try:
            profile.driver.get(url)
            time.sleep(random.uniform(2, constants.botSpeed))
            
            # Get total jobs count
            try:
                totalJobs = profile.driver.find_element(By.XPATH, '//small').text 
                totalPages = utils.jobsToPages(totalJobs)
            except:
                totalPages = 1
            
            lineToWrite = f"\n[{profile.profile_name}] Category: {category}, Location: {location}, Checking {totalJobs} jobs."
            self.displayWriteResults(lineToWrite, profile.profile_name)
            
            jobs_applied_in_search = 0
            
            for page in range(min(totalPages, 5)):  # Limit pages per search per profile
                if profile.applied_count >= config.max_applications_per_profile:
                    utils.prYellow(f"[{profile.profile_name}] Reached application limit")
                    break
                    
                currentPageJobs = constants.jobsPerPage * page
                pageUrl = url + "&start=" + str(currentPageJobs)
                profile.driver.get(pageUrl)
                time.sleep(random.uniform(1, constants.botSpeed))
                
                # Get job offers on current page
                offersPerPage = profile.driver.find_elements(By.XPATH, '//li[@data-occludable-job-id]')
                
                offerIds = []
                for offer in offersPerPage:
                    offerId = offer.get_attribute("data-occludable-job-id")
                    if offerId:
                        offerIds.append(int(offerId.split(":")[-1]))
                
                # Process each job
                for jobID in offerIds:
                    if profile.applied_count >= config.max_applications_per_profile:
                        break
                        
                    # Check if already applied (by any profile)
                    if str(jobID) in self.applied_jobs:
                        continue
                    
                    success = self.apply_to_job(profile, jobID)
                    if success:
                        jobs_applied_in_search += 1
                        
                        # Add delay between applications
                        delay = random.uniform(
                            config.min_delay_between_applications,
                            config.max_delay_between_applications
                        )
                        time.sleep(delay)
            
            utils.prGreen(f"[{profile.profile_name}] Applied to {jobs_applied_in_search} jobs in {category}, {location}")
            
        except Exception as e:
            utils.prRed(f"[{profile.profile_name}] Error processing search: {e}")
    
    def apply_to_job(self, profile: ProfileSession, jobID: int):
        """Apply to a specific job with a profile"""
        offerPage = f'https://www.linkedin.com/jobs/view/{jobID}'
        
        try:
            profile.driver.get(offerPage)
            time.sleep(random.uniform(1, constants.botSpeed))
            
            # Get job properties
            jobTitle, jobCompany, jobLocation, jobWorkPlace, jobPostedDate, jobApplications = self.getJobProperties(profile)
            
            # Check blacklists
            isBlacklistCompany = any(
                company.casefold() in jobCompany.casefold() 
                for company in config.blacklist
            )
            
            isBlacklistTitle = any(
                title.casefold() in jobTitle.casefold() 
                for title in config.blacklistTitles
            )
            
            isWrongFormat = not re.search(
                config.onlyApplyTitleFormat, jobTitle, re.IGNORECASE
            )
            
            # Format job properties for display
            jobProperties = f"[{profile.profile_name}] | {jobTitle} | {jobCompany} | {jobLocation}"
            
            # Skip if blacklisted
            if isBlacklistCompany:
                lineToWrite = f"{jobProperties} | 🚫 Blacklisted company!"
                self.displayWriteResults(lineToWrite, profile.profile_name)
                return False
            elif isBlacklistTitle:
                lineToWrite = f"{jobProperties} | 🚫 Blacklisted title!"
                self.displayWriteResults(lineToWrite, profile.profile_name)
                return False
            elif isWrongFormat:
                lineToWrite = f"{jobProperties} | 🚫 Title format doesn't match!"
                self.displayWriteResults(lineToWrite, profile.profile_name)
                return False
            
            # Find and click Easy Apply button
            button = self.easyApplyButton(profile)
            
            if button:
                button.click()
                time.sleep(random.uniform(1, constants.botSpeed))
                
                # Try to apply
                result = self.completeApplication(profile, offerPage)
                
                if "Applied" in result or "🥳" in result:
                    # Successfully applied
                    with self.results_lock:
                        self.applied_jobs.add(str(jobID))
                        profile.applied_count += 1
                        self.total_applied += 1
                    
                    lineToWrite = f"{jobProperties} | {result}"
                    self.displayWriteResults(lineToWrite, profile.profile_name)
                    
                    # Save updated applied jobs
                    self.save_applied_jobs()
                    return True
                else:
                    lineToWrite = f"{jobProperties} | {result}"
                    self.displayWriteResults(lineToWrite, profile.profile_name)
                    return False
            else:
                lineToWrite = f"{jobProperties} | ✅ Already applied!"
                self.displayWriteResults(lineToWrite, profile.profile_name)
                return False
                
        except Exception as e:
            utils.prRed(f"[{profile.profile_name}] Error applying to job {jobID}: {e}")
            return False
    
    def completeApplication(self, profile: ProfileSession, offerPage: str):
        """Complete the application process"""
        try:
            # Try direct submit (single page application)
            submit_button = profile.driver.find_element(
                By.CSS_SELECTOR, "button[aria-label='Submit application']"
            )
            submit_button.click()
            time.sleep(random.uniform(1, constants.botSpeed))
            return "🥳 Applied successfully!"
            
        except:
            # Multi-step application
            try:
                profile.driver.find_element(
                    By.CSS_SELECTOR, "button[aria-label='Continue to next step']"
                ).click()
                time.sleep(random.uniform(1, constants.botSpeed))
                
                # Get completion percentage
                comPercentage = profile.driver.find_element(
                    By.XPATH, 'html/body/div[3]/div/div/div[2]/div/div/span'
                ).text
                percenNumber = int(comPercentage[0:comPercentage.index("%")])
                
                return self.applyProcess(profile, percenNumber, offerPage)
                
            except:
                # Handle phone/country requirement
                try:
                    profile.driver.find_element(
                        By.CSS_SELECTOR, f"option[value='urn:li:country:{config.country_code}']"
                    ).click()
                    time.sleep(random.uniform(1, constants.botSpeed))
                    
                    profile.driver.find_element(
                        By.CSS_SELECTOR, 'input'
                    ).send_keys(config.phone_number)
                    time.sleep(random.uniform(1, constants.botSpeed))
                    
                    profile.driver.find_element(
                        By.CSS_SELECTOR, "button[aria-label='Continue to next step']"
                    ).click()
                    time.sleep(random.uniform(1, constants.botSpeed))
                    
                    comPercentage = profile.driver.find_element(
                        By.XPATH, 'html/body/div[3]/div/div/div[2]/div/div/span'
                    ).text
                    percenNumber = int(comPercentage[0:comPercentage.index("%")])
                    
                    return self.applyProcess(profile, percenNumber, offerPage)
                    
                except:
                    return "🥵 Cannot apply - extra info needed"
    
    def applyProcess(self, profile: ProfileSession, percentage: int, offerPage: str):
        """Handle multi-step application process"""
        applyPages = math.floor(100 / percentage) 
        
        try:    
            # Click through application pages
            for pages in range(applyPages - 2):
                profile.driver.find_element(
                    By.CSS_SELECTOR, "button[aria-label='Continue to next step']"
                ).click()
                time.sleep(random.uniform(1, constants.botSpeed))

            # Review application
            profile.driver.find_element(
                By.CSS_SELECTOR, "button[aria-label='Review your application']"
            ).click() 
            time.sleep(random.uniform(1, constants.botSpeed))

            # Unfollow company if configured
            if config.followCompanies is False:
                try:
                    profile.driver.find_element(
                        By.CSS_SELECTOR, "label[for='follow-company-checkbox']"
                    ).click() 
                    time.sleep(random.uniform(1, constants.botSpeed))
                except:
                    pass

            # Submit application
            profile.driver.find_element(
                By.CSS_SELECTOR, "button[aria-label='Submit application']"
            ).click()
            time.sleep(random.uniform(1, constants.botSpeed))

            return "🥳 Applied successfully!"
        except:
            return f"🥵 {applyPages} pages - couldn't complete application"
    
    def getJobProperties(self, profile: ProfileSession):
        """Extract job properties from the job page"""
        jobTitle = ""
        jobCompany = ""
        jobLocation = ""
        jobWorkPlace = ""
        jobPostedDate = ""
        jobApplications = ""

        try:
            jobTitle = profile.driver.find_element(
                By.XPATH, "//h1[contains(@class, 'job-title')]"
            ).get_attribute("innerHTML").strip()
        except:
            pass
            
        try:
            jobCompany = profile.driver.find_element(
                By.XPATH, "//a[contains(@class, 'ember-view t-black t-normal')]"
            ).get_attribute("innerHTML").strip()
        except:
            pass
            
        try:
            jobLocation = profile.driver.find_element(
                By.XPATH, "//span[contains(@class, 'bullet')]"
            ).get_attribute("innerHTML").strip()
        except:
            pass
            
        try:
            jobWorkPlace = profile.driver.find_element(
                By.XPATH, "//span[contains(@class, 'workplace-type')]"
            ).get_attribute("innerHTML").strip()
        except:
            pass
            
        try:
            jobPostedDate = profile.driver.find_element(
                By.XPATH, "//span[contains(@class, 'posted-date')]"
            ).get_attribute("innerHTML").strip()
        except:
            pass
            
        try:
            jobApplications = profile.driver.find_element(
                By.XPATH, "//span[contains(@class, 'applicant-count')]"
            ).get_attribute("innerHTML").strip()
        except:
            pass

        return jobTitle, jobCompany, jobLocation, jobWorkPlace, jobPostedDate, jobApplications
    
    def easyApplyButton(self, profile: ProfileSession):
        """Find the Easy Apply button"""
        try:
            button = profile.driver.find_element(
                By.XPATH, '//button[contains(@class, "jobs-apply-button")]'
            )
            return button
        except:
            return False
    
    def displayWriteResults(self, lineToWrite: str, profile_name: str):
        """Display and write results to file"""
        try:
            print(lineToWrite)
            # Write to profile-specific file
            timeStr = time.strftime("%Y%m%d")
            fileName = f"Applied_Jobs_{profile_name}_{timeStr}.txt"
            
            with self.results_lock:
                with open(f"data/{fileName}", 'a', encoding="utf-8") as f:
                    f.write(lineToWrite + "\n")
                    
        except Exception as e:
            utils.prRed(f"Error in DisplayWriteResults: {e}")
    
    def worker_thread(self, profile: ProfileSession):
        """Worker thread for a single profile"""
        # Start browser for this profile
        if not self.start_profile_browser(profile):
            utils.prRed(f"[{profile.profile_name}] Failed to start browser")
            return
        
        try:
            # Check login status
            if not self.check_login_status(profile):
                utils.prYellow(f"[{profile.profile_name}] Not logged in. Please log in manually.")
                utils.prYellow("Press Enter when ready...")
                input()
                
                if not self.check_login_status(profile):
                    utils.prRed(f"[{profile.profile_name}] Login failed")
                    return
            
            utils.prGreen(f"[{profile.profile_name}] Ready to apply!")
            
            # Process jobs from queue
            while not self.job_queue.empty() and profile.applied_count < config.max_applications_per_profile:
                try:
                    # Get next job search from queue
                    search_data = self.job_queue.get(timeout=1)
                    self.process_job_search(profile, search_data)
                    
                    # Add delay between searches
                    time.sleep(random.uniform(30, 60))
                    
                except queue.Empty:
                    break
                except Exception as e:
                    utils.prRed(f"[{profile.profile_name}] Error in worker: {e}")
                    
        finally:
            # Close browser
            self.close_profile_browser(profile)
            utils.prYellow(f"[{profile.profile_name}] Applied to {profile.applied_count} jobs")
    
    def run_sequential(self):
        """Run profiles sequentially (one at a time)"""
        utils.prGreen("Running profiles sequentially...")
        
        for profile in self.profiles:
            utils.prYellow(f"\n--- Starting {profile.profile_name} ---")
            self.worker_thread(profile)
            
            # Delay between profiles
            if profile != self.profiles[-1]:  # Not the last profile
                delay = random.uniform(60, 120)
                utils.prYellow(f"Waiting {delay:.0f} seconds before next profile...")
                time.sleep(delay)
    
    def run_parallel(self, max_concurrent=2):
        """Run multiple profiles in parallel"""
        utils.prGreen(f"Running up to {max_concurrent} profiles in parallel...")
        
        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            futures = []
            
            for i, profile in enumerate(self.profiles):
                # Stagger the start times
                if i > 0:
                    time.sleep(random.uniform(10, 20))
                    
                future = executor.submit(self.worker_thread, profile)
                futures.append(future)
                
                # Limit concurrent profiles
                if len(futures) >= max_concurrent:
                    # Wait for one to complete before starting another
                    completed, futures = wait(futures, return_when=FIRST_COMPLETED)
                    futures = list(futures)
            
            # Wait for all remaining profiles to complete
            for future in as_completed(futures):
                pass
    
    def run(self, mode='sequential', max_concurrent=2):
        """
        Main run method
        mode: 'sequential' or 'parallel'
        max_concurrent: max profiles to run at once (for parallel mode)
        """
        start_time = time.time()
        
        utils.prGreen("=== LinkedIn Multi-Profile Bot Starting ===")
        utils.prGreen(f"Profiles to use: {len(self.profiles)}")
        utils.prGreen(f"Mode: {mode}")
        
        # Generate URLs and populate job queue
        self.generateUrls()
        
        if self.job_queue.empty():
            utils.prRed("No jobs to process!")
            return
        
        # Run profiles
        if mode == 'parallel':
            self.run_parallel(max_concurrent)
        else:
            self.run_sequential()
        
        # Summary
        elapsed_time = time.time() - start_time
        utils.prGreen("\n=== Summary ===")
        utils.prGreen(f"Total applications: {self.total_applied}")
        utils.prGreen(f"Time elapsed: {elapsed_time/60:.1f} minutes")
        
        for profile in self.profiles:
            utils.prGreen(f"{profile.profile_name}: {profile.applied_count} applications")


def main():
    """Main function to run the multi-profile bot"""
    
    # Load profiles from config
    profiles_config = config.ixbrowser_profiles
    
    if not profiles_config:
        utils.prRed("No profiles configured! Please update config.py")
        return
    
    # Initialize bot
    bot = LinkedinMultiProfileBot(profiles_config)
    
    # Run bot
    # Options: 'sequential' or 'parallel'
    # For parallel, you can set max_concurrent (default 2)
    bot.run(mode=config.profile_run_mode, max_concurrent=config.max_concurrent_profiles)


if __name__ == "__main__":
    main()