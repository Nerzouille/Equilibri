import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
from config import FEATURE_NAMES, CATEGORICAL_FEATURES
import joblib

class MLHealthScorer:
    """ML health scoring system using regression models."""
    def __init__(self):
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boost': GradientBoostingRegressor(n_estimators=100, random_state=42)
        }
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.best_model = None
        self.is_trained = False
        self.feature_names = FEATURE_NAMES
        self.categorical_cols = CATEGORICAL_FEATURES

    def preprocess_features(self, df: pd.DataFrame, fit_encoders: bool = True) -> np.ndarray:
        """Preprocess features: encode categoricals, scale numerics."""
        df_processed = df.copy()
        for col in self.categorical_cols:
            if fit_encoders:
                self.label_encoders[col] = LabelEncoder()
                df_processed[col] = self.label_encoders[col].fit_transform(df_processed[col])
            else:
                df_processed[col] = self.label_encoders[col].transform(df_processed[col])
        X = df_processed[self.feature_names].values
        if fit_encoders:
            X = self.scaler.fit_transform(X)
        else:
            X = self.scaler.transform(X)
        return X

    def train(self, df: pd.DataFrame, scores: np.ndarray) -> Dict:
        """Train ML models and select best one based on test MAE."""
        X = self.preprocess_features(df, fit_encoders=True)
        y = scores
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        model_scores = {}
        for name, model in self.models.items():
            model.fit(X_train, y_train)
            y_pred_train = model.predict(X_train)
            y_pred_test = model.predict(X_test)
            train_mae = mean_absolute_error(y_train, y_pred_train)
            test_mae = mean_absolute_error(y_test, y_pred_test)
            train_r2 = r2_score(y_train, y_pred_train)
            test_r2 = r2_score(y_test, y_pred_test)
            cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='neg_mean_absolute_error')
            cv_mae = -cv_scores.mean()
            model_scores[name] = {
                'test_mae': test_mae,
                'test_r2': test_r2,
                'cv_mae': cv_mae,
                'model': model
            }
        best_name = min(model_scores.keys(), key=lambda k: model_scores[k]['test_mae'])
        self.best_model = model_scores[best_name]['model']
        self.is_trained = True
        return model_scores

    def predict(self, health_data: Dict) -> float:
        """Predict health score for a single day."""
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call train() first.")
        data_copy = health_data.copy()
        if 'is_weekend' not in data_copy:
            data_copy['is_weekend'] = False
        df = pd.DataFrame([data_copy])
        X = self.preprocess_features(df, fit_encoders=False)
        predicted_score = self.best_model.predict(X)[0]
        return float(np.clip(predicted_score, 0, 100))

    def feature_importance(self) -> Optional[List[Tuple[str, float]]]:
        """Return feature importances if available."""
        if self.best_model is not None and hasattr(self.best_model, 'feature_importances_'):
            return list(zip(self.feature_names, self.best_model.feature_importances_))
        return None

    def save_model(self, filepath):
        """Save model to file."""
        joblib.dump({
            'model': self.best_model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders
        }, filepath)

    def load_model(self, filepath):
        """Load model from file."""
        data = joblib.load(filepath)
        self.best_model = data['model']
        self.scaler = data['scaler']
        self.label_encoders = data['label_encoders']
        self.is_trained = True
