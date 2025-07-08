from ml_health_scorer import MLHealthScorer
from health_advisor import HealthAdvisor
from data_generator import generate_realistic_day
from datetime import datetime, timedelta

def demo_complete_system():
    """
    Complete demo showcasing the integration of ML health scoring and LLM-powered personalized health advice.
    """

    print("🏥 EQUILIBRI - Complete Health Analysis System")
    print("=" * 60)

    # 1. Initialize components
    print("\n1. Initializing ML Health Scorer...")
    scorer = MLHealthScorer()

    try:
        scorer.load_model("../../health_model.pkl")
        print("✅ ML model loaded successfully")
    except:
        print("❌ Model not found. Please run train_health_model.py first")
        return

    print("\n2. Initializing LLM Health Advisor...")
    try:
        advisor = HealthAdvisor(model_name="llama3:8b")
        print("✅ LLM advisor initialized (llama3:8b)")
    except Exception as e:
        print(f"❌ LLM initialization failed: {e}")
        print("Make sure Ollama is running and llama3:8b is installed")
        return

    # 2. Generate sample user data for different profiles
    profiles = [
        ("Healthy Professional", "balanced"),
        ("Stressed Student", "calm"),
        ("Active Athlete", "motivated")
    ]

    for profile_name, personality in profiles:
        print(f"\n{'='*20} {profile_name} {'='*20}")

        # Generate realistic day data
        today = datetime.now()
        if "Stressed" in profile_name:
            # Simulate stressed profile
            health_data = {
                'sleep_hours': 5.2,
                'steps': 3400,
                'hydration_liters': 1.1,
                'heart_rate_rest': 82,
                'stress_level': 'high',
                'mood': 'bad',
                'screen_time_hours': 9.2,
                'is_weekend': False
            }
        elif "Athlete" in profile_name:
            # Simulate athlete profile
            health_data = {
                'sleep_hours': 8.5,
                'steps': 18000,
                'hydration_liters': 3.2,
                'heart_rate_rest': 52,
                'stress_level': 'low',
                'mood': 'good',
                'screen_time_hours': 2.5,
                'is_weekend': False
            }
        else:
            # Balanced professional
            health_data = {
                'sleep_hours': 7.2,
                'steps': 8500,
                'hydration_liters': 2.1,
                'heart_rate_rest': 66,
                'stress_level': 'medium',
                'mood': 'neutral',
                'screen_time_hours': 5.5,
                'is_weekend': False
            }

        # 3. Get ML health score
        print("\n📊 Health Metrics:")
        for key, value in health_data.items():
            if key != 'is_weekend':
                print(f"  {key.replace('_', ' ').title()}: {value}")

        health_score = scorer.predict(health_data)
        print(f"\n🎯 ML Health Score: {health_score:.1f}/100")

        # 4. Get LLM analysis and advice
        print("\n🤖 LLM Analysis:")
        try:
            analysis = advisor.analyze_health_day(health_data, health_score, personality)
            print(f"  {analysis['analysis']}")

            print(f"\n🎯 Priority Area: {analysis['priority_area'].title()} (Score: {analysis['priority_score']}/100)")

            # 5. Get morning recommendations
            print("\n🌅 Tomorrow's Morning Recommendations:")
            recommendations = advisor.get_morning_recommendations(health_data, health_score)
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")

        except Exception as e:
            print(f"❌ LLM analysis failed: {e}")
            print("Make sure Ollama is running and accessible")

        print("\n" + "-" * 60)

    print("\n✅ Demo completed! The system combines:")
    print("  • ML-based health scoring (fast, accurate)")
    print("  • LLM-powered personalized advice (natural, contextual)")
    print("  • 100% offline operation (privacy-first)")

if __name__ == "__main__":
    demo_complete_system()
