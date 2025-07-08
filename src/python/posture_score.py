import cv2
import mediapipe as mp
import time
import math

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def compute_posture_score(landmarks):
    """
    Score de posture amélioré :
    - Vérifie si la tête est penchée (gauche/droite)
    - Vérifie si la tête est trop en avant (nez trop bas)
    - Vérifie si les épaules sont inclinées
    Retourne 1 si la posture est correcte, 0 sinon.
    """
    nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    left_ear = landmarks[mp_pose.PoseLandmark.LEFT_EAR.value]
    right_ear = landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value]

    # Shoulders angle (to detect if they are tilted)
    dx = right_shoulder.x - left_shoulder.x
    dy = right_shoulder.y - left_shoulder.y
    shoulder_angle = math.degrees(math.atan2(dy, dx))

    # Head tilt (nose by ear to detect if the head is tilted)
    ear_mid_y = (left_ear.y + right_ear.y) / 2
    head_tilt = abs(nose.y - ear_mid_y)

    # Criterias
    if abs(shoulder_angle) > 15:  # shoulders are tilted
        return 0, shoulder_angle, head_tilt
    if head_tilt > 0.07:  # head is tilted
        return 0, shoulder_angle, head_tilt
    return 1, shoulder_angle, head_tilt

def main():
    cap = cv2.VideoCapture(0)
    with mp_pose.Pose() as pose:
        last_score = None
        last_change_time = time.time()
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)
            score = None
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                score, shoulder_angle, head_tilt = compute_posture_score(results.pose_landmarks.landmark)
                cv2.putText(frame, f"Posture score: {score}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                cv2.putText(frame, f"Shoulder angle: {shoulder_angle:.1f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
                cv2.putText(frame, f"Head tilt: {head_tilt:.3f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
                # Detection of posture change
                if last_score is not None and score != last_score:
                    last_change_time = time.time()
                last_score = score
                # If bad posture > 7, display a reminder
                if score == 0 and (time.time() - last_change_time) > 7:
                    cv2.putText(frame, "Redresse-toi !", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,255), 3)
            cv2.imshow('Posture Detection', frame)
            if cv2.waitKey(5) & 0xFF == 27:
                break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
