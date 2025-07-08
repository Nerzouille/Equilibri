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
    
    def calibrate_posture_distance(self):
        """Calibration complète de la distance à la caméra (comme posture_score.py)"""
        print("\n🎯 CALIBRATION POSTURE")
        print("=" * 50)
        print("Positionnez-vous dans votre position de travail idéale")
        print("Appuyez sur 'c' pour commencer la calibration")
        print("Appuyez sur 'r' pour recommencer")
        print("Appuyez sur 'q' ou ESC pour annuler")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Impossible d'ouvrir la caméra")
            return None

        pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        calibration_mode = False
        calibration_samples = []
        calibration_head_samples = []
        reference_shoulder_width = None
        reference_head_shoulder_ratio = None

        print("📹 Aperçu caméra ouvert - positionnez-vous confortablement")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Erreur lecture caméra")
                break

            # Miroir horizontal
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb_frame)

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
                        
                        print(f"\n✅ Calibration terminée!")
                        print(f"   📏 Largeur épaules: {reference_shoulder_width:.3f}")
                        print(f"   📐 Ratio tête-épaules: {reference_head_shoulder_ratio:.3f}")
                        
                        cap.release()
                        cv2.destroyAllWindows()
                        
                        return {
                            "reference_shoulder_width": reference_shoulder_width,
                            "reference_head_shoulder_ratio": reference_head_shoulder_ratio,
                            "calibration_date": datetime.now().isoformat()
                        }

                # Afficher instructions
                if not calibration_mode:
                    cv2.putText(frame, "Position ideale -> Appuyez 'c'", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, "Recommencer -> Appuyez 'r'", 
                               (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    cv2.putText(frame, "Annuler -> Appuyez 'q' ou ESC", 
                               (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                # Afficher métriques actuelles
                cv2.putText(frame, f"Largeur epaules: {shoulder_width:.3f}", 
                           (10, frame.shape[0] - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(frame, f"Ratio tete-epaules: {head_shoulder_height_ratio:.3f}", 
                           (10, frame.shape[0] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                # Afficher calibration actuelle si disponible
                if reference_shoulder_width is not None:
                    cv2.putText(frame, f"Ref: {reference_shoulder_width:.3f} | {reference_head_shoulder_ratio:.3f}", 
                               (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

            else:
                # Pas de pose détectée
                cv2.putText(frame, "Positionnez-vous face à la caméra", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            cv2.imshow('Calibration Posture - Equilibri', frame)

            # Gestion des touches
            key = cv2.waitKey(5) & 0xFF
            if key == 27 or key == ord('q'):  # ESC ou 'q' pour quitter
                print("\n❌ Calibration annulée")
                break
            elif key == ord('c') and not calibration_mode:  # 'c' pour calibrer
                if results.pose_landmarks:
                    calibration_mode = True
                    calibration_samples = []
                    calibration_head_samples = []
                    print("🎯 Calibration démarrée! Restez dans votre position...")
                else:
                    print("❌ Aucune pose détectée, positionnez-vous face à la caméra")
            elif key == ord('r'):  # 'r' pour recommencer
                calibration_mode = False
                calibration_samples = []
                calibration_head_samples = []
                reference_shoulder_width = None
                reference_head_shoulder_ratio = None
                print("🔄 Calibration remise à zéro")

        # Nettoyage
        cap.release()
        cv2.destroyAllWindows()
        return None
    def compute_posture_score(self, landmarks, reference_shoulder_width=None, reference_head_shoulder_ratio=None):
        """Score de posture basé sur des critères réalistes (copié de posture_score.py)"""
        nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        left_ear = landmarks[mp_pose.PoseLandmark.LEFT_EAR.value]
        right_ear = landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value]

        # 1. Alignement des épaules
        shoulder_diff = abs(left_shoulder.y - right_shoulder.y)

        # 2. Position avant de la tête
        shoulder_mid_y = (left_shoulder.y + right_shoulder.y) / 2
        head_forward_ratio = (nose.y - shoulder_mid_y)

        # 3. Ratio hauteur tête-épaules
        head_shoulder_height_ratio = abs(nose.y - shoulder_mid_y)

        # 4. Inclinaison latérale de la tête
        ear_diff = abs(left_ear.y - right_ear.y)

        # 5. Distance avant/arrière basée sur la largeur des épaules
        shoulder_width = abs(right_shoulder.x - left_shoulder.x)

        # Utiliser les références si disponibles
        if reference_shoulder_width is not None:
            min_good_width = reference_shoulder_width * 0.8
            max_good_width = reference_shoulder_width * 1.2
            width_ratio = shoulder_width / reference_shoulder_width
            distance_status = "OK"
            if width_ratio > 1.2:
                distance_status = "TROP PROCHE"
            elif width_ratio < 0.8:
                distance_status = "TROP LOIN"
        else:
            min_good_width = 0.22
            max_good_width = 0.45
            distance_status = "OK" if min_good_width <= shoulder_width <= max_good_width else ("TROP LOIN" if shoulder_width < min_good_width else "TROP PROCHE")

        # Détection penché en avant
        forward_lean_detected = False
        if reference_head_shoulder_ratio is not None:
            lean_threshold = reference_head_shoulder_ratio * 0.7
            if head_shoulder_height_ratio < lean_threshold:
                forward_lean_detected = True
        else:
            if head_shoulder_height_ratio < 0.15:
                forward_lean_detected = True

        # Calcul du score (commence à 100)
        score = 100

        # Pénalités
        if shoulder_diff > 0.03:
            penalty = min(40, (shoulder_diff - 0.03) * 1000)
            score -= penalty

        if head_forward_ratio > -0.02:
            penalty = min(40, (head_forward_ratio + 0.02) * 800)
            score -= penalty

        if ear_diff > 0.04:
            penalty = min(50, (ear_diff - 0.04) * 800)
            score -= penalty

        if forward_lean_detected:
            if reference_head_shoulder_ratio is not None:
                deviation = reference_head_shoulder_ratio - head_shoulder_height_ratio
                penalty = min(40, deviation * 300)
                score -= penalty
            else:
                penalty = min(30, (0.15 - head_shoulder_height_ratio) * 200)
                score -= penalty

        if shoulder_width < min_good_width:
            distance_penalty = min(45, (min_good_width - shoulder_width) * 500)
            score -= distance_penalty

        if shoulder_width > max_good_width:
            distance_penalty = min(25, (shoulder_width - max_good_width) * 200)
            score -= distance_penalty

        # Bonus pour distance parfaite
        if reference_shoulder_width is not None:
            width_ratio = shoulder_width / reference_shoulder_width
            if 0.95 <= width_ratio <= 1.05:
                score += 5
            elif 0.9 <= width_ratio <= 1.1:
                score += 2

        score = max(0, min(100, int(score)))
        return score

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
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return None
            
            pose = mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                smooth_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            scores = []
            
            # Prendre 10 échantillons sur 3 secondes
            for i in range(10):
                ret, frame = cap.read()
                if not ret:
                    continue
                
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(rgb_frame)
                
                if results.pose_landmarks:
                    score = self.compute_posture_score(
                        results.pose_landmarks.landmark,
                        ref_shoulder_width,
                        ref_head_shoulder_ratio
                    )
                    scores.append(score)
                
                time.sleep(0.3)
            
            cap.release()
            cv2.destroyAllWindows()
            
            return sum(scores) / len(scores) if scores else None
            
        except Exception as e:
            print(f"Erreur analyse posture: {e}")
            try:
                cap.release()
                cv2.destroyAllWindows()
            except:
                pass
            return None
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
        print("🎯 EQUILIBRI - Monitoring Santé Simple")
        print("=" * 50)
        
        # Calibration OBLIGATOIRE au démarrage
        config = self.load_config()
        
        print("🎯 CALIBRATION DISTANCE CAMÉRA")
        print("Cette étape est obligatoire pour un score de posture précis")
        
        # Toujours forcer une nouvelle calibration
        calibrate = input("Voulez-vous calibrer maintenant? (Y/n): ").lower().strip()
        if calibrate != 'n':
            calibration_data = self.calibrate_posture_distance()
            if calibration_data:
                config["posture"] = {"calibrated": True, **calibration_data}
                self.save_config(config)
                print("✅ Calibration terminée et sauvegardée")
            else:
                print("❌ Calibration échouée - le monitoring de posture sera désactivé")
                config["posture"] = {"calibrated": False}
        else:
            # Vérifier si une calibration existe déjà
            if not config.get("posture", {}).get("calibrated", False):
                print("⚠️  Aucune calibration trouvée - le monitoring de posture sera désactivé")
                config["posture"] = {"calibrated": False}
            else:
                print("ℹ️  Utilisation de la calibration existante")
        
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
