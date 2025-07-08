#!/usr/bin/env python3
"""
Test script to verify Ollama integration
"""

from ollama_advisor import OllamaAdvisor
from pathlib import Path

def test_ollama_connection():
    """Basic test to verify Ollama connection"""
    print("Ollama Integration Test")
    print("=" * 40)
    
    # Create advisor with test file
    data_file = Path("../../data/daily.json")
    advisor = OllamaAdvisor(data_file)
    
    # Test 1: Ollama connection
    print("Testing Ollama connection...")
    is_available = advisor.is_ollama_available()
    if is_available:
        print("✓ Ollama is available")
    else:
        print("✗ Ollama not available")
        print("  Make sure Ollama is running: ollama serve")
        return False
    
    # Test 2: Simple call
    print("\nTesting simple call...")
    response = advisor.call_ollama("Say hello in English in one sentence.", max_tokens=50)
    if response:
        print(f"✓ Response received: {response}")
    else:
        print("✗ No response from Ollama")
        return False
    
    # Test 3: Data analysis (if available)
    print("\nTesting data analysis...")
    recent_data = advisor.load_recent_data(days=7)
    if recent_data:
        print(f"✓ {len(recent_data)} entries found in history")
        advice = advisor.analyze_startup_data()
        if advice:
            print("✓ Analysis successful")
        else:
            print("⚠ Analysis without advice (normal if little data)")
    else:
        print("ℹ No history data (normal for first test)")
    
    # Test 4: Posture score simulation
    print("\nTesting posture score simulation...")
    test_scores = [85, 78, 65, 45, 40, 38, 42]  # Declining scores
    for i, score in enumerate(test_scores):
        print(f"  Adding score {i+1}: {score}/100")
        advice = advisor.add_posture_score(score)
        if advice:
            print(f"  > Advice received: {advice}")
    
    print("\n✓ Test completed successfully!")
    return True

if __name__ == "__main__":
    test_ollama_connection()
