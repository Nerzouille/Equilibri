import cv2
import mediapipe as mp
import time
import math

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def compute_posture_score(landmarks, reference_shoulder_width=None):
    """
    Score of posture based on realistic criteria:
    - Shoulder alignment (left/right tilt)
    - Head position relative to the shoulders (up/down)
    - Lateral head tilt
    - Distance front/back (based on the width of the shoulders and the position of the nose)
    Returns a score between 0 and 100.
    """
    nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    left_ear = landmarks[mp_pose.PoseLandmark.LEFT_EAR.value]
    right_ear = landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value]

    # 1. Shoulder alignment (should be to the same height)
    shoulder_diff = abs(left_shoulder.y - right_shoulder.y)

    # 2. Head forward position (vertical position of the nose relative to the shoulders)
    shoulder_mid_y = (left_shoulder.y + right_shoulder.y) / 2
    head_forward_ratio = (nose.y - shoulder_mid_y)

    # 3. Head lateral tilt (difference in height of the ears)
    ear_diff = abs(left_ear.y - right_ear.y)

    # 4. Distance front/back (based on the width of the shoulders)
    shoulder_width = abs(right_shoulder.x - left_shoulder.x)

    # If we have a reference, use adaptive thresholds
    if reference_shoulder_width is not None:
        # Tolerance of ±20% compared to the reference
        min_good_width = reference_shoulder_width * 0.8
        max_good_width = reference_shoulder_width * 1.2

        # Ratio compared to the reference
        width_ratio = shoulder_width / reference_shoulder_width
        distance_status = "OK"
        if width_ratio > 1.2:
            distance_status = "TOO CLOSE"
        elif width_ratio < 0.8:
            distance_status = "TOO FAR"
    else:
        # Default values if no calibration
        min_good_width = 0.22
        max_good_width = 0.45
        distance_status = "OK" if min_good_width <= shoulder_width <= max_good_width else ("TOO FAR" if shoulder_width < min_good_width else "TOO CLOSE")

    # Calculate score (starts at 100)
    score = 100

    # Penalize the shoulder tilt
    if shoulder_diff > 0.03:  # Tolerance threshold
        penalty = min(40, (shoulder_diff - 0.03) * 1000)
        score -= penalty

    # Penalize the head too forward (the nose should be above the shoulders)
    if head_forward_ratio > -0.02:
        penalty = min(40, (head_forward_ratio + 0.02) * 800)
        score -= penalty

    # Penalize the lateral head tilt
    if ear_diff > 0.05:  # More sensitive threshold for lateral head tilt
        penalty = min(30, (ear_diff - 0.05) * 300)
        score -= penalty

    # Penalize the incorrect distance (adaptive if we have a reference)
    # Distance is a critical factor for good posture
    if shoulder_width < min_good_width:
        # Too close = more penalty as it's bad for eyes and posture
        distance_penalty = min(45, (min_good_width - shoulder_width) * 500)
        score -= distance_penalty

    if shoulder_width > max_good_width:
        # Too far = less penalty but still problematic
        distance_penalty = min(25, (shoulder_width - max_good_width) * 200)
        score -= distance_penalty

    # Bonus for perfect distance (in the ideal zone)
    if reference_shoulder_width is not None:
        # Calculate how close we are to the reference
        width_ratio = shoulder_width / reference_shoulder_width
        if 0.95 <= width_ratio <= 1.05:  # Within 5% of reference
            score += 5  # Small bonus for perfect distance
        elif 0.9 <= width_ratio <= 1.1:  # Within 10% of reference
            score += 2  # Small bonus for good distance

    # Ensure the score is between 0 and 100
    score = max(0, min(100, int(score)))

    return score, shoulder_diff, head_forward_ratio, ear_diff, shoulder_width, distance_status

def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Impossible to open the camera")
        return

    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as pose:
        bad_posture_start_time = None
        warning_displayed = False
        reference_shoulder_width = None
        calibration_mode = False
        calibration_samples = []

        print("=== Posture Detection ===")
        print("Press 'c' to calibrate your reference distance")
        print("Press 'r' to reset the calibration")
        print("Press 'q' or ESC to quit")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Flip the frame horizontally for a mirror view
            frame = cv2.flip(frame, 1)

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)

            current_time = time.time()

            if results.pose_landmarks:
                # Draw pose landmarks
                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
                )

                # Calculate posture score
                score, shoulder_diff, head_forward_ratio, ear_diff, shoulder_width, distance_status = compute_posture_score(
                    results.pose_landmarks.landmark, reference_shoulder_width
                )

                # Calibration mode
                if calibration_mode:
                    calibration_samples.append(shoulder_width)
                    cv2.rectangle(frame, (10, 10), (600, 70), (0, 255, 255), -1)
                    cv2.putText(frame, f"CALIBRATION... {len(calibration_samples)}/30", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
                    cv2.putText(frame, "Stay in a comfortable position", (20, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

                    if len(calibration_samples) >= 30:
                        reference_shoulder_width = sum(calibration_samples) / len(calibration_samples)
                        calibration_mode = False
                        calibration_samples = []
                        print(f"Calibration completed! Reference distance: {reference_shoulder_width:.3f}")

                # Display current metrics
                color = (0, 255, 0) if score >= 70 else (0, 165, 255) if score >= 50 else (0, 0, 255)
                cv2.putText(frame, f"Posture score: {score}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                cv2.putText(frame, f"Shoulder diff: {shoulder_diff:.3f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                cv2.putText(frame, f"Head forward: {head_forward_ratio:.3f}", (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                cv2.putText(frame, f"Ear diff: {ear_diff:.3f}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                cv2.putText(frame, f"Shoulder width: {shoulder_width:.3f}", (10, 135), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

                # Visual indicators for depth detection
                depth_color = (0, 255, 0) if distance_status == "OK" else (0, 0, 255)
                cv2.putText(frame, f"Distance: {distance_status}", (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.6, depth_color, 2)

                # Display the calibration status
                if reference_shoulder_width is not None:
                    cv2.putText(frame, f"Ref: {reference_shoulder_width:.3f}", (10, 185), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                else:
                    cv2.putText(frame, "Not calibrated - Press 'c'", (10, 185), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

                # Posture warning logic
                if score < 50:  # Bad posture threshold
                    if bad_posture_start_time is None:
                        bad_posture_start_time = current_time
                    elif current_time - bad_posture_start_time > 3:  # 3 seconds of bad posture
                        warning_displayed = True
                else:  # Good posture
                    bad_posture_start_time = None
                    warning_displayed = False

                # Display warning if needed
                if warning_displayed and not calibration_mode:
                    cv2.rectangle(frame, (10, 210), (500, 260), (0, 0, 255), -1)
                    cv2.putText(frame, "Straighten up!", (20, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)

            else:
                # No pose detected
                cv2.putText(frame, "No posture detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                bad_posture_start_time = None
                warning_displayed = False

            cv2.imshow('Posture Detection', frame)

            # Handle key presses
            key = cv2.waitKey(5) & 0xFF
            if key == 27 or key == ord('q'):  # ESC or 'q' to quit
                break
            elif key == ord('c'):  # 'c' to calibrate
                if not calibration_mode:
                    calibration_mode = True
                    calibration_samples = []
                    print("Calibration started! Stay in a comfortable position...")
            elif key == ord('r'):  # 'r' to reset calibration
                reference_shoulder_width = None
                calibration_mode = False
                calibration_samples = []
                print("Calibration reset!")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
