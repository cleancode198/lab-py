# LinkedIn URL constants
linkJobUrl = "https://www.linkedin.com/jobs/search/"

# Pagination
jobsPerPage = 25

# Speed settings (in seconds)
fast = 2
medium = 3
slow = 5

# Default bot speed
botSpeed = slow

# Maximum pages to process per search
maxPagesPerSearch = 40

# Application tracking
appliedJobsFile = "data/applied_jobs.json"

# Timeouts (in seconds)
pageLoadTimeout = 30
elementWaitTimeout = 10

# Anti-detection delays
humanLikeDelayMin = 0.5
humanLikeDelayMax = 2.0

# Session limits
maxApplicationsPerHour = 20
maxApplicationsPerDay = 100

# Multi-Profile specific constants
maxSearchesPerProfile = 10  # Maximum job searches per profile per session
profileSwitchDelay = 60  # Seconds to wait when switching profiles
parallelStartDelay = 15  # Seconds between starting parallel profiles
maxRetryAttempts = 3  # Maximum retries for failed operations

# File naming
logFilePrefix = "Applied_Jobs_"
performanceFile = "profile_performance.json"