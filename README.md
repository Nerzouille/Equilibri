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

## 9. Health Data Generator - Testing & Development

### Overview
To facilitate development and testing of the HealthMate application, we've created a realistic health data generator that produces believable user activity patterns over a 7-day period.

### Location
```
src/python/normal_history_generator.py
```

### 🚀 How to Use
```bash
# Run the generator
python src/python/normal_history_generator.py

# Output file
src/python/health_data.json
```

### What it Generates
The script creates **7 days** of realistic health data including:

| Metric | Description | Realistic Features |
|--------|-------------|-------------------|
| **Sleep Hours** | 6.0-8.5h weekdays, 7.0-9.5h weekends | Weekend sleep-ins |
| **Daily Steps** | 6k-12k weekdays, 4k-8k weekends | Work vs. leisure patterns |
| **Hydration** | 1.0-2.5L | Correlates with activity level |
| **Heart Rate** | 55-80 bpm | Affected by sleep quality |
| **Screen Time** | 2.0-7.0h | Higher on weekends & low activity days |
| **Stress Level** | low/medium/high | Based on sleep, activity, day type |
| **Mood** | good/neutral/bad | Influenced by previous day & stress |

### Smart Correlations
The generator creates **realistic relationships** between metrics:

- **Poor sleep** → Higher heart rate + more stress
- **Weekend patterns** → More sleep, less steps, more screen time
- **High activity** → Better hydration + lower stress
- **Mood continuity** → Yesterday's mood influences today's
- **Cascading effects** → One bad day can affect the next

### Sample Output
```json
[
  {
    "date": "2024-01-15",
    "day_of_week": "Monday",
    "sleep_hours": 7.2,
    "steps": 8500,
    "hydration_liters": 1.8,
    "heart_rate_rest": 62,
    "screen_time_hours": 4.5,
    "stress_level": "medium",
    "mood": "good",
    "is_weekend": false
  }
]
```

### Why Use This?
- **Test AI algorithms** with realistic patterns
- **Demo the app** with believable user journeys
- **Validate health scoring** logic with correlated data
- **Debug edge cases** like stress spikes or mood dips
- **No privacy concerns** - completely synthetic data

### Customization
Easy to modify for different user profiles by adjusting the base ranges in `generate_realistic_day()` function.

---

## 10. Hackathon Alignment – Qualcomm "Edge AI Consumer Utility App"

| Criteria          | Fit | Notes                                                             |
| ----------------- | --- | ----------------------------------------------------------------- |
| Consumer-oriented | ✅   | Everyday use, health-focused utility                              |
| Utility-focused   | ✅   | Provides actionable wellness and productivity value               |
| Edge AI-powered   | ✅   | All AI (posture, scoring, reminders) run locally                  |
| Cross-platform    | ✅   | Designed for Windows/macOS/Linux                                  |
| Developer-ready   | ✅   | Codebase with clear instructions, no external dependency required |

