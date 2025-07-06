import random
import json
from datetime import datetime, timedelta

def is_weekend(date):
    """Check if it's the weekend"""
    return date.weekday() >= 5

def generate_realistic_day(date, previous_day=None):
    """Generate realistic data for a day with simple correlations"""
    is_weekend_day = is_weekend(date)

    # Sleep - longer on weekends, influences other metrics
    if is_weekend_day:
        sleep_hours = round(random.uniform(7.0, 9.5), 1)
    else:
        sleep_hours = round(random.uniform(6.0, 8.5), 1)

    sleep_bonus = (sleep_hours - 7) * 500  # Well slept = more active
    if is_weekend_day:
        base_steps = random.randint(4000, 8000)  # Less activity on weekends
    else:
        base_steps = random.randint(6000, 12000)  # More activity during the week
    steps = max(2000, int(base_steps + sleep_bonus))

    # Hydration - correlated to activity
    activity_factor = steps / 8000  # Base of 8000 steps
    hydration = round(max(1.0, 1.5 * activity_factor * random.uniform(0.8, 1.3)), 1)

    # Heart rate - influenced by sleep
    if sleep_hours < 6:
        heart_rate = random.randint(65, 80)  # Higher if not well slept
    else:
        heart_rate = random.randint(55, 70)

    # Screen time - higher on weekends and if less active
    base_screen = 5.0 if is_weekend_day else 4.0
    if steps < 5000:
        base_screen += random.uniform(1.0, 2.0)  # More screen time if less active
    screen_time = round(max(2.0, base_screen + random.uniform(-1.0, 1.5)), 1)

    # Stress - based on sleep, activity and day
    stress_score = 0.5
    if sleep_hours < 6:
        stress_score += 0.3
    if steps < 4000:
        stress_score += 0.2
    if screen_time > 6:
        stress_score += 0.2
    if is_weekend_day:
        stress_score -= 0.2

    if stress_score < 0.3:
        stress_level = "low"
    elif stress_score < 0.7:
        stress_level = "medium"
    else:
        stress_level = "high"

    # Mood - influenced by stress, sleep and previous day
    mood_score = 0.5
    if sleep_hours >= 7:
        mood_score += 0.2
    if stress_level == "low":
        mood_score += 0.2
    elif stress_level == "high":
        mood_score -= 0.3

    # Influence of the previous day (continuity)
    if previous_day:
        if previous_day["mood"] == "good":
            mood_score += 0.1
        elif previous_day["mood"] == "bad":
            mood_score -= 0.1

    mood_score += random.uniform(-0.2, 0.2)

    if mood_score < 0.4:
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

if __name__ == "__main__":
    """Generate data for a week"""
    data = generate_week_data()

    output_file = "src/python/health_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Data generated for 7 days and saved in {output_file}")

    print("\nSummary of the week:")
    for day in data:
        print(f"{day['day_of_week']} ({day['date']}): "
              f"Sleep {day['sleep_hours']}h, "
              f"{day['steps']} steps, "
              f"Stress {day['stress_level']}, "
              f"Mood {day['mood']}")
