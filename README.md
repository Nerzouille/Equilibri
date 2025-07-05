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

## 9. Hackathon Alignment – Qualcomm "Edge AI Consumer Utility App"

| Criteria          | Fit | Notes                                                             |
| ----------------- | --- | ----------------------------------------------------------------- |
| Consumer-oriented | ✅   | Everyday use, health-focused utility                              |
| Utility-focused   | ✅   | Provides actionable wellness and productivity value               |
| Edge AI-powered   | ✅   | All AI (posture, scoring, reminders) run locally                  |
| Cross-platform    | ✅   | Designed for Windows/macOS/Linux                                  |
| Developer-ready   | ✅   | Codebase with clear instructions, no external dependency required |
