# LinkedIn IxBrowser Multi-Profile Job Automation Bot

An advanced LinkedIn Easy Apply bot that uses multiple IxBrowser profiles for distributed automation, anti-detection, and efficient job applications.

## Features

- **Multi-Profile Support**: Run multiple LinkedIn accounts simultaneously or sequentially
- **Anti-Detection**: Uses IxBrowser profiles to avoid LinkedIn automation detection
- **Smart Filtering**: Filters jobs by title, company, location, salary, and more
- **Blacklist Support**: Avoid specific companies or job titles
- **Multi-Step Applications**: Handles complex application forms
- **Duplicate Prevention**: Tracks applications across all profiles to avoid duplicates
- **Parallel & Sequential Modes**: Choose between running profiles together or one at a time
- **Session Management**: Automatic retries and error handling
- **Profile-Specific Logging**: Separate logs for each profile

## Prerequisites

1. **IxBrowser**: Install and set up IxBrowser with a LinkedIn profile
2. **Python 3.8+**: Required for running the bot
3. **Dependencies**: Install required packages:
   ```bash
   pip install selenium
   pip install ixbrowser_local_api
   ```

## Setup

1. **Configure IxBrowser Profiles**:
   - Create multiple profiles in IxBrowser
   - Log into LinkedIn manually in each profile
   - Note all profile IDs

2. **Update Configuration**:
   - Edit `config.py` with your preferences:
     - Add all profiles to `ixbrowser_profiles` list:
       ```python
       ixbrowser_profiles = [
           {"id": 211, "name": "Profile1"},
           {"id": 212, "name": "Profile2"},
           # Add more as needed
       ]
       ```
     - Choose run mode: `"sequential"` or `"parallel"`
     - Set `max_concurrent_profiles` for parallel mode
     - Update personal info for each profile
     - Configure job search criteria
     - Customize blacklists and filters

3. **Create Data Directory**:
   ```bash
   mkdir data
   ```

## Usage

1. **Start IxBrowser**: Make sure IxBrowser is running with all configured profiles

2. **Configure Profiles**: Update `config.py` with your profiles:
   ```python
   ixbrowser_profiles = [
       {"id": 211, "name": "Profile1"},
       {"id": 212, "name": "Profile2"},
   ]
   ```

3. **Choose Run Mode**:
   - Sequential: `profile_run_mode = "sequential"`
   - Parallel: `profile_run_mode = "parallel"`

4. **Run the Bot**:
   ```bash
   python linkedin_ixbrowser_bot.py
   ```

5. **Monitor Progress**: 
   - Watch the console for real-time updates
   - Each profile's progress is logged separately
   - Check `data/` folder for detailed logs

6. **Analyze Performance**:
   ```bash
   python profile_monitor.py
   ```

## Configuration Options

### Multi-Profile Settings
- `ixbrowser_profiles`: List of profile configurations
  ```python
  [{"id": 211, "name": "Profile1"}, {"id": 212, "name": "Profile2"}]
  ```
- `profile_run_mode`: How to run profiles
  - `"sequential"`: One profile at a time (safer)
  - `"parallel"`: Multiple profiles simultaneously (faster)
- `max_concurrent_profiles`: Max profiles running at once (parallel mode)
- `max_applications_per_profile`: Application limit per profile

### Essential Settings
- `keywords`: Job search keywords (e.g., ["react", "frontend"])
- `location`: Where to search (e.g., ["Remote", "Europe"])

### Filtering Options
- `experienceLevels`: Filter by experience level
- `jobType`: Filter by employment type
- `salary`: Minimum salary requirement
- `blacklist`: Companies to avoid
- `blacklistTitles`: Job title keywords to avoid
- `onlyApplyTitleFormat`: Regex pattern for acceptable titles

### Bot Behavior
- `botSpeed`: Delay between actions (fast/medium/slow)
- `followCompanies`: Whether to follow companies after applying
- `delay_between_profiles`: Wait time between profiles (sequential mode)
- `stagger_start_delay`: Delay between starting profiles (parallel mode)

## File Structure

```
linkedin-bot/
├── linkedin_ixbrowser_bot.py  # Main multi-profile bot script
├── config.py                   # Your configuration
├── constants.py                # Bot constants
├── utils.py                    # Utility functions
└── data/                       # Generated data
    ├── urlData.txt            # Generated job URLs
    ├── applied_jobs.json      # Tracks all applied jobs
    ├── Applied_Jobs_Profile1_[date].txt  # Profile-specific logs
    └── Applied_Jobs_Profile2_[date].txt  # Profile-specific logs
```

## Multi-Profile Operation Modes

### Sequential Mode (Recommended)
- Runs one profile at a time
- Safer and more stable
- Better for avoiding detection
- Configurable delay between profiles

### Parallel Mode
- Runs multiple profiles simultaneously
- Faster but requires more resources
- Set `max_concurrent_profiles` to control load
- Profiles start with staggered delays

## Important Notes

1. **Rate Limiting**: The bot includes delays to avoid detection. Don't reduce these!

2. **Session Management**: The bot will automatically retry on errors and manage sessions

3. **Manual Intervention**: Some applications may require manual input for complex forms

4. **LinkedIn ToS**: Automated applications may violate LinkedIn's Terms of Service. Use at your own risk!

## Troubleshooting

### "Failed to start browser"
- Ensure IxBrowser is running
- Check all profile IDs are correct
- Verify each profile exists in IxBrowser
- Make sure no profile is already in use

### "Cannot apply to this job"
- The job may require additional information
- Check if already applied by another profile
- Verify your profile is complete

### "Blacklisted company/title"
- This is normal - the bot is filtering based on your config
- Adjust blacklists in config.py if needed

### Multi-Profile Specific Issues

#### "Profile X not responding"
- Check if the profile is properly configured in IxBrowser
- Ensure the profile isn't being used elsewhere
- Try restarting IxBrowser

#### "High failure rate on Profile Y"
- The profile may be rate-limited
- Check if the LinkedIn account needs verification
- Consider reducing applications per profile

#### "Duplicate applications across profiles"
- This shouldn't happen - check `applied_jobs.json`
- Ensure all profiles are using the same data directory
- Restart the bot to reload the applied jobs list

#### "Parallel mode crashes"
- Reduce `max_concurrent_profiles`
- Check system resources (RAM/CPU)
- Try sequential mode first

## Safety Tips

1. **Start Small**: Test with a limited number of applications first
2. **Monitor Activity**: Watch the bot during initial runs
3. **Use Delays**: Don't set bot speed to "fast" immediately
4. **Profile Rotation**: Consider using multiple IxBrowser profiles
5. **Take Breaks**: Don't run the bot 24/7

## Additional Tools

### Profile Manager
Manage and test your IxBrowser profiles:

```bash
python profile_manager.py
```

Features:
- Test all configured profiles
- Add new profiles interactively
- View profile statistics
- Cleanup old log files
- Reset applied jobs list

### Performance Monitor
Monitor and analyze the performance of all your profiles:

```bash
python profile_monitor.py
```

Features:
- Generate performance reports
- Track success rates per profile
- View trends over time
- Get recommendations for improvement

### Example Configurations
See `example_multi_profile_setup.py` for various configuration examples:
- Sequential mode for beginners
- Parallel mode for advanced users
- Conservative settings for safety
- Large-scale operations

## Best Practices

1. **Profile Management**:
   - Use different email addresses for each profile
   - Vary profile information slightly
   - Keep profiles active with regular manual use

2. **Run Modes**:
   - Start with sequential mode
   - Test thoroughly before using parallel mode
   - Monitor performance regularly

3. **Safety Guidelines**:
   - Don't exceed 30-50 applications per profile per day
   - Take breaks between sessions
   - Rotate profiles regularly
   - Use the performance monitor to track success rates

4. **Optimization**:
   - Adjust delays based on performance
   - Update blacklists regularly
   - Fine-tune search criteria per profile

## Support

For issues:
1. Check the console output for error messages
2. Review the application log in the data folder
3. Ensure all dependencies are installed
4. Verify your LinkedIn profile is complete

Remember: This tool is for educational purposes. Always respect LinkedIn's Terms of Service and use automation responsibly.