import cv2
import mediapipe as mp
import time

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

def compute_posture_score(landmarks, reference_shoulder_width=None, reference_head_shoulder_ratio=None):
    """
    Score of posture based on realistic criteria:
    - Shoulder alignment (left/right tilt)
    - Head position relative to the shoulders (up/down)
    - Lateral head tilt
    - Distance front/back (based on the width of the shoulders)
    - Forward lean detection (head-shoulder height ratio)
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

    # 3. Head-shoulder height ratio (for detecting forward lean)
    # When leaning forward, the head appears lower relative to shoulders
    head_shoulder_height_ratio = abs(nose.y - shoulder_mid_y)

    # 4. Head lateral tilt (difference in height of the ears)
    ear_diff = abs(left_ear.y - right_ear.y)

    # 5. Distance front/back (based on the width of the shoulders)
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

    # Check for forward lean using head-shoulder height ratio
    forward_lean_detected = False
    if reference_head_shoulder_ratio is not None:
        # When leaning forward, the head moves CLOSER to shoulders, so ratio DECREASES
        lean_threshold = reference_head_shoulder_ratio * 0.7  # 30% decrease indicates forward lean
        if head_shoulder_height_ratio < lean_threshold:
            forward_lean_detected = True
    else:
        # Fallback: if head is very close to shoulders without calibration
        if head_shoulder_height_ratio < 0.15:  # Low ratio = head very close to shoulders
            forward_lean_detected = True

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

    # Penalize the lateral head tilt (much stronger penalty)
    if ear_diff > 0.04:  # Increased sensitivity for lateral head tilt
        penalty = min(50, (ear_diff - 0.04) * 800)  # Stronger scaling and higher max penalty
        score -= penalty

    # Penalize forward lean (hunched posture)
    if forward_lean_detected:
        if reference_head_shoulder_ratio is not None:
            # Calculate penalty based on how much closer the head is to shoulders
            deviation = reference_head_shoulder_ratio - head_shoulder_height_ratio
            penalty = min(40, deviation * 300)  # Strong penalty for leaning forward
            score -= penalty
        else:
            # Fallback penalty without calibration
            penalty = min(30, (0.15 - head_shoulder_height_ratio) * 200)
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

    return score, shoulder_diff, head_forward_ratio, ear_diff, shoulder_width, distance_status, head_shoulder_height_ratio, forward_lean_detected

def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Cannot open camera")
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
        reference_head_shoulder_ratio = None
        calibration_mode = False
        calibration_samples = []
        calibration_head_samples = []

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
                score, shoulder_diff, head_forward_ratio, ear_diff, shoulder_width, distance_status, head_shoulder_height_ratio, forward_lean_detected = compute_posture_score(
                    results.pose_landmarks.landmark, reference_shoulder_width, reference_head_shoulder_ratio
                )

                # Calibration mode
                if calibration_mode:
                    calibration_samples.append(shoulder_width)
                    calibration_head_samples.append(head_shoulder_height_ratio)
                    cv2.rectangle(frame, (10, 10), (600, 70), (0, 255, 255), -1)
                    cv2.putText(frame, f"CALIBRATION... {len(calibration_samples)}/30", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
                    cv2.putText(frame, "Stay in a comfortable position", (20, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

                    if len(calibration_samples) >= 30:
                        reference_shoulder_width = sum(calibration_samples) / len(calibration_samples)
                        reference_head_shoulder_ratio = sum(calibration_head_samples) / len(calibration_head_samples)
                        calibration_mode = False
                        calibration_samples = []
                        calibration_head_samples = []
                        print(f"Calibration completed! Reference distance: {reference_shoulder_width:.3f}, Head-shoulder ratio: {reference_head_shoulder_ratio:.3f}")

                # Display current metrics
                color = (0, 255, 0) if score >= 70 else (0, 165, 255) if score >= 50 else (0, 0, 255)

                # Show posture warnings
                if score < 50:
                    if bad_posture_start_time is None:
                        bad_posture_start_time = current_time
                    
                    elapsed = current_time - bad_posture_start_time
                    
                    # Show warning after 30 seconds of bad posture
                    if elapsed >= 30 and not warning_displayed:
                        print(f"Warning: Bad posture detected for {elapsed:.0f} seconds!")
                        warning_displayed = True
                    
                    # Show alert every 60 seconds
                    if elapsed >= 60 and int(elapsed) % 60 == 0:
                        print(f"Alert: Fix your posture! Bad posture for {elapsed:.0f} seconds")
                
                else:
                    # Reset timer for good posture
                    if bad_posture_start_time is not None:
                        duration = current_time - bad_posture_start_time
                        if duration >= 30:
                            print(f"Good posture restored after {duration:.0f} seconds")
                        bad_posture_start_time = None
                        warning_displayed = False

                # Draw info box
                cv2.rectangle(frame, (10, frame.shape[0] - 180), (500, frame.shape[0] - 10), (0, 0, 0), -1)
                
                info_text = [
                    f"Posture Score: {score}/100",
                    f"Shoulder Diff: {shoulder_diff:.3f}",
                    f"Head Forward: {head_forward_ratio:.3f}",
                    f"Lateral Tilt: {ear_diff:.3f}",
                    f"Distance: {distance_status} ({shoulder_width:.3f})",
                    f"Forward Lean: {'YES' if forward_lean_detected else 'NO'}"
                ]
                
                for i, text in enumerate(info_text):
                    cv2.putText(frame, text, (20, frame.shape[0] - 160 + i * 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

                # Show status message based on score
                if score >= 80:
                    status_msg = "Excellent posture!"
                elif score >= 70:
                    status_msg = "Good posture"
                elif score >= 50:
                    status_msg = "Correct your posture"
                else:
                    status_msg = "BAD POSTURE - URGENT"
                
                cv2.putText(frame, status_msg, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 2)

            cv2.imshow('Posture Analysis', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # ESC
                break
            elif key == ord('c') and results.pose_landmarks:
                calibration_mode = True
                calibration_samples = []
                calibration_head_samples = []
                print("Calibration started! Stay in a comfortable position for 30 measurements...")
            elif key == ord('r'):
                reference_shoulder_width = None
                reference_head_shoulder_ratio = None
                calibration_mode = False
                print("Calibration reset!")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
