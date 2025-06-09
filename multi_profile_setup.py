"""
Example configurations for running the LinkedIn bot with multiple profiles
"""

# Example 1: Two profiles running sequentially (recommended for beginners)
config_sequential_basic = {
    "ixbrowser_profiles": [
        {"id": 211, "name": "MainProfile"},
        {"id": 212, "name": "SecondaryProfile"},
    ],
    "profile_run_mode": "sequential",
    "max_applications_per_profile": 30,
    "delay_between_profiles": 120,  # 2 minutes between profiles
}

# Example 2: Three profiles running in parallel (2 at a time)
config_parallel_moderate = {
    "ixbrowser_profiles": [
        {"id": 211, "name": "Profile1"},
        {"id": 212, "name": "Profile2"},
        {"id": 213, "name": "Profile3"},
    ],
    "profile_run_mode": "parallel",
    "max_concurrent_profiles": 2,  # Only 2 profiles run at once
    "max_applications_per_profile": 25,
    "stagger_start_delay": 20,  # 20 seconds between starting each profile
}

# Example 3: Large-scale operation with 5 profiles
config_large_scale = {
    "ixbrowser_profiles": [
        {"id": 211, "name": "Profile1"},
        {"id": 212, "name": "Profile2"},
        {"id": 213, "name": "Profile3"},
        {"id": 214, "name": "Profile4"},
        {"id": 215, "name": "Profile5"},
    ],
    "profile_run_mode": "parallel",
    "max_concurrent_profiles": 3,  # Run 3 profiles simultaneously
    "max_applications_per_profile": 20,  # Lower limit per profile
    "stagger_start_delay": 30,  # More delay for stability
}

# Example 4: Conservative approach for maximum safety
config_conservative = {
    "ixbrowser_profiles": [
        {"id": 211, "name": "PrimaryAccount"},
        {"id": 212, "name": "BackupAccount"},
    ],
    "profile_run_mode": "sequential",
    "max_applications_per_profile": 15,  # Very conservative
    "delay_between_profiles": 300,  # 5 minutes between profiles
    "min_delay_between_applications": 60,  # 1 minute minimum between applications
    "max_delay_between_applications": 180,  # 3 minutes maximum
}

# Example usage in your config.py:
"""
# Copy one of these configurations to your config.py file
# For example, to use the sequential basic configuration:

ixbrowser_profiles = [
    {"id": 211, "name": "MainProfile"},
    {"id": 212, "name": "SecondaryProfile"},
]
profile_run_mode = "sequential"
max_concurrent_profiles = 1
max_applications_per_profile = 30
delay_between_profiles = 120
"""

# Tips for choosing a configuration:
"""
1. Start with Sequential Mode:
   - Easier to monitor and debug
   - Lower risk of detection
   - Good for testing your setup

2. Move to Parallel Mode when:
   - You're comfortable with the bot
   - You need to apply to more jobs quickly
   - Your profiles are well-established

3. Profile Management:
   - Use different email domains for each profile
   - Vary the profile information slightly
   - Don't use identical resumes across profiles

4. Safety Guidelines:
   - Start with lower application limits
   - Increase delays if you notice issues
   - Monitor each profile's performance
   - Take breaks between sessions
"""

# Advanced: Dynamic profile allocation based on job types
def create_specialized_profiles():
    """
    Example of creating profiles for different job categories
    """
    frontend_profiles = [
        {"id": 211, "name": "Frontend_React"},
        {"id": 212, "name": "Frontend_Vue"},
    ]
    
    fullstack_profiles = [
        {"id": 213, "name": "Fullstack_Node"},
        {"id": 214, "name": "Fullstack_Python"},
    ]
    
    # You could modify the bot to use different profiles for different keywords
    return {
        "frontend": frontend_profiles,
        "fullstack": fullstack_profiles
    }

# Monitoring function to track profile performance
def monitor_profile_performance():
    """
    Example of how to track which profiles are performing best
    """
    import json
    import os
    from datetime import datetime
    
    performance_file = "data/profile_performance.json"
    
    if os.path.exists(performance_file):
        with open(performance_file, 'r') as f:
            performance = json.load(f)
    else:
        performance = {}
    
    # Update this after each session
    session_data = {
        "date": datetime.now().isoformat(),
        "profiles": {
            "Profile1": {"applications": 25, "success_rate": 0.8},
            "Profile2": {"applications": 20, "success_rate": 0.75},
        }
    }
    
    # Add to performance tracking
    performance[datetime.now().strftime("%Y-%m-%d")] = session_data
    
    with open(performance_file, 'w') as f:
        json.dump(performance, f, indent=2)
    
    return performance

if __name__ == "__main__":
    print("This file contains example configurations for the multi-profile bot.")
    print("Copy the configuration you want to use into your config.py file.")
    print("\nAvailable configurations:")
    print("1. config_sequential_basic - Good for beginners")
    print("2. config_parallel_moderate - Balanced approach")
    print("3. config_large_scale - For experienced users")
    print("4. config_conservative - Maximum safety")