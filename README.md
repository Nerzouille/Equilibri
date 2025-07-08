# Equilibri - Smart Health Monitoring with Local AI

A comprehensive health monitoring application that combines real-time posture detection, health scoring, and intelligent AI advice - all running locally on your machine.

## 🌟 Features

- **Real-time Posture Monitoring**: Webcam-based posture analysis using MediaPipe
- **Local AI Assistant**: Intelligent health advice using Ollama (completely offline)
- **Health Score Calculation**: ML-powered daily health scoring
- **Smart Reminders**: Context-aware advice when posture degrades
- **Privacy-First**: All data processed locally, nothing sent to external servers
- **Automatic Calibration**: Personal posture reference calibration
- **Historical Tracking**: Monitor trends and improvements over time

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** with pip
2. **Webcam** for posture detection
3. **Ollama** for AI features (optional but recommended)

### Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd Equilibri

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install Ollama (for AI features)
# Visit https://ollama.ai and install Ollama
# Then install a model:
ollama pull llama3:8b
```

### Running the Application

```bash
# Navigate to the Python source directory
cd src/python

# Run the main monitoring application
python equilibri_terminal.py
```

## 📁 Project Structure

```
Equilibri/
├── src/python/
│   ├── equilibri_terminal.py    # Main application with AI integration
│   ├── simple_monitoring.py     # Simplified version without AI
│   ├── posture_score.py         # Posture scoring algorithm
│   ├── ollama_advisor.py        # AI health advisor
│   ├── ml_health_scorer.py      # ML health scoring engine
│   ├── data_generator.py        # Synthetic health data generator
│   ├── train_health_model.py    # ML model training
│   ├── test_ollama.py          # Test Ollama integration
│   └── config.py               # Configuration constants
├── data/                        # Health data storage
│   ├── daily.json              # Daily checkpoints
│   └── config.json             # User calibration data
├── requirements.txt             # Python dependencies
├── equilibri.sh                # Launch script
└── README.md                   # This file
```

## 🎯 How to Use

### First Time Setup

1. **Start the application**:
   ```bash
   python src/python/equilibri_terminal.py
   ```

2. **Posture Calibration** (mandatory):
   - Position yourself in your ideal work posture
   - Press 'c' to start calibration
   - Hold the position for 30 measurements
   - Calibration data is saved for future sessions

3. **Initial Health Data**:
   - Enter your sleep hours, hydration, and step count
   - These can be updated during the session

### During Monitoring

The application will:
- **Monitor posture every 30 seconds** automatically
- **Provide AI advice** when posture degrades or at startup
- **Save checkpoints** with health scores and posture data
- **Give encouraging feedback** based on your performance

### Available Commands

While the application is running, you can use these commands:

```bash
hydration 2.5      # Update hydration to 2.5L
steps 8000         # Update step count to 8000
status             # Show current health data
quit               # Exit with AI summary
```

### AI Features (Requires Ollama)

- **Startup Analysis**: Reviews your 7-day history and provides quick advice
- **Smart Interventions**: Gives advice when posture score drops below 60/100
- **Session Summary**: Provides encouraging feedback and tips when you quit
- **Cooldown System**: Prevents advice spam (5-minute minimum between suggestions)

## 🧠 AI Configuration

### Ollama Setup

```bash
# Install Ollama from https://ollama.ai
# Pull the recommended model
ollama pull llama3:8b

# Verify installation
ollama list
```

### Testing AI Integration

```bash
# Test if Ollama is working correctly
python src/python/test_ollama.py
```

## 📊 Health Scoring

The application uses a sophisticated ML model that analyzes:

| Metric | Description | Optimal Range | Impact |
|--------|-------------|---------------|---------|
| **Sleep Hours** | Nightly sleep duration | 7-9 hours | High |
| **Daily Steps** | Physical activity | 8,000+ steps | High |
| **Hydration** | Water intake | 2-3 liters | Medium |
| **Posture Score** | Real-time posture quality | 70+ /100 | High |
| **Stress Level** | Self-reported stress | Low | Medium |
| **Mood** | Daily mood state | Good/Neutral | Medium |
| **Screen Time** | Digital device usage | <6 hours | Low |

### Posture Scoring Algorithm

The posture detection uses MediaPipe to analyze:
- Shoulder alignment (left/right balance)
- Head position relative to shoulders
- Forward head posture
- Distance from camera (too close/far)
- Lateral head tilt

Scores range from 0-100, with penalties for poor posture and bonuses for ideal positioning.

## 🔧 Advanced Usage

### Training Custom ML Models

```bash
# Generate synthetic training data and train models
python src/python/train_health_model.py --days 2000

# Test the trained model
python src/python/test_health_scorer.py
```

### Running Without AI

If you prefer to run without Ollama:

```bash
# Use the simplified version
python src/python/simple_monitoring.py
```

### Data Management

Your health data is stored in:
- `data/daily.json`: Health checkpoints and posture scores
- `data/config.json`: Calibration settings

All data stays on your machine and is never transmitted externally.

## 🛠️ Development

### Dependencies

Key Python packages:
- `opencv-python`: Computer vision and webcam access
- `mediapipe`: Pose detection and analysis
- `scikit-learn`: Machine learning models
- `ollama`: Local AI integration
- `numpy`, `pandas`: Data processing

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `python test_ollama.py`
5. Submit a pull request

## 🐛 Troubleshooting

### Common Issues

**Camera not found**:
```bash
# Check camera permissions and availability
# Ensure no other app is using the webcam
```

**Ollama not responding**:
```bash
# Check if Ollama is running
ollama list

# Start Ollama service if needed
ollama serve
```

**Permission errors**:
```bash
# Ensure camera permissions are granted
# Run with appropriate permissions
```

**Poor posture detection**:
- Ensure good lighting
- Position camera at eye level
- Sit 60-80cm from camera
- Recalibrate if needed

### Performance Tips

- Close other camera applications
- Ensure stable lighting conditions
- Use the simplified version if performance is poor
- Adjust monitoring frequency in code if needed

## 📈 Health Insights

The application provides:
- **Real-time posture scoring** with visual feedback
- **Trend analysis** over days and weeks
- **Personalized AI recommendations** based on your patterns
- **Encouraging feedback** to maintain motivation
- **Actionable advice** for immediate improvements

## 🎮 Demo Mode

For demonstration purposes:
```bash
# Quick test of all features
python src/python/test_health_scorer.py

# Test just the AI integration
python src/python/test_ollama.py

# Manual posture scoring
python src/python/posture_score.py
```

## 📝 License

[Add your license information here]

## 🤝 Support

For questions or issues:
1. Check the troubleshooting section
2. Review the code documentation
3. Test individual components
4. Create an issue with detailed information

---

**Equilibri** - Your personal health companion, powered by local AI and computer vision.

