# User Information
firstname = "Marko"
lastname = "Kujacic"
country_code = "ee"  # Estonia country code for LinkedIn
phone_number = "712 3233"

# Browser Settings
headless = False  # Don't use headless mode with IxBrowser
firefoxProfileRootDir = r""  # Not needed for IxBrowser

# Location Settings
# You can use: ["Poland", "Singapore", "New York City Metropolitan Area", "Monroe County"]
# Or continents: ["Europe", "Asia", "Australia", "NorthAmerica", "SouthAmerica", "EMEA"]
location = ["EMEA"]

# Job Search Keywords
keywords = ["react", "javascript", "frontend", "typescript"]

# Experience Level Filter
# Options: ["Internship", "Entry level", "Associate", "Mid-Senior level", "Director", "Executive"]
experienceLevels = ["Entry level", "Associate", "Mid-Senior level", "Director", "Executive"]

# Time Filter
# Options: ["Any Time", "Past Month", "Past Week", "Past 24 hours"]
datePosted = ["Any Time"]

# Employment Type
# Options: ["Full-time", "Part-time", "Contract", "Temporary", "Volunteer", "Internship", "Other"]
jobType = ["Full-time", "Part-time", "Contract"]

# Work Location Type
# Options: ["On-site", "Remote", "Hybrid"]
remote = ["Remote"]

# Salary Filter
# Options: ["$40,000+", "$60,000+", "$80,000+", "$100,000+", "$120,000+", "$140,000+", "$160,000+", "$180,000+", "$200,000+"]
salary = ["$60,000+"]

# Sort Order
# Options: ["Recent"] or ["Relevant"]
sort = ["Recent"]

# Company Blacklist - Companies to avoid
blacklist = [
    "EPAM", "primeit", "ERP", "Luxoft", "Intellias", "GR4", "Devoteam", 
    "Signify Technology", "Crossover", "YouGov", "Trust In SODA", "URBAN LINKER", 
    "ALTEN", "VIEWNEXT", "Braintrust", "Mentor Talent Acquisition", "Hays", 
    "Theta", "atSistemas", "Cloudflare", "Solas IT Recruitment", "THRIVE", 
    "Noir", "Treatwell", "Storyteq", "Vivid", "Infinity Quest"
]

# Title Keywords Blacklist - Skip jobs with these keywords in title
blacklistTitles = [
    "designer", "backend", "back end", "back-end", "DevOps", "Quality Assurance", 
    "Data Engineer", "Mentor", "Microsoft Dynamics 365", "Sales", "AEM", "Test", 
    "CRM", "Embedded", "Adult", "Intern", "Java ", ".Net", "DotNet", "Rust", 
    "Kotlin", "Swift", "Objective C", "Ruby on Rails", "PHP", "WordPress", 
    "Drupal", "C++", "C#", "Linux"
]

# Whitelist Settings (leave empty to apply to all companies)
onlyApply = [""]  # Only apply to these companies (empty = all companies)
onlyApplyTitles = [""]  # Only apply to jobs with these keywords in title

# Title Format Filter - Regular expression to match acceptable job titles
# This regex matches frontend/fullstack positions with various title formats
onlyApplyTitleFormat = "(javascript|typescript|frontend|front-end|front end|fullstack|full-stack|full stack|react|angular|vue|next|nuxt|gatsby|node|express|nest|js|software|web).*(dev|engineer|manager|architect|programmer|expert)"

# Application Settings
followCompanies = False  # Don't auto-follow companies after applying

# IxBrowser Profile Settings
# Configure multiple profiles here
ixbrowser_profiles = [
    {"id": 211, "name": "Profile1"},
    {"id": 212, "name": "Profile2"},
    # Add more profiles as needed
    # {"id": 213, "name": "Profile3"},
]

# Multi-Profile Settings
profile_run_mode = "sequential"  # Options: "sequential" or "parallel"
max_concurrent_profiles = 2  # Maximum profiles to run simultaneously (for parallel mode)

# Bot Behavior Settings
max_applications_per_profile = 30  # Max applications per profile per session
max_applications_per_session = 100  # Total max applications across all profiles
min_delay_between_applications = 30  # Minimum seconds between applications
max_delay_between_applications = 90  # Maximum seconds between applications

# Profile Rotation Settings
delay_between_profiles = 60  # Seconds to wait between switching profiles (sequential mode)
stagger_start_delay = 15  # Seconds between starting each profile (parallel mode)