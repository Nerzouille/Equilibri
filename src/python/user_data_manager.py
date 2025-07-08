import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class UserHealthData:
    """Simple manager for user health data"""

    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self.data_file = f"user_data_{user_id}.json"
        self.profile_file = f"user_profile_{user_id}.json"

    def save_daily_data(self, health_data: Dict) -> bool:
        """Save daily health data"""
        try:
            # Add timestamp automatically
            health_data['timestamp'] = datetime.now().isoformat()
            health_data['date'] = datetime.now().strftime("%Y-%m-%d")

            # Load existing data or create new file
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    all_data = json.load(f)
            else:
                all_data = []

            # Add new data
            all_data.append(health_data)

            # Save
            with open(self.data_file, 'w') as f:
                json.dump(all_data, f, indent=2)

            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False

    def get_latest_data(self) -> Optional[Dict]:
        """Get the most recent data"""
        try:
            if not os.path.exists(self.data_file):
                return None

            with open(self.data_file, 'r') as f:
                all_data = json.load(f)

            if not all_data:
                return None

            # Return most recent data
            return all_data[-1]
        except Exception as e:
            print(f"Read error: {e}")
            return None

    def get_history(self, days: int = 7) -> List[Dict]:
        """Get history of the last N days"""
        try:
            if not os.path.exists(self.data_file):
                return []

            with open(self.data_file, 'r') as f:
                all_data = json.load(f)

            # Return the last N days
            return all_data[-days:] if len(all_data) > days else all_data
        except Exception as e:
            print(f"History read error: {e}")
            return []

    def save_user_profile(self, profile: Dict) -> bool:
        """Save user profile"""
        try:
            profile['updated_at'] = datetime.now().isoformat()

            with open(self.profile_file, 'w') as f:
                json.dump(profile, f, indent=2)

            return True
        except Exception as e:
            print(f"Profile save error: {e}")
            return False

    def get_user_profile(self) -> Dict:
        """Get user profile"""
        try:
            if os.path.exists(self.profile_file):
                with open(self.profile_file, 'r') as f:
                    return json.load(f)
            else:
                # Default profile
                return {
                    "name": "User",
                    "personality": "balanced",
                    "goals": {
                        "sleep_target": 8.0,
                        "steps_target": 10000,
                        "hydration_target": 2.5
                    },
                    "created_at": datetime.now().isoformat()
                }
        except Exception as e:
            print(f"Profile read error: {e}")
            return {"name": "User", "personality": "balanced"}

def create_sample_user_data():
    """Create sample data for testing"""
    user_data = UserHealthData("demo_user")

    # User profile
    profile = {
        "name": "Alice Dupont",
        "age": 28,
        "personality": "motivated",
        "goals": {
            "sleep_target": 8.0,
            "steps_target": 10000,
            "hydration_target": 2.5
        },
        "preferences": {
            "morning_reminders": True,
            "stress_tracking": True,
            "posture_alerts": True
        }
    }

    user_data.save_user_profile(profile)

    # Health data for recent days
    sample_days = [
        {
            "sleep_hours": 7.5,
            "steps": 9200,
            "hydration_liters": 2.3,
            "heart_rate_rest": 62,
            "stress_level": "low",
            "mood": "good",
            "screen_time_hours": 4.2,
            "is_weekend": False,
            "notes": "Bonne journée, meeting important réussi"
        },
        {
            "sleep_hours": 6.8,
            "steps": 7500,
            "hydration_liters": 1.8,
            "heart_rate_rest": 68,
            "stress_level": "medium",
            "mood": "neutral",
            "screen_time_hours": 6.5,
            "is_weekend": False,
            "notes": "Journée chargée, oublié de boire assez d'eau"
        },
        {
            "sleep_hours": 8.2,
            "steps": 12000,
            "hydration_liters": 2.7,
            "heart_rate_rest": 58,
            "stress_level": "low",
            "mood": "good",
            "screen_time_hours": 3.1,
            "is_weekend": True,
            "notes": "Super weekend, randonnée avec des amis"
        }
    ]

    for day_data in sample_days:
        user_data.save_daily_data(day_data)

    return user_data

if __name__ == "__main__":
    # Create sample data
    user_data = create_sample_user_data()

    print("📊 User data created successfully!")
    print(f"Profile: {user_data.get_user_profile()['name']}")
    print(f"Latest data: {user_data.get_latest_data()}")
    print(f"History: {len(user_data.get_history())} days")
