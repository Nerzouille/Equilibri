import sys
import numpy as np
import pandas as pd
import argparse
from data_generator import generate_dataset
from ml_health_scorer import MLHealthScorer

def calculate_health_score(row):
    """Calculate health score from raw data (0-100 scale)"""
    # Sleep score (0-40 points)
    if 7 <= row['sleep_hours'] <= 9:
        sleep_score = 40
    elif 6 <= row['sleep_hours'] <= 10:
        sleep_score = 30
    elif row['sleep_hours'] < 5:
        sleep_score = 10
    else:
        sleep_score = 20

    # Activity score (0-30 points)
    if row['steps'] >= 10000:
        activity_score = 30
    elif row['steps'] >= 8000:
        activity_score = 25
    elif row['steps'] >= 5000:
        activity_score = 15
    else:
        activity_score = 5

    # Hydration score (0-15 points)
    if 2 <= row['hydration_liters'] <= 3:
        hydration_score = 15
    elif 1.5 <= row['hydration_liters'] <= 3.5:
        hydration_score = 10
    else:
        hydration_score = 5

    # Stress and mood score (0-15 points)
    stress_scores = {'low': 15, 'medium': 8, 'high': 3}
    mood_scores = {'good': 5, 'neutral': 3, 'bad': 1}
    stress_mood_score = stress_scores.get(row['stress_level'], 5) + mood_scores.get(row['mood'], 2)

    # Total score
    total_score = sleep_score + activity_score + hydration_score + stress_mood_score

    # Add noise for realism
    noise = np.random.normal(0, 3)
    total_score += noise

    return max(0, min(100, total_score))

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Train ML health scoring model')
    parser.add_argument('--days', '-d', type=int, default=1500,
                       help='Number of synthetic days to generate (default: 1500)')

    args = parser.parse_args()

    print(f"🚀 Training ML Health Scorer with {args.days} days of synthetic data")
    print("=" * 60)

    # Generate synthetic dataset
    print(f"Generating {args.days} days of synthetic health data...")
    data_list = generate_dataset(num_days=args.days)

    # Convert to DataFrame
    df = pd.DataFrame(data_list)
    print(f"Generated DataFrame with {len(df)} rows and {len(df.columns)} columns")

    # Calculate health scores for each day
    print("Calculating health scores...")
    scores = np.array([calculate_health_score(row) for _, row in df.iterrows()])

    print(f"Score range: {scores.min():.1f} - {scores.max():.1f}")
    print(f"Score mean: {scores.mean():.1f} ± {scores.std():.1f}")

    # Train the model
    scorer = MLHealthScorer()
    print("Training the ML health scorer...")
    model_results = scorer.train(df, scores)

    # Print best model performance
    best_model_name = min(model_results.keys(), key=lambda k: model_results[k]['test_mae'])
    best_results = model_results[best_model_name]
    print(f"\n🏆 Best model: {best_model_name}")
    print(f"   Test MAE: {best_results['test_mae']:.2f}")
    print(f"   Test R²: {best_results['test_r2']:.3f}")

    # Save the model (always to health_model.pkl)
    model_path = "health_model.pkl"
    scorer.save_model(model_path)
    print(f"Model trained and saved to {model_path}")

if __name__ == "__main__":
    main()
