#!/usr/bin/env python3
"""
Simple Equilibri Health Monitoring
"""

import json
import cv2
import time
import mediapipe as mp
from datetime import datetime
from pathlib import Path
import threading

# Import scoring function from posture_score.py to avoid duplication
from posture_score import compute_posture_score

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

class SimpleMonitoring:
    def __init__(self):
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.config_file = self.data_dir / "config.json"
        self.daily_file = self.data_dir / "daily.json"
        self.running = False
        
        # Manual data defaults
        self.manual_data = {
            "sleep_hours": 8.0,
            "hydration_liters": 2.0,
            "steps": 5000,
            "stress_level": "medium",
            "mood": "neutral"
        }
        
    def load_config(self):
        """Load configuration"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def save_config(self, config):
        """Save configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def calibrate_posture(self):
        """Simple posture calibration"""
        print("Posture calibration - Position yourself correctly")
        print("Press 'c' to calibrate, 'q' to quit")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Cannot open camera")
            return None
        
        pose = mp_pose.Pose()
        calibration_samples = []
        calibration_head_samples = []
        calibrating = False
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb_frame)
            
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                
                # Calculate metrics
                landmarks = results.pose_landmarks.landmark
                nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
                left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
                
                shoulder_width = abs(right_shoulder.x - left_shoulder.x)
                shoulder_mid_y = (left_shoulder.y + right_shoulder.y) / 2
                head_shoulder_ratio = abs(nose.y - shoulder_mid_y)
                
                if calibrating:
                    calibration_samples.append(shoulder_width)
                    calibration_head_samples.append(head_shoulder_ratio)
                    
                    cv2.putText(frame, f"Calibrating... {len(calibration_samples)}/30", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    if len(calibration_samples) >= 30:
                        ref_shoulder_width = sum(calibration_samples) / len(calibration_samples)
                        ref_head_shoulder_ratio = sum(calibration_head_samples) / len(calibration_head_samples)
                        
                        print(f"Calibration complete!")
                        print(f"Reference shoulder width: {ref_shoulder_width:.3f}")
                        print(f"Reference head-shoulder ratio: {ref_head_shoulder_ratio:.3f}")
                        
                        cap.release()
                        cv2.destroyAllWindows()
                        
                        return {
                            "reference_shoulder_width": ref_shoulder_width,
                            "reference_head_shoulder_ratio": ref_head_shoulder_ratio,
                            "calibration_date": datetime.now().isoformat()
                        }
                else:
                    cv2.putText(frame, "Press 'c' to calibrate", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow('Calibration', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c') and results.pose_landmarks:
                calibrating = True
                calibration_samples = []
                calibration_head_samples = []
                print("Calibration started!")
        
        cap.release()
        cv2.destroyAllWindows()
        return None
    
    def get_posture_score(self, config):
        """Get current posture score using the proper scoring function"""
        posture_config = config.get("posture", {})
        ref_shoulder_width = posture_config.get("reference_shoulder_width")
        ref_head_shoulder_ratio = posture_config.get("reference_head_shoulder_ratio")
        
        if not ref_shoulder_width or not ref_head_shoulder_ratio:
            return None
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return None
        
        pose = mp_pose.Pose()
        scores = []
        
        # Take 10 samples over 2 seconds
        for _ in range(10):
            ret, frame = cap.read()
            if not ret:
                continue
            
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb_frame)
            
            if results.pose_landmarks:
                # Use complete function from posture_score.py instead of simplified calculation
                score_data = compute_posture_score(
                    results.pose_landmarks.landmark,
                    ref_shoulder_width,
                    ref_head_shoulder_ratio
                )
                # Function returns tuple, take first element (score)
                score = score_data[0] if isinstance(score_data, tuple) else score_data
                scores.append(score)
            
            time.sleep(0.2)
        
        cap.release()
        cv2.destroyAllWindows()
        
        return sum(scores) / len(scores) if scores else None
    
    def save_checkpoint(self, posture_score):
        """Save a checkpoint with current data"""
        try:
            # Load existing data
            daily_data = {}
            if self.daily_file.exists():
                with open(self.daily_file, 'r') as f:
                    daily_data = json.load(f)
            
            # Create checkpoint
            checkpoint = {
                "timestamp": datetime.now().isoformat(),
                "time": datetime.now().strftime("%H:%M:%S"),
                "date": datetime.now().strftime("%Y-%m-%d"),
                "day_of_week": datetime.now().strftime("%A"),
                "sleep_hours": self.manual_data["sleep_hours"],
                "steps": self.manual_data["steps"],
                "hydration_liters": self.manual_data["hydration_liters"],
                "heart_rate_rest": 70,  # Default
                "screen_time_hours": 6.0,  # Default
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
            
            print(f"Checkpoint saved at {checkpoint['time']} - Posture: {posture_score:.1f}/100")
            
        except Exception as e:
            print(f"Error saving checkpoint: {e}")
    
    def command_handler(self):
        """Handle user commands"""
        print("Commands: hydration <value>, steps <value>, sleep <value>, stress <level>, mood <mood>, status, quit")
        
        while self.running:
            try:
                cmd = input().strip().lower()
                
                if cmd == "quit":
                    self.running = False
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
                        print(f"Hydration updated to {value}L")
                    except:
                        print("Invalid format. Use: hydration 2.5")
                elif cmd.startswith("steps "):
                    try:
                        value = int(cmd.split()[1])
                        self.manual_data["steps"] = value
                        print(f"Steps updated to {value}")
                    except:
                        print("Invalid format. Use: steps 8000")
                elif cmd.startswith("sleep "):
                    try:
                        value = float(cmd.split()[1])
                        self.manual_data["sleep_hours"] = value
                        print(f"Sleep updated to {value}h")
                    except:
                        print("Invalid format. Use: sleep 7.5")
                elif cmd.startswith("stress "):
                    try:
                        level = cmd.split()[1]
                        if level in ["low", "medium", "high"]:
                            self.manual_data["stress_level"] = level
                            print(f"Stress updated to {level}")
                        else:
                            print("Use: stress low/medium/high")
                    except:
                        print("Invalid format. Use: stress medium")
                elif cmd.startswith("mood "):
                    try:
                        mood = cmd.split()[1]
                        if mood in ["good", "neutral", "bad"]:
                            self.manual_data["mood"] = mood
                            print(f"Mood updated to {mood}")
                        else:
                            print("Use: mood good/neutral/bad")
                    except:
                        print("Invalid format. Use: mood good")
                        
            except EOFError:
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def monitoring_loop(self, config):
        """Main monitoring loop"""
        print("Starting monitoring... (checking posture every 2 minutes)")
        
        while self.running:
            try:
                print(f"Checking posture... {datetime.now().strftime('%H:%M:%S')}")
                posture_score = self.get_posture_score(config)
                
                if posture_score:
                    self.save_checkpoint(posture_score)
                    
                    if posture_score < 50:
                        print("⚠️  Poor posture detected!")
                    elif posture_score < 75:
                        print("💡 Posture could be improved")
                    else:
                        print("✅ Good posture!")
                else:
                    print("❌ Could not analyze posture")
                
                # Wait 2 minutes
                for i in range(120):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                print(f"Error in monitoring: {e}")
                time.sleep(5)
    
    def run(self):
        """Main run function"""
        print("Simple Health Monitoring")
        print("=" * 40)
        
        config = self.load_config()
        
        # Check if posture is calibrated
        if not config.get("posture", {}).get("reference_shoulder_width"):
            print("Posture not calibrated. Starting calibration...")
            calibration_data = self.calibrate_posture()
            if calibration_data:
                config["posture"] = calibration_data
                self.save_config(config)
                print("Calibration saved!")
            else:
                print("Calibration failed. Posture monitoring will be disabled.")
                return
        else:
            print("Using existing posture calibration.")
        
        # Initialize manual data
        print("\nInitial data entry:")
        try:
            sleep = input(f"Sleep hours (default {self.manual_data['sleep_hours']}): ")
            if sleep.strip():
                self.manual_data["sleep_hours"] = float(sleep)
            
            hydration = input(f"Hydration in L (default {self.manual_data['hydration_liters']}): ")
            if hydration.strip():
                self.manual_data["hydration_liters"] = float(hydration)
            
            steps = input(f"Steps (default {self.manual_data['steps']}): ")
            if steps.strip():
                self.manual_data["steps"] = int(steps)
        except:
            print("Using defaults")
        
        self.running = True
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitoring_loop, args=(config,))
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Handle commands
        self.command_handler()
        
        print("Monitoring stopped.")

def main():
    try:
        app = SimpleMonitoring()
        app.run()
    except KeyboardInterrupt:
        print("\nProgram interrupted")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
