import cv2
import mediapipe as mp
import time
import math

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def compute_posture_score_debug(landmarks):
    """Version debug avec plus d'informations"""
    nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    left_ear = landmarks[mp_pose.PoseLandmark.LEFT_EAR.value]
    right_ear = landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value]

    print(f"Nose: ({nose.x:.3f}, {nose.y:.3f})")
    print(f"Left shoulder: ({left_shoulder.x:.3f}, {left_shoulder.y:.3f})")
    print(f"Right shoulder: ({right_shoulder.x:.3f}, {right_shoulder.y:.3f})")

    # 1. Shoulder alignment
    shoulder_diff = abs(left_shoulder.y - right_shoulder.y)
    print(f"Shoulder diff: {shoulder_diff:.3f}")

    # 2. Head forward position
    shoulder_mid_y = (left_shoulder.y + right_shoulder.y) / 2
    head_forward_ratio = (nose.y - shoulder_mid_y)
    print(f"Head forward ratio: {head_forward_ratio:.3f}")

    # 3. Head lateral tilt
    ear_diff = abs(left_ear.y - right_ear.y)
    print(f"Ear diff: {ear_diff:.3f}")

    # Calculate score
    score = 100
    print(f"Starting score: {score}")

    # Penalize shoulder misalignment
    if shoulder_diff > 0.03:
        penalty = min(40, (shoulder_diff - 0.03) * 1000)
        score -= penalty
        print(f"Shoulder penalty: {penalty:.1f}, new score: {score}")

    # Penalize head too far forward
    if head_forward_ratio > -0.02:
        penalty = min(40, (head_forward_ratio + 0.02) * 800)
        score -= penalty
        print(f"Head forward penalty: {penalty:.1f}, new score: {score}")

    # Penalize head tilt
    if ear_diff > 0.02:
        penalty = min(20, (ear_diff - 0.02) * 500)
        score -= penalty
        print(f"Ear penalty: {penalty:.1f}, new score: {score}")

    final_score = max(0, min(100, int(score)))
    print(f"Final score: {final_score}")
    print("-" * 50)

    return final_score, shoulder_diff, head_forward_ratio, ear_diff

def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Erreur: Impossible d'ouvrir la caméra")
        return

    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as pose:

        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # Flip the frame horizontally
            frame = cv2.flip(frame, 1)

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)

            if results.pose_landmarks:
                # Draw pose landmarks
                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )

                # Calculate posture score every 30 frames (1 second at 30fps)
                if frame_count % 30 == 0:
                    print(f"\n=== Frame {frame_count} ===")
                    score, shoulder_diff, head_forward_ratio, ear_diff = compute_posture_score_debug(results.pose_landmarks.landmark)

                    # Simple score calculation for display
                    simple_score = 100
                    if shoulder_diff > 0.03:
                        simple_score -= 30
                    if head_forward_ratio > -0.02:
                        simple_score -= 30
                    if ear_diff > 0.02:
                        simple_score -= 20

                    print(f"Simple score calculation: {simple_score}")

                # Display score on frame
                cv2.putText(frame, f"Score: calculating...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, f"Frame: {frame_count}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

            else:
                cv2.putText(frame, "Aucune posture détectée", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            cv2.imshow('Posture Debug', frame)

            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
