#!/usr/bin/env python3
"""
Demo script to show how distance affects posture score
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from posture_score import compute_posture_score
import numpy as np

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

    # Set specific landmarks we use
    landmarks[0] = MockLandmark(nose_x, nose_y)  # NOSE
    landmarks[11] = MockLandmark(left_shoulder_x, left_shoulder_y)  # LEFT_SHOULDER
    landmarks[12] = MockLandmark(right_shoulder_x, right_shoulder_y)  # RIGHT_SHOULDER
    landmarks[7] = MockLandmark(left_ear_x, left_ear_y)  # LEFT_EAR
    landmarks[8] = MockLandmark(right_ear_x, right_ear_y)  # RIGHT_EAR
    
    return landmarks

def demo_distance_impact():
    """Demonstrate how distance affects posture score"""
    print("=== Distance Impact on Posture Score Demo ===\n")
    
    # Perfect posture at reference distance
    print("1. Perfect posture at reference distance:")
    reference_landmarks = create_mock_landmarks()
    ref_score, _, _, _, ref_width, _ = compute_posture_score(reference_landmarks)
    calibrated_score, _, _, _, _, ref_status = compute_posture_score(reference_landmarks, ref_width)
    print(f"   Without calibration: Score = {ref_score}, Width = {ref_width:.3f}")
    print(f"   With calibration: Score = {calibrated_score}, Status = {ref_status}")
    print()
    
    # Same posture but closer to screen
    print("2. Same posture but TOO CLOSE to screen:")
    close_landmarks = create_mock_landmarks(left_shoulder_x=0.4, right_shoulder_x=0.6)
    close_score, _, _, _, close_width, close_status = compute_posture_score(close_landmarks, ref_width)
    print(f"   Score = {close_score}, Width = {close_width:.3f}, Status = {close_status}")
    print(f"   Score impact: {close_score - calibrated_score} points")
    print()
    
    # Same posture but farther from screen
    print("3. Same posture but TOO FAR from screen:")
    far_landmarks = create_mock_landmarks(left_shoulder_x=0.2, right_shoulder_x=0.8)
    far_score, _, _, _, far_width, far_status = compute_posture_score(far_landmarks, ref_width)
    print(f"   Score = {far_score}, Width = {far_width:.3f}, Status = {far_status}")
    print(f"   Score impact: {far_score - calibrated_score} points")
    print()
    
    # Perfect distance bonus
    print("4. Perfect distance (within 5% of reference):")
    perfect_landmarks = create_mock_landmarks(left_shoulder_x=0.305, right_shoulder_x=0.695)  # Very close to reference
    perfect_score, _, _, _, perfect_width, perfect_status = compute_posture_score(perfect_landmarks, ref_width)
    print(f"   Score = {perfect_score}, Width = {perfect_width:.3f}, Status = {perfect_status}")
    print(f"   Score impact: {perfect_score - calibrated_score} points (bonus for perfect distance)")
    print()
    
    print("=== Summary ===")
    print("The distance from the screen significantly impacts your posture score:")
    print(f"• Perfect distance: {calibrated_score} points (baseline)")
    print(f"• Too close: {close_score} points ({close_score - calibrated_score:+d} points)")
    print(f"• Too far: {far_score} points ({far_score - calibrated_score:+d} points)")
    print(f"• Perfect distance bonus: {perfect_score} points ({perfect_score - calibrated_score:+d} points)")
    print()
    print("💡 Tip: Use the calibration feature ('c' key) to set your optimal working distance!")

if __name__ == "__main__":
    demo_distance_impact()
