"""
Multi-Profile Performance Monitor
Tracks and analyzes the performance of multiple LinkedIn profiles
"""

import os
import json
import glob
from datetime import datetime, timedelta
from collections import defaultdict
import re


class ProfileMonitor:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.performance_file = os.path.join(data_dir, "profile_performance.json")
        self.applied_jobs_file = os.path.join(data_dir, "applied_jobs.json")
        
    def analyze_profile_logs(self):
        """Analyze log files for each profile"""
        profile_stats = defaultdict(lambda: {
            "total_applications": 0,
            "successful_applications": 0,
            "failed_applications": 0,
            "blacklisted_encounters": 0,
            "already_applied": 0,
            "dates_active": set()
        })
        
        # Find all log files
        log_pattern = os.path.join(self.data_dir, "Applied_Jobs_*.txt")
        log_files = glob.glob(log_pattern)
        
        for log_file in log_files:
            # Extract profile name and date from filename
            filename = os.path.basename(log_file)
            match = re.match(r"Applied_Jobs_(.+)_(\d{8})\.txt", filename)
            if match:
                profile_name = match.group(1)
                date = match.group(2)
                profile_stats[profile_name]["dates_active"].add(date)
                
                # Analyze log content
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if "🥳" in line or "Successfully applied" in line:
                            profile_stats[profile_name]["successful_applications"] += 1
                            profile_stats[profile_name]["total_applications"] += 1
                        elif "🥵" in line or "Cannot apply" in line:
                            profile_stats[profile_name]["failed_applications"] += 1
                            profile_stats[profile_name]["total_applications"] += 1
                        elif "🚫" in line or "Blacklisted" in line:
                            profile_stats[profile_name]["blacklisted_encounters"] += 1
                        elif "✅" in line or "Already applied" in line:
                            profile_stats[profile_name]["already_applied"] += 1
        
        return profile_stats
    
    def generate_report(self):
        """Generate a comprehensive performance report"""
        stats = self.analyze_profile_logs()
        
        print("=" * 60)
        print("LINKEDIN MULTI-PROFILE PERFORMANCE REPORT")
        print("=" * 60)
        print(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Overall statistics
        total_apps = sum(p["total_applications"] for p in stats.values())
        total_success = sum(p["successful_applications"] for p in stats.values())
        total_failed = sum(p["failed_applications"] for p in stats.values())
        
        print("OVERALL STATISTICS:")
        print(f"Total Profiles: {len(stats)}")
        print(f"Total Applications: {total_apps}")
        print(f"Successful Applications: {total_success}")
        print(f"Failed Applications: {total_failed}")
        if total_apps > 0:
            print(f"Overall Success Rate: {(total_success/total_apps)*100:.1f}%")
        print("\n" + "-" * 60 + "\n")
        
        # Per-profile statistics
        print("PROFILE-BY-PROFILE BREAKDOWN:\n")
        
        for profile_name, data in sorted(stats.items()):
            print(f"Profile: {profile_name}")
            print(f"  Active Days: {len(data['dates_active'])}")
            print(f"  Total Applications: {data['total_applications']}")
            print(f"  Successful: {data['successful_applications']}")
            print(f"  Failed: {data['failed_applications']}")
            
            if data['total_applications'] > 0:
                success_rate = (data['successful_applications'] / data['total_applications']) * 100
                print(f"  Success Rate: {success_rate:.1f}%")
            
            print(f"  Blacklisted Encounters: {data['blacklisted_encounters']}")
            print(f"  Already Applied: {data['already_applied']}")
            
            if len(data['dates_active']) > 0:
                avg_per_day = data['total_applications'] / len(data['dates_active'])
                print(f"  Average Applications/Day: {avg_per_day:.1f}")
            
            print()
        
        # Best performing profile
        if stats:
            best_profile = max(stats.items(), 
                             key=lambda x: x[1]['successful_applications'])
            print("-" * 60)
            print(f"BEST PERFORMING PROFILE: {best_profile[0]}")
            print(f"With {best_profile[1]['successful_applications']} successful applications")
        
        print("\n" + "=" * 60)
    
    def save_performance_snapshot(self):
        """Save current performance data for trend analysis"""
        stats = self.analyze_profile_logs()
        
        # Load existing performance data
        if os.path.exists(self.performance_file):
            with open(self.performance_file, 'r') as f:
                performance_history = json.load(f)
        else:
            performance_history = {}
        
        # Add current snapshot
        snapshot_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        performance_history[snapshot_date] = {
            profile: {
                "total_applications": data["total_applications"],
                "successful_applications": data["successful_applications"],
                "failed_applications": data["failed_applications"],
                "success_rate": (data["successful_applications"] / data["total_applications"] * 100) 
                               if data["total_applications"] > 0 else 0
            }
            for profile, data in stats.items()
        }
        
        # Save updated history
        with open(self.performance_file, 'w') as f:
            json.dump(performance_history, f, indent=2)
        
        print(f"Performance snapshot saved to {self.performance_file}")
    
    def show_trends(self, days=7):
        """Show performance trends over time"""
        if not os.path.exists(self.performance_file):
            print("No performance history found. Run save_performance_snapshot() first.")
            return
        
        with open(self.performance_file, 'r') as f:
            history = json.load(f)
        
        print(f"\nPERFORMANCE TRENDS (Last {days} days):\n")
        
        # Filter snapshots from last N days
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_snapshots = {
            date: data for date, data in history.items()
            if datetime.strptime(date.split('_')[0], "%Y-%m-%d") >= cutoff_date
        }
        
        if not recent_snapshots:
            print("No data available for the specified period.")
            return
        
        # Analyze trends per profile
        profiles = set()
        for snapshot in recent_snapshots.values():
            profiles.update(snapshot.keys())
        
        for profile in sorted(profiles):
            print(f"\nProfile: {profile}")
            print("Date               | Apps | Success | Rate")
            print("-" * 45)
            
            for date, data in sorted(recent_snapshots.items()):
                if profile in data:
                    p_data = data[profile]
                    date_str = date.split('_')[0]
                    print(f"{date_str:18} | {p_data['total_applications']:4d} | "
                          f"{p_data['successful_applications']:7d} | "
                          f"{p_data['success_rate']:4.1f}%")
    
    def get_recommendations(self):
        """Provide recommendations based on performance data"""
        stats = self.analyze_profile_logs()
        
        print("\nRECOMMENDATIONS:\n")
        
        for profile_name, data in stats.items():
            if data['total_applications'] == 0:
                continue
                
            success_rate = (data['successful_applications'] / data['total_applications']) * 100
            
            print(f"Profile: {profile_name}")
            
            if success_rate < 50:
                print("  ⚠️  Low success rate detected.")
                print("  - Review your application criteria")
                print("  - Check if your profile is complete")
                print("  - Consider adjusting search filters")
            elif success_rate > 80:
                print("  ✅ Excellent success rate!")
                print("  - Consider increasing daily application limit")
                print("  - You could expand your search criteria")
            
            if data['blacklisted_encounters'] > data['total_applications'] * 0.3:
                print("  ⚠️  High blacklist encounter rate.")
                print("  - Review and update your blacklist")
                print("  - Consider being more selective with search terms")
            
            if data['already_applied'] > 10:
                print("  ℹ️  Many duplicate encounters.")
                print("  - Consider expanding search locations")
                print("  - Try different keywords")
            
            print()


def main():
    """Main function to run the monitor"""
    monitor = ProfileMonitor()
    
    while True:
        print("\nMULTI-PROFILE PERFORMANCE MONITOR")
        print("1. Generate Performance Report")
        print("2. Save Performance Snapshot")
        print("3. Show Trends")
        print("4. Get Recommendations")
        print("5. Exit")
        
        choice = input("\nSelect an option (1-5): ")
        
        if choice == "1":
            monitor.generate_report()
        elif choice == "2":
            monitor.save_performance_snapshot()
        elif choice == "3":
            days = input("Enter number of days to analyze (default 7): ")
            days = int(days) if days.isdigit() else 7
            monitor.show_trends(days)
        elif choice == "4":
            monitor.get_recommendations()
        elif choice == "5":
            print("Exiting monitor...")
            break
        else:
            print("Invalid option. Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()