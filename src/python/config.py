"""Configuration for Equilibri Health Scoring System"""

FEATURE_NAMES = [
    'sleep_hours',
    'steps',
    'hydration_liters',
    'heart_rate_rest',
    'stress_level',
    'mood',
    'screen_time_hours',
    'is_weekend',
]

CATEGORICAL_FEATURES = ['stress_level', 'mood']

FEATURE_RANGES = {
    'sleep_hours': (0, 12),
    'steps': (0, 50000),
    'hydration_liters': (0, 10),
    'heart_rate_rest': (30, 150),
    'screen_time_hours': (0, 24),
}

CATEGORICAL_VALUES = {
    'stress_level': ['low', 'medium', 'high'],
    'mood': ['good', 'neutral', 'bad']
}
