# Specification Document – "HealthMate" Application

## 1. Project Objective

Design and develop a fully offline, Edge AI-powered desktop application aimed at improving users' daily lifestyle and wellness. The app will act as a personalized health assistant that analyzes behavioral and environmental data to provide tailored recommendations and reminders — all processed locally on-device.

---

## 2. Functional Requirements

| Ref | Feature                  | Description                                                                                                       |
| --- | ------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| F1  | Health Score Calculation | Daily score based on sleep, hydration, physical activity, posture, and weather data.                              |
| F2  | Morning Recommendations  | Three personalized and actionable suggestions provided each morning.                                              |
| F3  | Contextual Reminders     | Smart prompts throughout the day (hydration, posture, breaks) based on context (schedule, weather, user profile). |
| F4  | Posture Detection        | Local webcam-based posture analysis via computer vision.                                                          |
| F5  | Historical Tracking      | Weekly/monthly trends in health score and habits.                                                                 |
| F6  | Sleep Insights           | Silent nightly analysis with recommendations for improved rest.                                                   |
| F7  | Fully Offline Mode       | Core features must operate with no internet access.                                                               |
| F8  | Optional Health API Sync | Optional integration with services like Google Fit, Apple Health, Fitbit.                                         |
| F9  | Optional Weather Data    | External weather API integration for adaptive suggestions (cached locally).                                       |
| F10 | Lightweight UI           | Minimalist interface focused on usability and accessibility.                                                      |

---

## 3. Target Audience

* **Primary users:** General public (students, professionals, anyone seeking healthier habits)
* **Usage scenario:** Daily personal use on laptop
* **User goals:** Get simple, actionable wellness support without data sharing or complex setup

---

## 4. Technical Constraints

| Category               | Requirement                                                              |
| ---------------------- | ------------------------------------------------------------------------ |
| Target platform        | Snapdragon X Elite PCs (compatible with Windows/macOS/Linux)             |
| Offline-first          | Full functionality without any internet connection                       |
| Privacy                | All data processed and stored locally                                    |
| Lightweight processing | Must work efficiently in a resource-constrained local environment        |
| UX requirements        | Clean, functional UI with subtle interactions                            |
| Multimodal AI          | Combine tabular/log data (sleep/activity) with computer vision (posture) |

---

## 5. Technical Architecture

| Component           | Technologies                                                                            |
| ------------------- | --------------------------------------------------------------------------------------- |
| UI Framework        | Tauri + Svelte (or Electron / Flutter Desktop) or whatever we want                      |
| Backend             | Python (FastAPI or local scripts), or Rust                                              |
| Local storage       | SQLite or JSON-based storage                                                            |
| Notification system | Native OS notifications (Windows/macOS/Linux)                                           |
| Embedded AI         | ONNX Runtime or PyTorch + scikit-learn (lightweight models)                             |
| Computer Vision     | OpenCV + MediaPipe (or YOLOv8-light for posture detection)                              |
| Optional APIs       | WeatherAPI / OpenWeatherMap for weather; Fitbit/Google Fit/Apple Health for health data |
| Data orchestration  | Local cache system or lightweight scheduler for data sync and scoring                   |

---

## 6. User Flow

**Morning:**

* App starts
* Health Score is computed and shown
* Personalized recommendations are displayed

**During the Day:**

* Smart reminders for hydration, posture, breaks based on user behavior and weather
* Local CV and data processing running in background

**Evening:**

* Sleep guidance (screen dimming, breathing prompts)
* Day recap and next-day planning

---

## 7. Core Modules

| Module                | Description                                                             |
| --------------------- | ----------------------------------------------------------------------- |
| Health Scoring Engine | Local engine combining rule-based logic + statistical model             |
| Recommendation System | Personalized, contextual tips derived from user inputs and live signals |
| Posture Analysis      | Real-time, privacy-safe computer vision using webcam data               |
| Local Sync/API        | (Optional) Local caching of data from weather and health APIs           |
| Tracking Dashboard    | Local stats visualization and simple trend breakdowns                   |

---

## 8. Team Setup I guess (5 members, 3 devs)
| Role               | Responsibilities                                       |
| ------------------ | ------------------------------------------------------ |
| Dev 1 – Frontend   | UI implementation, user interaction, notifications     |
| Dev 2 – Backend/AI | Score computation, logic, recommendations              |
| Dev 3 – CV/Edge AI | Posture detection with webcam, local model integration |
| UX/Design          | UX flow, user scenarios, UI design                     |
| Pitch & Docs       | GitHub setup, presentation, demo video, pitch to jury  |

---

## 9. Current Implementation - ML Health Scoring System

### Overview
The current implementation focuses on the core ML health scoring engine that analyzes daily health metrics and provides personalized health scores using machine learning.

### Architecture
```
src/python/
├── ml_health_scorer.py      # Main ML scoring engine
├── data_generator.py        # Realistic health data generator
├── train_health_model.py    # Model training script
├── predict_health_score.py  # Prediction interface
├── test_health_scorer.py    # Testing and validation
└── config.py               # Configuration and constants
```

### 🚀 How to Use
```bash
# 1. Train the model
python src/python/train_health_model.py

# 2. Test the system
python src/python/test_health_scorer.py

# 3. Predict health score
python src/python/predict_health_score.py
```

### Installation & Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Core dependencies:
# - scikit-learn (ML models)
# - pandas, numpy (data processing)
# - joblib (model serialization)
```

### Quick Demo
```bash
# 1. Train a model (generates synthetic data automatically)
python src/python/train_health_model.py

# 2. Test with different user profiles
python src/python/test_health_scorer.py

# 3. Predict your own health score
python src/python/predict_health_score.py
```

### Health Metrics Analyzed

| Metric | Description | Range/Values | Impact on Score |
|--------|-------------|--------------|-----------------|
| **Sleep Hours** | Nightly sleep duration | 3.0-12.0 hours | Optimal: 7-9h |
| **Daily Steps** | Physical activity level | 500-25,000 steps | Target: 8,000+ |
| **Hydration** | Water intake | 0.5-5.0 liters | Optimal: 2-3L |
| **Heart Rate** | Resting heart rate | 40-110 bpm | Healthy: 55-75 |
| **Stress Level** | Perceived stress | low/medium/high | Lower is better |
| **Mood** | Daily mood state | good/neutral/bad | Positive impact |
| **Screen Time** | Digital device usage | 1-16 hours | Moderation key |
| **Weekend** | Day type factor | true/false | Behavior patterns |

### ML Model Performance
- **Best Model**: Auto-selected (Random Forest or Gradient Boosting)
- **Accuracy**: ~85-90% (MAE < 5 points on 100-point scale)
- **Features**: 8 input features with categorical encoding
- **Training**: 1500+ synthetic days with realistic correlations

### Sample Predictions
```json
{
  "sleep_hours": 7.2,
  "steps": 8500,
  "hydration_liters": 2.1,
  "heart_rate_rest": 66,
  "stress_level": "medium",
  "mood": "neutral",
  "screen_time_hours": 5.5,
  "is_weekend": false
}
// → Predicted Score: 72.5/100
```

---

## 10. Next Steps - Full Edge AI Implementation

### Planned Features
- **Computer Vision**: Posture detection using MediaPipe
- **Local LLM**: Health advice generation with Ollama
- **Desktop UI**: Cross-platform interface with real-time monitoring
- **Smart Reminders**: Context-aware notifications throughout the day

---

## 11. Hackathon Alignment – Qualcomm "Edge AI Consumer Utility App"

| Criteria          | Fit | Notes                                                             |
| ----------------- | --- | ----------------------------------------------------------------- |
| Consumer-oriented | ✅   | Everyday use, health-focused utility                              |
| Utility-focused   | ✅   | Provides actionable wellness and productivity value               |
| Edge AI-powered   | ✅   | All AI (posture, scoring, reminders) run locally                  |
| Cross-platform    | ✅   | Designed for Windows/macOS/Linux                                  |
| Developer-ready   | ✅   | Codebase with clear instructions, no external dependency required |

---

### Core Components

#### 1. ML Health Scorer (`ml_health_scorer.py`)
- **Purpose**: Main ML engine that predicts health scores from daily metrics
- **Models**: Random Forest and Gradient Boosting (auto-selects best performer)
- **Features**: Sleep, steps, hydration, heart rate, stress, mood, screen time
- **Output**: Health score from 0-100

#### 2. Data Generator (`data_generator.py`)
- **Purpose**: Creates realistic synthetic health data for training and testing
- **Profiles**: Supports different user types (athlete, stressed, sedentary, etc.)
- **Realism**: Correlates metrics (poor sleep → higher heart rate, weekend patterns)
- **Output**: JSON dataset with 7+ days of health data

### How the Data Generator Works

The data generator (`data_generator.py`) creates realistic synthetic health data by simulating different user profiles and their behavioral patterns:

#### User Profiles
- **Normal** (70%): Typical user with average habits
- **Athlete**: High activity, good sleep, low screen time
- **Stressed**: Poor sleep, high heart rate, irregular patterns
- **Sedentary**: Low steps, high screen time, poor hydration
- **Insomniac**: Very low sleep hours (3-5h), cascading effects
- **Overworker**: Long screen time, poor sleep, high stress
- **Healthy**: Optimal across all metrics
- **Unhealthy**: Poor habits across multiple areas

#### Realistic Correlations
The generator creates believable relationships between metrics:
- **Poor sleep** → Higher heart rate + increased stress
- **Weekend patterns** → More sleep, fewer steps, more screen time
- **High activity** → Better hydration needs + lower stress
- **Stress cascade** → Bad day affects next day's mood
- **Seasonal effects** → Weather impacts activity and mood

#### Sample Generation Process
```python
# 1. Choose profile (70% normal, 30% extreme)
profile = generate_extreme_profile()

# 2. Generate base metrics based on profile
if profile == "athlete":
    sleep_hours = 7.5-9.5h
    steps = 15,000-25,000
    hydration = 3.0-5.0L
    
# 3. Apply correlations and adjustments
heart_rate = base_rate + sleep_penalty - fitness_factor
hydration *= activity_boost * weekend_factor

# 4. Add realistic noise and constraints
final_value = max(min_value, min(max_value, calculated_value))
```

#### Why This Approach Works
- **Diversity**: 8 different user profiles ensure model sees edge cases
- **Realism**: Correlations match real-world health patterns
- **Scalability**: Can generate thousands of days for robust training
- **Flexibility**: Easy to add new profiles or adjust existing ones
- **Privacy**: No real user data needed for development

#### Example Generated Day
```json
{
  "profile": "stressed",
  "sleep_hours": 5.2,        // Poor sleep (stressed profile)
  "steps": 3400,             // Low activity (stress impact)
  "hydration_liters": 1.1,   // Forgot to drink water
  "heart_rate_rest": 82,     // Elevated (stress + poor sleep)
  "stress_level": "high",    // Direct from profile
  "mood": "bad",             // Influenced by previous day
  "screen_time_hours": 9.2,  // High (sedentary behavior)
  "is_weekend": false
}
```

#### 3. Model Training (`train_health_model.py`)
- **Purpose**: Trains ML models on generated data
- **Process**: Generates 2000+ days of synthetic data, trains multiple models
- **Validation**: Cross-validation and test set evaluation
- **Output**: Trained model saved as `health_model.pkl`

#### 4. Prediction Interface (`predict_health_score.py`)
- **Purpose**: Predicts health score for new user data
- **Input**: JSON file or hardcoded example data
- **Usage**: `python predict_health_score.py user_data.json`
- **Output**: Predicted health score

