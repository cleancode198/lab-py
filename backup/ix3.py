from ixbrowser_local_api import IXBrowserClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import json
import os

class IxBrowserJobAutomation:
    def __init__(self):
        self.client = IXBrowserClient()
        self.driver = None
        
    def start_profile(self, profile_id):
        """Start IxBrowser profile and connect Selenium"""
        try:
            # Open profile using official API
            response = self.client.open_profile(profile_id, cookies_backup=False, load_profile_info_page=False)
            # print("Response:", json.dumps(response, indent=2))
            # 	open_result = c.open_profile(profile_id, cookies_backup=False, load_profile_info_page=False)
            
            # Get the debug port from response
            debug_port = response['debugging_port']
            
            # Connect Selenium to the running browser
            options = webdriver.ChromeOptions()
            options.debugger_address = f"127.0.0.1:{debug_port}"
            
            webdriver_path = response['webdriver']
            # Use IxBrowser's ChromeDriver if provided
            if webdriver_path and os.path.exists(webdriver_path):
                print(f"Using IxBrowser ChromeDriver: {webdriver_path}")
                service = Service(executable_path=webdriver_path)
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                # Try connecting without specifying driver
                print("Connecting without specific driver...")
                self.driver = webdriver.Chrome(options=options)
            
            print(f"Successfully connected to profile: {profile_id}")
            return True
            
        except Exception as e:
            print(f"Error starting profile: {e}")
            return False
    
    def close_profile(self, profile_id):
        """Close the profile properly"""
        try:
            self.client.close_profile(profile_id)
            print("Profile closed successfully")
        except Exception as e:
            print(f"Error closing profile: {e}")
    
    def apply_on_linkedin(self, job_url):
        print(f"job_url {job_url}")
        """Example LinkedIn Easy Apply automation"""
        try:
            self.driver.get(job_url)
            # time.sleep(random.uniform(3, 5))
            
            # Wait for and click Easy Apply button
            # easy_apply_button = WebDriverWait(self.driver, 10).until(
            #     EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'jobs-apply-button')]"))
            # )
            # easy_apply_button.click()
            
            # Add your application logic here
            # ...
            
        except Exception as e:
            print(f"Error applying to job: {e}")

def main():
    # Initialize automation
    automation = IxBrowserJobAutomation()
    
    profile_id = 211
    
    # Start automation
    if automation.start_profile(profile_id):
        try:
            # Example job URLs
            job_urls = [
                "https://www.linkedin.com/",
                # "https://www.linkedin.com/jobs/view/1234567890",
                # Add more job URLs
            ]
            
            for job_url in job_urls:
                automation.apply_on_linkedin(job_url)
                # Random delay between applications
                time.sleep(random.uniform(60, 180))
                
        finally:
            # Always close the profile properly
            automation.close_profile(profile_id)

if __name__ == "__main__":
    main()
