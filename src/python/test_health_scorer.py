import pandas as pd
import numpy as np
from data_generator import generate_dataset, generate_realistic_day
from ml_health_scorer import MLHealthScorer

# 1. Generate synthetic dataset
print("\n🚀 ML Health Scorer - Hackathon Demo\n" + "="*50)
print("Generating synthetic health dataset...")
data = generate_dataset(num_days=1500)
df = pd.DataFrame(data)

# Reference scoring (same as used for ML target)
def reference_score(day):
    # For demo, use a simple weighted sum as a reference (not used in ML)
    score = 0
    score += 0.3 * min(1, day['sleep_hours']/8)
    score += 0.2 * min(1, day['steps']/10000)
    score += 0.1 * min(1, day['hydration_liters']/2.5)
    score += 0.1 * (1 if day['stress_level']=='low' else 0.5 if day['stress_level']=='medium' else 0)
    score += 0.1 * (1 if day['mood']=='good' else 0.5 if day['mood']=='neutral' else 0)
    score += 0.1 * (1 - min(1, day['screen_time_hours']/10))
    score += 0.1 * (1 if 55<=day['heart_rate_rest']<=75 else 0.5)
    return round(score*100, 1)

# 2. Train MLHealthScorer
print("Training ML health scoring model...")
scorer = MLHealthScorer()
scores = np.array([reference_score(day) for day in data])
model_results = scorer.train(df, scores)

# 3. Print model performance
best_model = min(model_results, key=lambda k: model_results[k]['test_mae'])
print(f"\n🏆 Best model: {best_model}")
print(f"   Test MAE: {model_results[best_model]['test_mae']:.2f}")
print(f"   Test R²: {model_results[best_model]['test_r2']:.3f}")
print("\n📊 Feature Importance:")
for feat, imp in scorer.feature_importance():
    print(f"   {feat}: {imp:.3f}")

# 4. Test on realistic user profiles
print("\n🧪 Testing on sample user profiles\n" + "-"*30)
test_cases = [
    {
        'name': 'Stressed Developer',
        'data': {
            'sleep_hours': 5.5,
            'steps': 3200,
            'hydration_liters': 1.2,
            'heart_rate_rest': 82,
            'stress_level': 'high',
            'mood': 'bad',
            'screen_time_hours': 12.0,
            'is_weekend': False
        }
    },
    {
        'name': 'Balanced Person',
        'data': {
            'sleep_hours': 8.5,
            'steps': 15000,
            'hydration_liters': 3.2,
            'heart_rate_rest': 58,
            'stress_level': 'low',
            'mood': 'good',
            'screen_time_hours': 3.0,
            'is_weekend': False
        }
    },
    {
        'name': 'Average Person',
        'data': {
            'sleep_hours': 7.0,
            'steps': 6500,
            'hydration_liters': 2.0,
            'heart_rate_rest': 68,
            'stress_level': 'medium',
            'mood': 'neutral',
            'screen_time_hours': 6.0,
            'is_weekend': False
        }
    }
]
for test in test_cases:
    pred = scorer.predict(test['data'])
    ref = reference_score(test['data'])
    print(f"\n{test['name']}")
    print(f"   ML Predicted Score: {pred:.1f}/100")
    print(f"   Reference Score: {ref:.1f}/100")
    print(f"   Difference: {abs(pred-ref):.1f} points")

print("\n✅ ML Health Scorer system is ready for hackathon demo!")