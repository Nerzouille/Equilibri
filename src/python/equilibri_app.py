"""
EQUILIBRI - Temporary Version
"""

from health_tracker import HealthTracker
from user_data_manager import UserHealthData, create_sample_user_data
import os

def setup_user():
    """Initial user configuration"""
    print("🏥 EQUILIBRI - Initial Configuration")
    print("=" * 50)

    name = input("Your first name: ")

    print("\nPersonality for advice:")
    print("1. Balanced (encouraging)")
    print("2. Motivated (energetic)")
    print("3. Calm (gentle)")
    print("4. Direct (practical)")

    personality_map = {
        "1": "balanced",
        "2": "motivated",
        "3": "calm",
        "4": "direct"
    }

    personality_choice = input("Choix (1-4): ")
    personality = personality_map.get(personality_choice, "balanced")

    # Goals
    print("\nYour health goals:")
    try:
        sleep_target = float(input("Desired sleep hours (e.g., 8): ") or "8")
        steps_target = int(input("Desired daily steps (e.g., 10000): ") or "10000")
        hydration_target = float(input("Daily water liters (e.g., 2.5): ") or "2.5")
    except ValueError:
        print("⚠️ Using default values")
        sleep_target = 8.0
        steps_target = 10000
        hydration_target = 2.5

    profile = {
        "name": name,
        "personality": personality,
        "goals": {
            "sleep_target": sleep_target,
            "steps_target": steps_target,
            "hydration_target": hydration_target
        },
        "preferences": {
            "morning_reminders": True,
            "stress_tracking": True
        }
    }

    user_data = UserHealthData("main_user")
    user_data.save_user_profile(profile)

    print(f"\n✅ Profile created for {name}!")
    return user_data

def main_menu():
    """Main application menu"""
    print("\n🏥 EQUILIBRI - Main Menu")
    print("=" * 40)
    print("1. Enter today's data")
    print("2. View today's analysis")
    print("3. History (last 7 days)")
    print("4. Quick demo")
    print("5. User configuration")
    print("0. Exit")

    return input("\nChoice: ")

def show_history(tracker):
    """Show score history"""
    print("\n📊 History of last 7 days")
    print("=" * 50)

    history = tracker.user_data.get_history(7)

    if not history:
        print("No history available")
        return

    print(f"{'Date':<12} {'Score':<8} {'Sleep':<8} {'Steps':<8} {'Stress':<10}")
    print("-" * 50)

    for day in history:
        # Calculate score for each day
        try:
            score = tracker.ml_scorer.predict(day)
            date = day.get('date', 'N/A')[:10]  # Format YYYY-MM-DD
            sleep = day.get('sleep_hours', 'N/A')
            steps = day.get('steps', 'N/A')
            stress = day.get('stress_level', 'N/A')

            print(f"{date:<12} {score:<8.1f} {sleep:<8} {steps:<8} {stress:<10}")
        except:
            print(f"Error for {day.get('date', 'N/A')}")

def main():
    """Main function"""

    # Check if ML model exists
    if not os.path.exists("../../health_model.pkl"):
        print("❌ ML model not found!")
        print("🔧 Run first: python train_health_model.py")
        return

    # Initialize tracker
    tracker = HealthTracker("main_user")

    # Check if user exists
    profile = tracker.user_data.get_user_profile()
    if profile.get('name') == 'User':  # Default profile
        print("👋 Welcome to EQUILIBRI!")
        print("Let's set up your profile first...")
        setup_user()
        tracker = HealthTracker("main_user")  # Reload

    print(f"\n👋 Hello {tracker.user_data.get_user_profile()['name']}!")

    while True:
        choice = main_menu()

        if choice == "1":
            tracker.daily_workflow()

        elif choice == "2":
            print("\n🔍 Analyse d'aujourd'hui...")
            analysis = tracker.analyze_today()
            if analysis:
                tracker.display_analysis(analysis)
            else:
                print("❌ No data for today. Please enter your data first.")

        elif choice == "3":
            show_history(tracker)

        elif choice == "4":
            tracker.quick_demo()

        elif choice == "5":
            setup_user()
            tracker = HealthTracker("main_user")  # Recharger

        elif choice == "0":
            print("👋 See you later!")
            break

        else:
            print("❌ Invalid choice")

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("🔧 Check that Ollama is running and the model is trained")
