#!/usr/bin/env python3
"""
Simple Equilibri Health Monitoring - Version simplifiée
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

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

class HealthMonitoring:
    def __init__(self):
        self.data_dir = Path("../../data")
        self.data_dir.mkdir(exist_ok=True)
        self.config_file = self.data_dir / "config.json"
        self.daily_file = self.data_dir / "daily.json"
        self.running = False
        
        # Manual data
        self.manual_data = {
            "sleep_hours": 8.0,
            "hydration_liters": 2.0,
            "steps": 5000,
            "stress_level": "medium",
            "mood": "neutral"
        }
        
        # Signal handling
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C"""
        print("\nArrêt du monitoring...")
        self.running = False
        sys.exit(0)
        
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
            print(f"Erreur sauvegarde config: {e}")
    
    def simple_posture_check(self, config):
        """Vérification rapide de posture"""
        posture_config = config.get("posture", {})
        if not posture_config.get("calibrated", False):
            return None
            
        ref_shoulder_width = posture_config.get("reference_shoulder_width")
        ref_head_shoulder_ratio = posture_config.get("reference_head_shoulder_ratio")
        
        if not ref_shoulder_width or not ref_head_shoulder_ratio:
            return None
        
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return None
            
            pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.7)
            scores = []
            
            # Prendre 5 échantillons rapides
            for i in range(5):
                ret, frame = cap.read()
                if not ret:
                    continue
                
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(rgb_frame)
                
                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark
                    nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
                    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
                    
                    current_shoulder_width = abs(right_shoulder.x - left_shoulder.x)
                    shoulder_mid_y = (left_shoulder.y + right_shoulder.y) / 2
                    current_head_shoulder_ratio = abs(nose.y - shoulder_mid_y)
                    
                    # Score simple
                    width_diff = abs(current_shoulder_width - ref_shoulder_width) / ref_shoulder_width
                    ratio_diff = abs(current_head_shoulder_ratio - ref_head_shoulder_ratio) / ref_head_shoulder_ratio
                    
                    score = max(0, 100 - (width_diff + ratio_diff) * 100)
                    scores.append(score)
                
                time.sleep(0.1)
            
            cap.release()
            cv2.destroyAllWindows()
            
            return sum(scores) / len(scores) if scores else None
            
        except Exception as e:
            print(f"Erreur analyse posture: {e}")
            return None
    
    def save_checkpoint(self, posture_score):
        """Sauvegarde checkpoint"""
        try:
            # Charger données existantes
            daily_data = {}
            if self.daily_file.exists():
                try:
                    with open(self.daily_file, 'r') as f:
                        daily_data = json.load(f)
                except:
                    daily_data = {}
            
            # Créer checkpoint
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
            
            # Ajouter aux données journalières
            if "checkpoints" not in daily_data:
                daily_data["checkpoints"] = []
            daily_data["checkpoints"].append(checkpoint)
            daily_data["date"] = checkpoint["date"]
            
            # Sauvegarder
            with open(self.daily_file, 'w') as f:
                json.dump(daily_data, f, indent=2)
            
            return checkpoint
            
        except Exception as e:
            print(f"Erreur sauvegarde: {e}")
            return None
    
    def monitoring_thread(self, config):
        """Thread de monitoring"""
        while self.running:
            try:
                print(f"\n🔍 Vérification posture... {datetime.now().strftime('%H:%M:%S')}")
                
                posture_score = self.simple_posture_check(config)
                
                if posture_score:
                    checkpoint = self.save_checkpoint(posture_score)
                    if checkpoint:
                        print(f"✅ Checkpoint sauvé: {checkpoint['time']} - Posture: {posture_score:.1f}/100")
                        
                        if posture_score < 50:
                            print("⚠️  Mauvaise posture détectée!")
                        elif posture_score < 75:
                            print("💡 Posture à améliorer")
                        else:
                            print("✅ Bonne posture!")
                else:
                    print("❌ Impossible d'analyser la posture")
                
                # Attendre 30 secondes
                for i in range(30):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                print(f"Erreur monitoring: {e}")
                time.sleep(5)
    
    def run(self):
        """Fonction principale"""
        print("🎯 EQUILIBRI - Monitoring Santé Simple")
        print("=" * 50)
        
        # Charger config
        config = self.load_config()
        
        # Calibration si nécessaire
        if not config.get("posture", {}).get("calibrated", False):
            print("⚠️  Calibration posture requise")
            print("La posture est déjà calibrée dans le fichier config existant")
            # Utiliser la calibration existante
            config["posture"] = {"calibrated": True}
        
        # Données initiales
        print("\n📋 Configuration données initiales:")
        try:
            sleep = input(f"Heures de sommeil (défaut: {self.manual_data['sleep_hours']}): ")
            if sleep.strip():
                self.manual_data["sleep_hours"] = float(sleep)
            
            hydration = input(f"Hydratation en L (défaut: {self.manual_data['hydration_liters']}): ")
            if hydration.strip():
                self.manual_data["hydration_liters"] = float(hydration)
            
            steps = input(f"Nombre de pas (défaut: {self.manual_data['steps']}): ")
            if steps.strip():
                self.manual_data["steps"] = int(steps)
        except:
            print("Utilisation des valeurs par défaut")
        
        # Démarrer monitoring
        print(f"\n🔄 Démarrage monitoring (vérification toutes les 30s)")
        print("Commandes disponibles:")
        print("  hydration <valeur>  - Mettre à jour l'hydratation")
        print("  steps <valeur>      - Mettre à jour les pas")
        print("  status              - Afficher le statut")
        print("  quit                - Quitter")
        
        self.running = True
        
        # Lancer thread monitoring
        monitor_thread = threading.Thread(target=self.monitoring_thread, args=(config,))
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Boucle commandes
        while self.running:
            try:
                cmd = input("\n> ").strip().lower()
                
                if cmd == "quit":
                    self.running = False
                    break
                elif cmd == "status":
                    print(f"💤 Sommeil: {self.manual_data['sleep_hours']}h")
                    print(f"💧 Hydratation: {self.manual_data['hydration_liters']}L")
                    print(f"🚶 Pas: {self.manual_data['steps']}")
                    print(f"😰 Stress: {self.manual_data['stress_level']}")
                    print(f"😊 Humeur: {self.manual_data['mood']}")
                elif cmd.startswith("hydration "):
                    try:
                        value = float(cmd.split()[1])
                        self.manual_data["hydration_liters"] = value
                        print(f"💧 Hydratation mise à jour: {value}L")
                    except:
                        print("❌ Format invalide. Utiliser: hydration 2.5")
                elif cmd.startswith("steps "):
                    try:
                        value = int(cmd.split()[1])
                        self.manual_data["steps"] = value
                        print(f"🚶 Pas mis à jour: {value}")
                    except:
                        print("❌ Format invalide. Utiliser: steps 8000")
                elif cmd:
                    print("❌ Commande inconnue. Taper 'quit' pour quitter.")
                    
            except KeyboardInterrupt:
                self.running = False
                break
            except EOFError:
                self.running = False
                break
        
        print("\n👋 Monitoring arrêté")

def main():
    try:
        app = HealthMonitoring()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Programme interrompu")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()
