import sys
import json
from ml_health_scorer import MLHealthScorer

if __name__ == "__main__":
    model_path = "health_model.pkl"
    scorer = MLHealthScorer()
    scorer.load_model(model_path)

    example_data = {
        "sleep_hours": 7.2,
        "steps": 8500,
        "hydration_liters": 2.1,
        "heart_rate_rest": 66,
        "stress_level": "medium",
        "mood": "neutral",
        "screen_time_hours": 5.5,
        "is_weekend": False
    }

    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as f:
            user_data = json.load(f)
    else:
        user_data = example_data

    score = scorer.predict(user_data)
    print(f"Predicted health score: {score}")
