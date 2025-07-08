from user_data_manager import UserHealthData
from ml_health_scorer import MLHealthScorer
from health_advisor import HealthAdvisor
from typing import Dict
import json
from datetime import datetime

class HealthTracker:
    """Simple interface for tracking and analyzing daily health"""

    def __init__(self, user_id: str = "main_user"):
        self.user_data = UserHealthData(user_id)
        self.ml_scorer = MLHealthScorer()
        self.health_advisor = HealthAdvisor()

        # Load ML model
        try:
            self.ml_scorer.load_model("../../health_model.pkl")
            print("✅ ML model loaded")
        except:
            print("❌ ML model not found. Run train_health_model.py first")

    def input_daily_data(self) -> Dict:
        """Simple interface for entering daily data"""
        print("\n🏥 EQUILIBRI - Daily Health Data Entry")
        print("=" * 50)

        data = {}

        try:
            # Basic data
            data['sleep_hours'] = float(input("💤 Sleep hours (e.g., 7.5): "))
            data['steps'] = int(input("🚶 Number of steps (e.g., 8500): "))
            data['hydration_liters'] = float(input("💧 Water consumed in liters (e.g., 2.1): "))
            data['heart_rate_rest'] = int(input("❤️ Resting heart rate (e.g., 65): "))

            # Subjective data
            print("\n📊 Subjective assessments:")
            stress_options = ["low", "medium", "high"]
            print("Stress level: 1=low, 2=medium, 3=high")
            stress_choice = int(input("Choice (1-3): "))
            data['stress_level'] = stress_options[stress_choice - 1]

            mood_options = ["good", "neutral", "bad"]
            print("Mood: 1=good, 2=neutral, 3=bad")
            mood_choice = int(input("Choice (1-3): "))
            data['mood'] = mood_options[mood_choice - 1]

            data['screen_time_hours'] = float(input("📱 Screen time in hours (e.g., 5.5): "))

            # Weekend?
            is_weekend = input("🗓️ Weekend? (y/n): ").lower().startswith('y')
            data['is_weekend'] = is_weekend

            # Optional notes
            notes = input("📝 Notes (optional): ")
            if notes.strip():
                data['notes'] = notes

            return data

        except (ValueError, IndexError) as e:
            print(f"❌ Input error: {e}")
            return None

    def quick_input_data(self, sleep: float, steps: int, hydration: float,
                        stress: str = "medium", mood: str = "neutral") -> Dict:
        """Quick data entry for testing"""
        return {
            'sleep_hours': sleep,
            'steps': steps,
            'hydration_liters': hydration,
            'heart_rate_rest': 65,  # Default value
            'stress_level': stress,
            'mood': mood,
            'screen_time_hours': 5.0,  # Default value
            'is_weekend': False
        }

    def analyze_today(self, health_data: Dict = None) -> Dict:
        """Analyze today's data"""

        if health_data is None:
            health_data = self.user_data.get_latest_data()

        if health_data is None:
            print("❌ No data available")
            return None

        # Calculate ML score
        ml_score = self.ml_scorer.predict(health_data)

        # Get user profile
        profile = self.user_data.get_user_profile()
        personality = profile.get('personality', 'balanced')

        # LLM analysis
        llm_analysis = self.health_advisor.analyze_health_day(
            health_data, ml_score, personality
        )

        # Morning recommendations
        morning_recs = self.health_advisor.get_morning_recommendations(
            health_data, ml_score
        )

        return {
            'health_data': health_data,
            'ml_score': ml_score,
            'llm_analysis': llm_analysis,
            'morning_recommendations': morning_recs,
            'user_profile': profile
        }

    def daily_workflow(self):
        """Complete daily workflow"""
        print("\n🌅 EQUILIBRI - Daily Analysis")
        print("=" * 50)

        # 1. Data entry
        print("\n1️⃣ Health data entry")
        health_data = self.input_daily_data()

        if health_data is None:
            return

        # 2. Save
        print("\n2️⃣ Saving data...")
        if self.user_data.save_daily_data(health_data):
            print("✅ Data saved")
        else:
            print("❌ Save error")
            return

        # 3. Analysis
        print("\n3️⃣ Analyzing your day...")
        try:
            analysis = self.analyze_today(health_data)

            if analysis:
                self.display_analysis(analysis)
            else:
                print("❌ Analysis error")

        except Exception as e:
            print(f"❌ Analysis error: {e}")

    def display_analysis(self, analysis: Dict):
        """Display analysis clearly"""
        print(f"\n🎯 Health Score: {analysis['ml_score']:.1f}/100")

        print(f"\n🤖 Personalized Analysis:")
        print(f"   {analysis['llm_analysis']['analysis']}")

        print(f"\n📊 Priority Area: {analysis['llm_analysis']['priority_area'].title()}")
        print(f"   Score: {analysis['llm_analysis']['priority_score']}/100")

        print(f"\n🌅 Recommendations for tomorrow:")
        for i, rec in enumerate(analysis['morning_recommendations'], 1):
            print(f"   {i}. {rec}")

    def quick_demo(self):
        """Quick demo with sample data"""
        print("\n⚡ EQUILIBRI - Quick Demo")
        print("=" * 50)

        # Sample data
        demo_data = self.quick_input_data(
            sleep=7.2,
            steps=8500,
            hydration=2.1,
            stress="medium",
            mood="neutral"
        )

        print("📊 Sample data:")
        for key, value in demo_data.items():
            if key != 'is_weekend':
                print(f"   {key.replace('_', ' ').title()}: {value}")

        # Analysis
        analysis = self.analyze_today(demo_data)
        if analysis:
            self.display_analysis(analysis)

if __name__ == "__main__":
    tracker = HealthTracker()

    print("🏥 EQUILIBRI Health Tracker")
    print("1. Complete entry (1)")
    print("2. Quick demo (2)")

    choice = input("\nChoice: ")

    if choice == "1":
        tracker.daily_workflow()
    elif choice == "2":
        tracker.quick_demo()
    else:
        print("Quick demo by default...")
        tracker.quick_demo()
