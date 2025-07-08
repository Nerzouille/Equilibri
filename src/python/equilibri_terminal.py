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
import os
import logging
import warnings

# Importer la fonction de scoring depuis posture_score.py pour éviter la duplication
from posture_score import compute_posture_score
# Importer l'advisor IA Ollama
from ollama_advisor import OllamaAdvisor

# Supprimer les messages de log TensorFlow/MediaPipe
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GLOG_minloglevel'] = '3'
warnings.filterwarnings('ignore')
logging.getLogger('tensorflow').setLevel(logging.ERROR)
logging.getLogger('mediapipe').setLevel(logging.ERROR)

# Rediriger stderr temporairement pour supprimer les messages I0000/W0000
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
        
        # Camera et pose - garder ouverts en permanence
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
        
        # IA Advisor Ollama
        self.ai_advisor = OllamaAdvisor(self.daily_file)
        
        # Signal handling
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C"""
        print("\nArrêt du monitoring...")
        self.running = False
        
        # Donner le bilan final avec l'IA
        self.ai_advisor.give_closing_summary()
        
        self.cleanup_camera()
        sys.exit(0)
        
    def init_camera(self):
        """Initialiser la caméra et MediaPipe une seule fois"""
        if self.cap is None:
            print("Initialisation de la caméra...")
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
                print("Impossible d'ouvrir la caméra")
                return False
            print("Caméra initialisée")
            return True
        return True
        
    def cleanup_camera(self):
        """Nettoyer les ressources caméra"""
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
            print(f"Erreur sauvegarde config: {e}")
    
    def calibrate_posture_distance(self):
        """Calibration complète de la distance à la caméra"""
        print("\nCALIBRATION POSTURE")
        print("=" * 50)
        print("Positionnez-vous dans votre position de travail idéale")
        print("Appuyez sur 'c' pour commencer la calibration")
        print("Appuyez sur 'r' pour recommencer")
        print("Appuyez sur 'q' ou ESC pour annuler")
        
        if not self.init_camera():
            return None
        
        calibration_mode = False
        calibration_samples = []
        calibration_head_samples = []
        reference_shoulder_width = None
        reference_head_shoulder_ratio = None

        print("Aperçu caméra ouvert - positionnez-vous confortablement")

        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Erreur lecture caméra")
                break

            # Miroir horizontal
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)

            if results.pose_landmarks:
                # Dessiner les landmarks
                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
                )

                # Calculer métriques
                landmarks = results.pose_landmarks.landmark
                nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
                left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]

                shoulder_width = abs(right_shoulder.x - left_shoulder.x)
                shoulder_mid_y = (left_shoulder.y + right_shoulder.y) / 2
                head_shoulder_height_ratio = abs(nose.y - shoulder_mid_y)

                # Mode calibration
                if calibration_mode:
                    calibration_samples.append(shoulder_width)
                    calibration_head_samples.append(head_shoulder_height_ratio)
                    
                    # Afficher statut calibration
                    cv2.rectangle(frame, (10, 10), (600, 70), (0, 255, 255), -1)
                    cv2.putText(frame, f"CALIBRATION... {len(calibration_samples)}/30", 
                               (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
                    cv2.putText(frame, "Restez dans votre position ideale", 
                               (20, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

                    # Calibration terminée
                    if len(calibration_samples) >= 30:
                        reference_shoulder_width = sum(calibration_samples) / len(calibration_samples)
                        reference_head_shoulder_ratio = sum(calibration_head_samples) / len(calibration_head_samples)
                        
                        print(f"\nCalibration terminée!")
                        print(f"   Largeur épaules: {reference_shoulder_width:.3f}")
                        print(f"   Ratio tête-épaules: {reference_head_shoulder_ratio:.3f}")
                        
                        cv2.destroyAllWindows()
                        
                        return {
                            "reference_shoulder_width": reference_shoulder_width,
                            "reference_head_shoulder_ratio": reference_head_shoulder_ratio,
                            "calibrated": True
                        }

                # Affichage des métriques actuelles
                shoulder_str = f"Largeur epaules: {shoulder_width:.3f}"
                head_str = f"Ratio tete-epaules: {head_shoulder_height_ratio:.3f}"
                
                cv2.rectangle(frame, (10, frame.shape[0] - 80), (500, frame.shape[0] - 10), (0, 0, 0), -1)
                cv2.putText(frame, shoulder_str, (20, frame.shape[0] - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, head_str, (20, frame.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            cv2.imshow("Calibration Posture", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('c') and not calibration_mode:
                calibration_mode = True
                calibration_samples = []
                calibration_head_samples = []
                print("Calibration commencée - restez dans votre position idéale")
            elif key == ord('r'):
                calibration_mode = False
                calibration_samples = []
                calibration_head_samples = []
                print("Calibration remise à zéro")
            elif key == ord('q') or key == 27:  # ESC
                print("Calibration annulée")
                break

        # Nettoyage
        cv2.destroyAllWindows()
        return None

    def advanced_posture_check(self, config):
        """Vérification avancée de posture avec le vrai algorithme"""
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
            
            # Prendre 10 échantillons sur 3 secondes
            for i in range(10):
                ret, frame = self.cap.read()
                if not ret:
                    continue
                
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.pose.process(rgb_frame)
                
                if results.pose_landmarks:
                    # Utiliser la fonction importée de posture_score.py
                    score_data = compute_posture_score(
                        results.pose_landmarks.landmark,
                        ref_shoulder_width,
                        ref_head_shoulder_ratio
                    )
                    # La fonction retourne un tuple, on prend le premier élément (score)
                    score = score_data[0] if isinstance(score_data, tuple) else score_data
                    scores.append(score)
                
                time.sleep(0.3)
            
            avg_score = sum(scores) / len(scores) if scores else None
            
            # Ajouter le score à l'IA et vérifier si elle doit donner un conseil
            if avg_score is not None:
                self.ai_advisor.add_posture_score(avg_score)
                
                # Conseil spécifique pour très mauvaise posture
                if avg_score < 40:
                    self.ai_advisor.give_bad_posture_advice(avg_score)
            
            return avg_score
            
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
                # Vérification silencieuse de la posture
                posture_score = self.advanced_posture_check(config)
                
                if posture_score:
                    checkpoint = self.save_checkpoint(posture_score)
                    # Sauvegarde silencieuse sans message
                else:
                    # Échec silencieux de l'analyse
                    pass
                
                # Attendre 30 secondes
                for i in range(30):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                # Erreur silencieuse
                time.sleep(5)
    
    def run(self):
        """Fonction principale"""
        print("EQUILIBRI - Monitoring Santé Simple")
        print("=" * 50)
        
        # Analyse IA de l'historique au démarrage
        self.ai_advisor.analyze_startup_data()
        
        # Calibration OBLIGATOIRE au démarrage
        config = self.load_config()
        
        print("\nCALIBRATION DISTANCE CAMÉRA")
        print("Cette étape est obligatoire pour un score de posture précis")
        
        # Toujours forcer une nouvelle calibration
        calibrate = input("Voulez-vous calibrer maintenant? (Y/n): ").lower().strip()
        if calibrate != 'n':
            calibration_data = self.calibrate_posture_distance()
            if calibration_data:
                config["posture"] = {"calibrated": True, **calibration_data}
                self.save_config(config)
                print("Calibration terminée et sauvegardée")
            else:
                print("Calibration échouée - le monitoring de posture sera désactivé")
                config["posture"] = {"calibrated": False}
        else:
            # Vérifier si une calibration existe déjà
            if not config.get("posture", {}).get("calibrated", False):
                print("Aucune calibration trouvée - le monitoring de posture sera désactivé")
                config["posture"] = {"calibrated": False}
            else:
                print("Utilisation de la calibration existante")
        
        # Données initiales
        print("\nConfiguration données initiales:")
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
        print(f"\nDémarrage monitoring (vérification toutes les 30s)")
        print("L'IA donnera des conseils quand nécessaire")
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
                    print("Génération du bilan final...")
                    self.ai_advisor.give_closing_summary()
                    break
                elif cmd == "status":
                    print(f"Sommeil: {self.manual_data['sleep_hours']}h")
                    print(f"Hydratation: {self.manual_data['hydration_liters']}L")
                    print(f"Pas: {self.manual_data['steps']}")
                    print(f"Stress: {self.manual_data['stress_level']}")
                    print(f"Humeur: {self.manual_data['mood']}")
                elif cmd.startswith("hydration "):
                    try:
                        value = float(cmd.split()[1])
                        self.manual_data["hydration_liters"] = value
                        print(f"Hydratation mise à jour: {value}L")
                    except:
                        print("Format invalide. Utiliser: hydration 2.5")
                elif cmd.startswith("steps "):
                    try:
                        value = int(cmd.split()[1])
                        self.manual_data["steps"] = value
                        print(f"Pas mis à jour: {value}")
                    except:
                        print("Format invalide. Utiliser: steps 8000")
                elif cmd:
                    print("Commande inconnue. Taper 'quit' pour quitter.")
                    
            except KeyboardInterrupt:
                self.running = False
                print("\nGénération du bilan final...")
                self.ai_advisor.give_closing_summary()
                break
            except EOFError:
                self.running = False
                print("\nGénération du bilan final...")
                self.ai_advisor.give_closing_summary()
                break
        
        print("\nMonitoring arrêté")
        self.cleanup_camera()

def main():
    try:
        app = HealthMonitoring()
        app.run()
    except KeyboardInterrupt:
        print("\nProgramme interrompu")
    except Exception as e:
        print(f"Erreur: {e}")
    finally:
        try:
            app.cleanup_camera()
        except:
            pass

if __name__ == "__main__":
    main()
