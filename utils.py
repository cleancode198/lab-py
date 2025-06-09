import math
import constants
import config
from typing import List
import time
import threading
import os

from selenium.webdriver.firefox.options import Options

# Thread lock for file operations
file_lock = threading.Lock()

def browserOptions():
    """Firefox browser options (kept for compatibility)"""
    options = Options()
    firefoxProfileRootDir = config.firefoxProfileRootDir
    options.add_argument("--start-maximized")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-extensions")
    options.add_argument('--disable-gpu')
    if(config.headless):
        options.add_argument("--headless")

    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--incognito")
    options.add_argument("-profile")
    options.add_argument(firefoxProfileRootDir)

    return options

def prRed(prt):
    """Print in red color"""
    with file_lock:
        print(f"\033[91m{prt}\033[00m")

def prGreen(prt):
    """Print in green color"""
    with file_lock:
        print(f"\033[92m{prt}\033[00m")

def prYellow(prt):
    """Print in yellow color"""
    with file_lock:
        print(f"\033[93m{prt}\033[00m")

def getUrlDataFile():
    """Read URL data file with thread safety"""
    urlData = []
    try:
        with file_lock:
            with open('data/urlData.txt', 'r') as file:
                urlData = file.readlines()
    except FileNotFoundError:
        text = "FileNotFound: urlData.txt file is not found. Please run generateUrls() first."
        prRed(text)
    return urlData

def jobsToPages(numOfJobs: str) -> int:
    """Convert job count to number of pages"""
    number_of_pages = 1

    if (' ' in numOfJobs):
        spaceIndex = numOfJobs.index(' ')
        totalJobs = (numOfJobs[0:spaceIndex])
        totalJobs_int = int(totalJobs.replace(',', ''))
        number_of_pages = math.ceil(totalJobs_int/constants.jobsPerPage)
        if (number_of_pages > 40): 
            number_of_pages = 40
    else:
        try:
            number_of_pages = int(numOfJobs)
        except:
            number_of_pages = 1

    return number_of_pages

def urlToKeywords(url: str) -> List[str]:
    """Extract keywords and location from URL"""
    try:
        keywordUrl = url[url.index("keywords=")+9:]
        keyword = keywordUrl[0:keywordUrl.index("&")] 
        locationUrl = url[url.index("location=")+9:]
        location = locationUrl[0:locationUrl.index("&")] 
        return [keyword, location]
    except:
        return ["Unknown", "Unknown"]

def writeResults(text: str, profile_name: str = None):
    """Write results to file with thread safety and profile support"""
    timeStr = time.strftime("%Y%m%d")
    
    # Create profile-specific filename if profile name is provided
    if profile_name:
        fileName = f"Applied_Jobs_{profile_name}_{timeStr}.txt"
    else:
        fileName = f"Applied_Jobs_DATA_{timeStr}.txt"
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    filepath = os.path.join('data', fileName)
    
    with file_lock:
        try:
            # Check if file exists and has content
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                # Read existing content
                with open(filepath, 'r', encoding="utf-8") as file:
                    lines = []
                    for line in file:
                        if "----" not in line:
                            lines.append(line)
                
                # Write updated content
                with open(filepath, 'w', encoding="utf-8") as f:
                    f.write(f"---- Applied Jobs Data ({profile_name or 'General'}) ---- created at: {timeStr}\n")
                    f.write("---- Number | Job Title | Company | Location | Work Place | Posted Date | Applications | Result\n")
                    for line in lines: 
                        f.write(line)
                    f.write(text + "\n")
            else:
                # Create new file
                with open(filepath, 'w', encoding="utf-8") as f:
                    f.write(f"---- Applied Jobs Data ({profile_name or 'General'}) ---- created at: {timeStr}\n")
                    f.write("---- Number | Job Title | Company | Location | Work Place | Posted Date | Applications | Result\n")
                    f.write(text + "\n")
                    
        except Exception as e:
            prRed(f"Error writing results: {e}")

def printInfoMes(bot: str):
    """Print info message"""
    prYellow(f"ℹ️ {bot} is starting soon... ")

def donate(driver):
    """Donation message (kept for compatibility)"""
    prYellow('If you like the project, please support the developer!')
    try:
        driver.get('https://github.com/sponsors')  # Updated to a generic link
    except Exception as e:
        prRed(f"Error in donate: {e}")

class LinkedinUrlGenerate:
    """Generate LinkedIn job search URLs based on configuration"""
    
    def generateUrlLinks(self):
        """Generate all URL combinations from config"""
        path = []
        for location in config.location:
            for keyword in config.keywords:
                url = (constants.linkJobUrl + "?f_AL=true&keywords=" + keyword + 
                      self.jobType() + self.remote() + self.checkJobLocation(location) + 
                      self.jobExp() + self.datePosted() + self.salary() + self.sortBy())
                path.append(url)
        return path

    def checkJobLocation(self, job):
        """Convert location to LinkedIn geo ID"""
        jobLoc = "&location=" + job
        
        location_map = {
            "asia": "&geoId=102393603",
            "europe": "&geoId=100506914",
            "northamerica": "&geoId=102221843",
            "southamerica": "&geoId=104514572",
            "australia": "&geoId=101452733",
            "africa": "&geoId=103537801",
            "emea": "&geoId=100506914"  # Default to Europe for EMEA
        }
        
        job_lower = job.casefold()
        for key, geo_id in location_map.items():
            if key in job_lower:
                jobLoc += geo_id
                break
                
        return jobLoc

    def jobExp(self):
        """Build experience level filter"""
        jobtExpArray = config.experienceLevels
        if not jobtExpArray:
            return ""
            
        firstJobExp = jobtExpArray[0]
        jobExp = ""
        
        exp_map = {
            "Internship": "1",
            "Entry level": "2",
            "Associate": "3",
            "Mid-Senior level": "4",
            "Director": "5",
            "Executive": "6"
        }
        
        # First experience level
        if firstJobExp in exp_map:
            jobExp = f"&f_E={exp_map[firstJobExp]}"
        
        # Additional experience levels
        for exp in jobtExpArray[1:]:
            if exp in exp_map:
                jobExp += f"%2C{exp_map[exp]}"
                
        return jobExp

    def datePosted(self):
        """Build date posted filter"""
        if not config.datePosted:
            return ""
            
        date_map = {
            "Any Time": "",
            "Past Month": "&f_TPR=r2592000&",
            "Past Week": "&f_TPR=r604800&",
            "Past 24 hours": "&f_TPR=r86400&"
        }
        
        return date_map.get(config.datePosted[0], "")

    def jobType(self):
        """Build job type filter"""
        jobTypeArray = config.jobType
        if not jobTypeArray:
            return ""
            
        firstjobType = jobTypeArray[0]
        jobType = ""
        
        type_map = {
            "Full-time": "F",
            "Part-time": "P",
            "Contract": "C",
            "Temporary": "T",
            "Volunteer": "V",
            "Internship": "I",
            "Other": "O"
        }
        
        # First job type
        if firstjobType in type_map:
            jobType = f"&f_JT={type_map[firstjobType]}"
        
        # Additional job types
        for jtype in jobTypeArray[1:]:
            if jtype in type_map:
                jobType += f"%2C{type_map[jtype]}"
                
        jobType += "&"
        return jobType

    def remote(self):
        """Build remote work filter"""
        remoteArray = config.remote
        if not remoteArray:
            return ""
            
        firstJobRemote = remoteArray[0]
        jobRemote = ""
        
        remote_map = {
            "On-site": "1",
            "Remote": "2",
            "Hybrid": "3"
        }
        
        # First remote option
        if firstJobRemote in remote_map:
            jobRemote = f"f_WT={remote_map[firstJobRemote]}"
        
        # Additional remote options
        for remote_type in remoteArray[1:]:
            if remote_type in remote_map:
                jobRemote += f"%2C{remote_map[remote_type]}"
                
        return jobRemote

    def salary(self):
        """Build salary filter"""
        if not config.salary:
            return ""
            
        salary_map = {
            "$40,000+": "f_SB2=1&",
            "$60,000+": "f_SB2=2&",
            "$80,000+": "f_SB2=3&",
            "$100,000+": "f_SB2=4&",
            "$120,000+": "f_SB2=5&",
            "$140,000+": "f_SB2=6&",
            "$160,000+": "f_SB2=7&",
            "$180,000+": "f_SB2=8&",
            "$200,000+": "f_SB2=9&"
        }
        
        return salary_map.get(config.salary[0], "")

    def sortBy(self):
        """Build sort order"""
        if not config.sort:
            return ""
            
        sort_map = {
            "Recent": "sortBy=DD",
            "Relevant": "sortBy=R"
        }
        
        return sort_map.get(config.sort[0], "")

# Multi-profile specific utilities
def createProfileSpecificDir(profile_name: str):
    """Create a directory for profile-specific data"""
    profile_dir = f"data/profiles/{profile_name}"
    os.makedirs(profile_dir, exist_ok=True)
    return profile_dir

def logProfileActivity(profile_name: str, activity: str):
    """Log profile-specific activity with timestamp"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {activity}\n"
    
    log_file = f"data/profiles/{profile_name}/activity.log"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    with file_lock:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)

def getProfileStats(profile_name: str) -> dict:
    """Get statistics for a specific profile"""
    stats = {
        'total_applications': 0,
        'successful': 0,
        'failed': 0,
        'last_active': None
    }
    
    # Read profile's log file
    timeStr = time.strftime("%Y%m%d")
    log_file = f"data/Applied_Jobs_{profile_name}_{timeStr}.txt"
    
    if os.path.exists(log_file):
        with file_lock:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if "🥳" in line or "Successfully applied" in line:
                        stats['successful'] += 1
                        stats['total_applications'] += 1
                    elif "🥵" in line or "Cannot apply" in line:
                        stats['failed'] += 1
                        stats['total_applications'] += 1
        
        stats['last_active'] = time.strftime("%Y-%m-%d %H:%M:%S")
    
    return stats