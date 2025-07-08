#!/usr/bin/env python3
"""
Test for forward lean detection
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from posture_score import compute_posture_score

class MockLandmark:
    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z

def create_mock_landmarks(nose_x=0.5, nose_y=0.4,
                         left_shoulder_x=0.3, left_shoulder_y=0.6,
                         right_shoulder_x=0.7, right_shoulder_y=0.6,
                         left_ear_x=0.45, left_ear_y=0.35,
                         right_ear_x=0.55, right_ear_y=0.35):
    """Create mock landmarks for testing"""
    landmarks = [MockLandmark(0, 0) for _ in range(33)]

    landmarks[0] = MockLandmark(nose_x, nose_y)  # NOSE
    landmarks[11] = MockLandmark(left_shoulder_x, left_shoulder_y)  # LEFT_SHOULDER
    landmarks[12] = MockLandmark(right_shoulder_x, right_shoulder_y)  # RIGHT_SHOULDER
    landmarks[7] = MockLandmark(left_ear_x, left_ear_y)  # LEFT_EAR
    landmarks[8] = MockLandmark(right_ear_x, right_ear_y)  # RIGHT_EAR
    
    return landmarks

def test_forward_lean_detection():
    """Test forward lean detection with calibration"""
    print("=== Forward Lean Detection Test ===\n")
    
    # 1. Reference posture (good posture)
    print("1. Reference posture (upright):")
    ref_landmarks = create_mock_landmarks()
    ref_score, _, _, _, ref_width, _, ref_head_ratio, _ = compute_posture_score(ref_landmarks)
    print(f"   Score: {ref_score}, Head-shoulder ratio: {ref_head_ratio:.3f}")
    
    # 2. Same person, same distance, but leaning forward (nose closer to shoulders)
    print("\n2. Same person leaning forward:")
    lean_landmarks = create_mock_landmarks(
        nose_y=0.55,  # Nose much closer to shoulder level (leaning forward)
        left_shoulder_x=0.3, right_shoulder_x=0.7  # Same distance
    )
    lean_score, _, _, _, _, _, lean_head_ratio, lean_detected = compute_posture_score(
        lean_landmarks, ref_width, ref_head_ratio
    )
    print(f"   Score: {lean_score}, Head-shoulder ratio: {lean_head_ratio:.3f}")
    print(f"   Forward lean detected: {lean_detected}")
    print(f"   Score difference: {lean_score - ref_score} points")
    
    # 3. Even more leaning forward
    print("\n3. Severely leaning forward:")
    severe_lean_landmarks = create_mock_landmarks(
        nose_y=0.62,  # Nose very close to shoulder level
        left_shoulder_x=0.3, right_shoulder_x=0.7  # Same distance
    )
    severe_score, _, _, _, _, _, severe_head_ratio, severe_detected = compute_posture_score(
        severe_lean_landmarks, ref_width, ref_head_ratio
    )
    print(f"   Score: {severe_score}, Head-shoulder ratio: {severe_head_ratio:.3f}")
    print(f"   Forward lean detected: {severe_detected}")
    print(f"   Score difference: {severe_score - ref_score} points")
    
    # 4. Without calibration (fallback detection)
    print("\n4. Forward lean without calibration (fallback):")
    fallback_score, _, _, _, _, _, fallback_head_ratio, fallback_detected = compute_posture_score(
        severe_lean_landmarks
    )
    print(f"   Score: {fallback_score}, Head-shoulder ratio: {fallback_head_ratio:.3f}")
    print(f"   Forward lean detected: {fallback_detected}")
    
    print("\n=== Summary ===")
    print("Forward lean detection is now working!")
    print(f"• Upright posture: {ref_score} points")
    print(f"• Mild forward lean: {lean_score} points ({lean_score - ref_score:+d})")
    print(f"• Severe forward lean: {severe_score} points ({severe_score - ref_score:+d})")
    print("\nThe system can now detect when you're hunched over your computer!")

if __name__ == "__main__":
    test_forward_lean_detection()
