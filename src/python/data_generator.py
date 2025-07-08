import random
import json
from datetime import datetime, timedelta

def is_weekend(date):
    """Check if it's the weekend"""
    return date.weekday() >= 5

def generate_extreme_profile():
    """Generate a profile type for data diversity"""
    profiles = [
        "athlete", "stressed", "sedentary", "insomniac",
        "overworker", "healthy", "unhealthy", "normal"
    ]

    if random.random() < 0.7:
        return "normal"
    else:
        return random.choice(profiles)

def generate_realistic_day(date, previous_day=None):
    """Generate realistic data for a day"""
    is_weekend_day = is_weekend(date)
    profile = generate_extreme_profile()

    # Sleep
    if profile == "insomniac":
        sleep_hours = round(random.uniform(3.0, 5.5), 1)
    elif profile == "overworker":
        sleep_hours = round(random.uniform(4.0, 6.5), 1)
    elif profile == "athlete":
        sleep_hours = round(random.uniform(7.5, 9.5), 1)
    elif profile == "healthy":
        sleep_hours = round(random.uniform(7.0, 8.5), 1)
    elif is_weekend_day:
        sleep_hours = round(random.uniform(7.0, 10.0), 1)
    else:
        sleep_hours = round(random.uniform(5.5, 9.0), 1)

    # Steps
    sleep_bonus = (sleep_hours - 7) * 300

    if profile == "athlete":
        base_steps = random.randint(15000, 25000)
    elif profile == "sedentary":
        base_steps = random.randint(1000, 4000)
    elif profile == "stressed":
        base_steps = random.randint(2000, 6000)
    elif profile == "healthy":
        base_steps = random.randint(8000, 12000)
    elif is_weekend_day:
        base_steps = random.randint(3000, 10000)
    else:
        base_steps = random.randint(4000, 14000)

    steps = max(500, int(base_steps + sleep_bonus))

    # Hydration
    if profile == "athlete":
        base_hydration = random.uniform(3.0, 5.0)
    elif profile == "stressed":
        base_hydration = random.uniform(0.8, 1.8)
    elif profile == "sedentary":
        base_hydration = random.uniform(1.2, 2.2)
    else:
        base_hydration = random.uniform(1.5, 3.5)

    activity_boost = max(0, (steps - 5000) / 15000)
    weekend_factor = 1.3 if is_weekend_day else 1.0
    stress_penalty = random.uniform(0.7, 1.1)
    weather_factor = random.uniform(0.8, 1.6)

    hydration = round(max(0.5, base_hydration * activity_boost * weekend_factor * stress_penalty * weather_factor), 1)

    # Heart rate
    if profile == "athlete":
        base_heart_rate = random.randint(45, 60)
    elif profile == "stressed":
        base_heart_rate = random.randint(75, 90)
    elif profile == "unhealthy":
        base_heart_rate = random.randint(70, 85)
    else:
        base_heart_rate = random.randint(55, 80)

    if sleep_hours < 4:
        sleep_penalty = random.randint(20, 35)
    elif sleep_hours < 6:
        sleep_penalty = random.randint(10, 20)
    elif sleep_hours > 10:
        sleep_penalty = random.randint(5, 15)
    else:
        sleep_penalty = random.randint(-8, 8)

    fitness_factor = max(-15, min(15, (steps - 8000) // 800))
    stress_impact = int((sleep_hours < 6) * 20 + (steps < 3000) * 15)

    heart_rate = max(40, min(110, base_heart_rate + sleep_penalty - fitness_factor + stress_impact))

    # Screen time
    if profile == "overworker":
        base_screen = random.uniform(10.0, 16.0)
    elif profile == "sedentary":
        base_screen = random.uniform(8.0, 14.0)
    elif profile == "athlete":
        base_screen = random.uniform(2.0, 5.0)
    elif profile == "healthy":
        base_screen = random.uniform(3.0, 6.0)
    elif is_weekend_day:
        base_screen = random.uniform(4.0, 12.0)
    else:
        base_screen = random.uniform(3.0, 10.0)

    screen_time = round(max(1.0, base_screen + random.uniform(-1.5, 2.0)), 1)

    # Stress
    if profile == "stressed":
        stress_score = random.uniform(0.8, 1.2)  # Chronic stress
    elif profile == "overworker":
        stress_score = random.uniform(0.7, 1.1)  # Hard worker
    elif profile == "athlete":
        stress_score = random.uniform(0.2, 0.6)  # sporty (less stress)
    elif profile == "healthy":
        stress_score = random.uniform(0.3, 0.7)  # balanced
    else:
        stress_score = 0.4  # Base normale

    # impacts
    if sleep_hours < 5:
        stress_score += random.uniform(0.4, 0.8)
    if steps < 3000:
        stress_score += random.uniform(0.3, 0.6)
    if screen_time > 10:
        stress_score += random.uniform(0.4, 0.7)

    # Weekend effect (less stress)
    if is_weekend_day:
        weekend_relief = random.uniform(0.2, 0.6)
        stress_score -= weekend_relief

    # Final variability
    stress_score += random.uniform(-0.3, 0.4)

    if stress_score < 0.3:
        stress_level = "low"
    elif stress_score < 0.75:
        stress_level = "medium"
    else:
        stress_level = "high"

    # Mood
    if profile == "stressed":
        mood_score = random.uniform(0.2, 0.5)  # Stessed = bad mood
    elif profile == "athlete":
        mood_score = random.uniform(0.6, 0.9)  # Sporty = good mood
    elif profile == "healthy":
        mood_score = random.uniform(0.5, 0.8)  # Balanced
    else:
        mood_score = 0.5

    if sleep_hours >= 7:
        mood_score += random.uniform(0.1, 0.3)
    if stress_level == "low":
        mood_score += random.uniform(0.1, 0.3)
    elif stress_level == "high":
        mood_score -= random.uniform(0.3, 0.5)

    # Weekend boost
    if is_weekend_day:
        weekend_mood_boost = random.uniform(0.1, 0.4)
        mood_score += weekend_mood_boost

    # Continuity with previous day
    if previous_day:
        if previous_day["mood"] == "good":
            mood_score += random.uniform(0.05, 0.2)
        elif previous_day["mood"] == "bad":
            mood_score -= random.uniform(0.05, 0.2)

    mood_score += random.uniform(-0.3, 0.3)

    if mood_score < 0.35:
        mood = "bad"
    elif mood_score < 0.7:
        mood = "neutral"
    else:
        mood = "good"

    return {
        "date": date.strftime("%Y-%m-%d"),
        "day_of_week": date.strftime("%A"),
        "sleep_hours": sleep_hours,
        "steps": steps,
        "hydration_liters": hydration,
        "heart_rate_rest": heart_rate,
        "screen_time_hours": screen_time,
        "stress_level": stress_level,
        "mood": mood,
        "is_weekend": is_weekend_day
    }

def generate_week_data():
    """Generate 7 days of realistic data"""
    start_date = datetime.now() - timedelta(days=6)
    week_data = []
    previous_day = None

    for i in range(7):
        current_date = start_date + timedelta(days=i)
        day_data = generate_realistic_day(current_date, previous_day)
        week_data.append(day_data)
        previous_day = day_data

    return week_data

def generate_dataset(num_days=1500):
    """Generate a list of daily health dicts for num_days, with continuity between days."""
    start_date = datetime.now() - timedelta(days=num_days-1)
    data = []
    previous_day = None
    for i in range(num_days):
        current_date = start_date + timedelta(days=i)
        day_data = generate_realistic_day(current_date, previous_day)
        data.append(day_data)
        previous_day = day_data
    return data

if __name__ == "__main__":
    """Generate sample data for a week for testing and save to file"""
    data = generate_week_data()
    output_file = "src/python/health_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Sample health data generated for 7 days and saved in {output_file}")
    print("\nSummary:")
    for day in data:
        print(f"{day['day_of_week']} ({day['date']}): "
              f"Sleep {day['sleep_hours']}h, "
              f"{day['steps']} steps, "
              f"Stress {day['stress_level']}, "
              f"Mood {day['mood']}")
