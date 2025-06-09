"""
Profile Manager - Utility for managing multiple IxBrowser profiles
"""

import json
import os
from datetime import datetime
from ixbrowser_local_api import IXBrowserClient


class ProfileManager:
    def __init__(self):
        self.client = IXBrowserClient()
        self.config_file = "config.py"
        self.profile_data_file = "data/profile_metadata.json"
        self.load_profile_data()
    
    def load_profile_data(self):
        """Load profile metadata"""
        if os.path.exists(self.profile_data_file):
            with open(self.profile_data_file, 'r') as f:
                self.profile_data = json.load(f)
        else:
            self.profile_data = {}
    
    def save_profile_data(self):
        """Save profile metadata"""
        os.makedirs(os.path.dirname(self.profile_data_file), exist_ok=True)
        with open(self.profile_data_file, 'w') as f:
            json.dump(self.profile_data, f, indent=2)
    
    def test_profile(self, profile_id):
        """Test if a profile can be opened"""
        print(f"Testing profile {profile_id}...")
        try:
            response = self.client.open_profile(profile_id, cookies_backup=False)
            if 'debugging_port' in response:
                print(f"✅ Profile {profile_id} is working!")
                self.client.close_profile(profile_id)
                return True
            else:
                print(f"❌ Profile {profile_id} failed to open properly")
                return False
        except Exception as e:
            print(f"❌ Error testing profile {profile_id}: {e}")
            return False
    
    def test_all_profiles(self):
        """Test all configured profiles"""
        print("\nTesting all configured profiles...\n")
        
        # Read profiles from config
        profiles = self.read_profiles_from_config()
        
        if not profiles:
            print("No profiles found in config.py")
            return
        
        results = []
        for profile in profiles:
            profile_id = profile['id']
            profile_name = profile.get('name', f'Profile_{profile_id}')
            
            print(f"Testing {profile_name} (ID: {profile_id})")
            success = self.test_profile(profile_id)
            results.append({
                'id': profile_id,
                'name': profile_name,
                'status': 'working' if success else 'failed',
                'last_tested': datetime.now().isoformat()
            })
            print()
        
        # Update profile data
        for result in results:
            self.profile_data[str(result['id'])] = result
        
        self.save_profile_data()
        
        # Summary
        working = sum(1 for r in results if r['status'] == 'working')
        print(f"\nSummary: {working}/{len(results)} profiles are working")
    
    def read_profiles_from_config(self):
        """Read profile configuration from config.py"""
        try:
            config_vars = {}
            with open(self.config_file, 'r') as f:
                exec(f.read(), config_vars)
            
            return config_vars.get('ixbrowser_profiles', [])
        except Exception as e:
            print(f"Error reading config.py: {e}")
            return []
    
    def add_profile(self):
        """Interactive profile addition"""
        print("\nAdd New Profile")
        print("-" * 40)
        
        profile_id = input("Enter profile ID: ")
        if not profile_id.isdigit():
            print("Profile ID must be a number")
            return
        
        profile_name = input("Enter profile name (optional): ")
        if not profile_name:
            profile_name = f"Profile_{profile_id}"
        
        # Test the profile
        print(f"\nTesting profile {profile_id}...")
        if not self.test_profile(int(profile_id)):
            confirm = input("Profile test failed. Add anyway? (y/n): ")
            if confirm.lower() != 'y':
                return
        
        # Update config file
        self.update_config_file(int(profile_id), profile_name)
        
        print(f"\n✅ Profile {profile_name} added successfully!")
    
    def update_config_file(self, profile_id, profile_name):
        """Update config.py with new profile"""
        # This is a simplified version - in production, you'd want more robust config editing
        print("\nPlease manually add this to your config.py:")
        print(f'    {{"id": {profile_id}, "name": "{profile_name}"}},')
        print("\nAdd it to the ixbrowser_profiles list.")
    
    def view_profile_stats(self):
        """View statistics for all profiles"""
        print("\nProfile Statistics")
        print("-" * 60)
        
        if not self.profile_data:
            print("No profile data available. Run 'Test All Profiles' first.")
            return
        
        print(f"{'ID':<10} {'Name':<20} {'Status':<10} {'Last Tested':<20}")
        print("-" * 60)
        
        for profile_id, data in sorted(self.profile_data.items()):
            last_tested = data.get('last_tested', 'Never')
            if last_tested != 'Never':
                last_tested = last_tested.split('T')[0]  # Just the date
            
            status = data.get('status', 'Unknown')
            status_icon = "✅" if status == 'working' else "❌"
            
            print(f"{profile_id:<10} {data.get('name', 'Unknown'):<20} "
                  f"{status_icon} {status:<8} {last_tested:<20}")
    
    def cleanup_logs(self):
        """Clean up old log files"""
        print("\nCleanup Old Logs")
        print("-" * 40)
        
        days = input("Delete logs older than how many days? (default: 30): ")
        days = int(days) if days.isdigit() else 30
        
        import glob
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        log_pattern = "data/Applied_Jobs_*.txt"
        for log_file in glob.glob(log_pattern):
            # Extract date from filename
            try:
                filename = os.path.basename(log_file)
                date_str = filename.split('_')[-1].replace('.txt', '')
                file_date = datetime.strptime(date_str, "%Y%m%d")
                
                if file_date < cutoff_date:
                    os.remove(log_file)
                    deleted_count += 1
                    print(f"Deleted: {filename}")
            except:
                continue
        
        print(f"\n✅ Deleted {deleted_count} old log files")
    
    def reset_applied_jobs(self):
        """Reset the applied jobs list"""
        print("\n⚠️  WARNING: This will reset the applied jobs list!")
        print("The bot will not know which jobs have been applied to previously.")
        
        confirm = input("\nAre you sure? Type 'RESET' to confirm: ")
        if confirm == 'RESET':
            applied_file = 'data/applied_jobs.json'
            if os.path.exists(applied_file):
                # Backup the old file
                backup_file = f'data/applied_jobs_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                os.rename(applied_file, backup_file)
                print(f"✅ Backed up old file to: {backup_file}")
            
            # Create empty file
            with open(applied_file, 'w') as f:
                json.dump([], f)
            
            print("✅ Applied jobs list has been reset")
        else:
            print("Reset cancelled")


def main():
    """Main menu for profile manager"""
    manager = ProfileManager()
    
    while True:
        print("\n" + "=" * 50)
        print("LINKEDIN PROFILE MANAGER")
        print("=" * 50)
        print("1. Test All Profiles")
        print("2. Add New Profile")
        print("3. View Profile Statistics")
        print("4. Cleanup Old Logs")
        print("5. Reset Applied Jobs List")
        print("6. Exit")
        
        choice = input("\nSelect an option (1-6): ")
        
        if choice == "1":
            manager.test_all_profiles()
        elif choice == "2":
            manager.add_profile()
        elif choice == "3":
            manager.view_profile_stats()
        elif choice == "4":
            manager.cleanup_logs()
        elif choice == "5":
            manager.reset_applied_jobs()
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid option. Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()