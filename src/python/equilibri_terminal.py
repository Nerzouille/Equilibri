#!/usr/bin/env python3
"""
Simple Equilibri Health Monitoring - Simplified Version
"""

import json
import cv2
import time
import mediapipe as mp
from datetime import datetime
from pathlib import Path
import threading
import signal
import sys
import os
import logging
import warnings

# Import scoring function from posture_score.py to avoid duplication
from posture_score import compute_posture_score
# Import Ollama AI advisor
from ollama_advisor import OllamaAdvisor

# Suppress TensorFlow/MediaPipe log messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GLOG_minloglevel'] = '3'
warnings.filterwarnings('ignore')
logging.getLogger('tensorflow').setLevel(logging.ERROR)
logging.getLogger('mediapipe').setLevel(logging.ERROR)

# Redirect stderr temporarily to suppress I0000/W0000 messages
import sys
from io import StringIO

class SuppressOutput:
    def __init__(self):
        self.original_stderr = sys.stderr
        
    def __enter__(self):
        sys.stderr = StringIO()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr = self.original_stderr

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

class HealthMonitoring:
    def __init__(self):
        self.data_dir = Path("../../data")
        self.data_dir.mkdir(exist_ok=True)
        self.config_file = self.data_dir / "config.json"
        self.daily_file = self.data_dir / "daily.json"
        self.running = False
        
        # Camera and pose - keep permanently open
        self.cap = None
        self.pose = None
        
        # Manual data
        self.manual_data = {
            "sleep_hours": 8.0,
            "hydration_liters": 2.0,
            "steps": 5000,
            "stress_level": "medium",
            "mood": "neutral"
        }
        
        # AI Advisor Ollama
        self.ai_advisor = OllamaAdvisor(self.daily_file)
        
        # Signal handling
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C"""
        print("\nStopping monitoring...")
        self.running = False
        
        # Give final summary with AI
        self.ai_advisor.give_closing_summary()
        
        self.cleanup_camera()
        sys.exit(0)
        
    def init_camera(self):
        """Initialize camera and MediaPipe once"""
        if self.cap is None:
            print("Initializing camera...")
            with SuppressOutput():
                self.cap = cv2.VideoCapture(0)
                self.pose = mp_pose.Pose(
                    static_image_mode=False,
                    model_complexity=1,
                    smooth_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
            
            if not self.cap.isOpened():
                print("Cannot open camera")
                return False
            print("Camera initialized")
            return True
        return True
        
    def cleanup_camera(self):
        """Clean up camera resources"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        if self.pose is not None:
            self.pose.close()
            self.pose = None
        cv2.destroyAllWindows()
        
    def load_config(self):
        """Load configuration"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            return {}
        except:
            return {}
    
    def save_config(self, config):
        """Save configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Config save error: {e}")
    
    def calibrate_posture_distance(self):
        """Complete camera distance calibration"""
        print("\nPOSTURE CALIBRATION")
        print("=" * 50)
        print("Position yourself in your ideal work position")
        print("Press 'c' to start calibration")
        print("Press 'r' to restart")
        print("Press 'q' or ESC to cancel")
        
        if not self.init_camera():
            return None
        
        calibration_mode = False
        calibration_samples = []
        calibration_head_samples = []
        reference_shoulder_width = None
        reference_head_shoulder_ratio = None

        print("Camera preview open - position yourself comfortably")

        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Camera read error")
                break

            # Horizontal mirror
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)

            if results.pose_landmarks:
                # Draw landmarks
                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
                )

                # Calculate metrics
                landmarks = results.pose_landmarks.landmark
                nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
                left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]

                shoulder_width = abs(right_shoulder.x - left_shoulder.x)
                shoulder_mid_y = (left_shoulder.y + right_shoulder.y) / 2
                head_shoulder_height_ratio = abs(nose.y - shoulder_mid_y)

                # Calibration mode
                if calibration_mode:
                    calibration_samples.append(shoulder_width)
                    calibration_head_samples.append(head_shoulder_height_ratio)
                    
                    # Show calibration status
                    cv2.rectangle(frame, (10, 10), (600, 70), (0, 255, 255), -1)
                    cv2.putText(frame, f"CALIBRATING... {len(calibration_samples)}/30", 
                               (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
                    cv2.putText(frame, "Stay in your ideal position", 
                               (20, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

                    # Calibration complete
                    if len(calibration_samples) >= 30:
                        reference_shoulder_width = sum(calibration_samples) / len(calibration_samples)
                        reference_head_shoulder_ratio = sum(calibration_head_samples) / len(calibration_head_samples)
                        
                        print(f"\nCalibration complete!")
                        print(f"   Shoulder width: {reference_shoulder_width:.3f}")
                        print(f"   Head-shoulder ratio: {reference_head_shoulder_ratio:.3f}")
                        
                        cv2.destroyAllWindows()
                        
                        return {
                            "reference_shoulder_width": reference_shoulder_width,
                            "reference_head_shoulder_ratio": reference_head_shoulder_ratio,
                            "calibrated": True
                        }

                # Display current metrics
                shoulder_str = f"Shoulder width: {shoulder_width:.3f}"
                head_str = f"Head-shoulder ratio: {head_shoulder_height_ratio:.3f}"
                
                cv2.rectangle(frame, (10, frame.shape[0] - 80), (500, frame.shape[0] - 10), (0, 0, 0), -1)
                cv2.putText(frame, shoulder_str, (20, frame.shape[0] - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, head_str, (20, frame.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            cv2.imshow("Posture Calibration", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('c') and not calibration_mode:
                calibration_mode = True
                calibration_samples = []
                calibration_head_samples = []
                print("Calibration started - stay in your ideal position")
            elif key == ord('r'):
                calibration_mode = False
                calibration_samples = []
                calibration_head_samples = []
                print("Calibration reset")
            elif key == ord('q') or key == 27:  # ESC
                print("Calibration cancelled")
                break

        # Cleanup
        cv2.destroyAllWindows()
        return None

    def advanced_posture_check(self, config):
        """Advanced posture verification with real algorithm"""
        posture_config = config.get("posture", {})
        if not posture_config.get("calibrated", False):
            return None
            
        ref_shoulder_width = posture_config.get("reference_shoulder_width")
        ref_head_shoulder_ratio = posture_config.get("reference_head_shoulder_ratio")
        
        if not ref_shoulder_width or not ref_head_shoulder_ratio:
            return None
        
        try:
            if not self.init_camera():
                return None
            
            scores = []
            
            # Take 10 samples over 3 seconds
            for i in range(10):
                ret, frame = self.cap.read()
                if not ret:
                    continue
                
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.pose.process(rgb_frame)
                
                if results.pose_landmarks:
                    # Use imported function from posture_score.py
                    score_data = compute_posture_score(
                        results.pose_landmarks.landmark,
                        ref_shoulder_width,
                        ref_head_shoulder_ratio
                    )
                    # Function returns tuple, take first element (score)
                    score = score_data[0] if isinstance(score_data, tuple) else score_data
                    scores.append(score)
                
                time.sleep(0.3)
            
            avg_score = sum(scores) / len(scores) if scores else None
            
            # Add score to AI and check if it should give advice
            if avg_score is not None:
                self.ai_advisor.add_posture_score(avg_score)
                
                # Specific advice for very bad posture
                if avg_score < 40:
                    self.ai_advisor.give_bad_posture_advice(avg_score)
            
            return avg_score
            
        except Exception as e:
            print(f"Posture analysis error: {e}")
            return None
    
    def save_checkpoint(self, posture_score):
        """Save checkpoint"""
        try:
            # Load existing data
            daily_data = {}
            if self.daily_file.exists():
                try:
                    with open(self.daily_file, 'r') as f:
                        daily_data = json.load(f)
                except:
                    daily_data = {}
            
            # Create checkpoint
            checkpoint = {
                "timestamp": datetime.now().isoformat(),
                "time": datetime.now().strftime("%H:%M:%S"),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "day_of_week": datetime.now().strftime("%A"),
                "sleep_hours": self.manual_data["sleep_hours"],
                "steps": self.manual_data["steps"],
                "hydration_liters": self.manual_data["hydration_liters"],
                "heart_rate_rest": 70,
                "screen_time_hours": 6.0,
                "stress_level": self.manual_data["stress_level"],
                "mood": self.manual_data["mood"],
                "is_weekend": datetime.now().weekday() >= 5,
                "posture_score": posture_score if posture_score else 0
            }
            
            # Add to daily data
            if "checkpoints" not in daily_data:
                daily_data["checkpoints"] = []
            daily_data["checkpoints"].append(checkpoint)
            daily_data["date"] = checkpoint["date"]
            
            # Save
            with open(self.daily_file, 'w') as f:
                json.dump(daily_data, f, indent=2)
            
            return checkpoint
            
        except Exception as e:
            print(f"Save error: {e}")
            return None
    
    def monitoring_thread(self, config):
        """Monitoring thread"""
        while self.running:
            try:
                # Silent posture check
                posture_score = self.advanced_posture_check(config)
                
                if posture_score:
                    checkpoint = self.save_checkpoint(posture_score)
                    # Silent save without message
                else:
                    # Silent analysis failure
                    pass
                
                # Wait 30 seconds
                for i in range(30):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                # Silent error
                time.sleep(5)
    
    def run(self):
        """Main function"""
        print("EQUILIBRI - Simple Health Monitoring")
        print("=" * 50)
        
        # AI analysis of history at startup
        self.ai_advisor.analyze_startup_data()
        
        # MANDATORY calibration at startup
        config = self.load_config()
        
        print("\nCAMERA DISTANCE CALIBRATION")
        print("This step is required for accurate posture scoring")
        
        # Always force new calibration
        calibrate = input("Do you want to calibrate now? (Y/n): ").lower().strip()
        if calibrate != 'n':
            calibration_data = self.calibrate_posture_distance()
            if calibration_data:
                config["posture"] = {"calibrated": True, **calibration_data}
                self.save_config(config)
                print("Calibration complete and saved")
            else:
                print("Calibration failed - posture monitoring will be disabled")
                config["posture"] = {"calibrated": False}
        else:
            # Check if calibration already exists
            if not config.get("posture", {}).get("calibrated", False):
                print("No calibration found - posture monitoring will be disabled")
                config["posture"] = {"calibrated": False}
            else:
                print("Using existing calibration")
        
        # Initial data
        print("\nInitial data configuration:")
        try:
            sleep = input(f"Sleep hours (default: {self.manual_data['sleep_hours']}): ")
            if sleep.strip():
                self.manual_data["sleep_hours"] = float(sleep)
            
            hydration = input(f"Hydration in L (default: {self.manual_data['hydration_liters']}): ")
            if hydration.strip():
                self.manual_data["hydration_liters"] = float(hydration)
            
            steps = input(f"Number of steps (default: {self.manual_data['steps']}): ")
            if steps.strip():
                self.manual_data["steps"] = int(steps)
        except:
            print("Using default values")
        
        # Start monitoring
        print(f"\nStarting monitoring (check every 30s)")
        print("AI will give advice when needed")
        print("Available commands:")
        print("  hydration <value>  - Update hydration")
        print("  steps <value>      - Update steps")
        print("  status             - Show status")
        print("  quit               - Quit")
        
        self.running = True
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitoring_thread, args=(config,))
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Command loop
        while self.running:
            try:
                cmd = input("\n> ").strip().lower()
                
                if cmd == "quit":
                    self.running = False
                    print("Generating final summary...")
                    self.ai_advisor.give_closing_summary()
                    break
                elif cmd == "status":
                    print(f"Sleep: {self.manual_data['sleep_hours']}h")
                    print(f"Hydration: {self.manual_data['hydration_liters']}L")
                    print(f"Steps: {self.manual_data['steps']}")
                    print(f"Stress: {self.manual_data['stress_level']}")
                    print(f"Mood: {self.manual_data['mood']}")
                elif cmd.startswith("hydration "):
                    try:
                        value = float(cmd.split()[1])
                        self.manual_data["hydration_liters"] = value
                        print(f"Hydration updated: {value}L")
                    except:
                        print("Invalid format. Use: hydration 2.5")
                elif cmd.startswith("steps "):
                    try:
                        value = int(cmd.split()[1])
                        self.manual_data["steps"] = value
                        print(f"Steps updated: {value}")
                    except:
                        print("Invalid format. Use: steps 8000")
                elif cmd:
                    print("Unknown command. Type 'quit' to exit.")
                    
            except KeyboardInterrupt:
                self.running = False
                print("\nGenerating final summary...")
                self.ai_advisor.give_closing_summary()
                break
            except EOFError:
                self.running = False
                print("\nGenerating final summary...")
                self.ai_advisor.give_closing_summary()
                break
        
        print("\nMonitoring stopped")
        self.cleanup_camera()

def main():
    try:
        app = HealthMonitoring()
        app.run()
    except KeyboardInterrupt:
        print("\nProgram interrupted")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            app.cleanup_camera()
        except:
            pass

if __name__ == "__main__":
    main()
