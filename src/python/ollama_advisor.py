#!/usr/bin/env python3
"""
Ollama Health Advisor - Intelligent advice based on local AI
"""

import json
import ollama
from datetime import datetime, timedelta
from pathlib import Path
import time

class OllamaAdvisor:
    def __init__(self, data_file_path, model_name="llama3:8b"):
        self.data_file = Path(data_file_path)
        self.model_name = model_name
        self.last_advice_time = 0
        self.advice_cooldown = 300  # 5 minutes minimum between advice
        self.last_posture_scores = []
        self.max_history = 10  # Keep last 10 scores
        
    def is_ollama_available(self):
        """Check if Ollama is available"""
        try:
            ollama.list()
            return True
        except:
            return False
    
    def call_ollama(self, prompt, max_tokens=200):
        """Call Ollama with a prompt"""
        if not self.is_ollama_available():
            return None
            
        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    'num_predict': max_tokens,
                    'temperature': 0.7
                }
            )
            return response['response'].strip()
        except Exception as e:
            print(f"Ollama error: {e}")
            return None
    
    def load_recent_data(self, days=7):
        """Load recent data"""
        try:
            if not self.data_file.exists():
                return []
            
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            checkpoints = data.get("checkpoints", [])
            
            # Filter recent data
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_data = []
            
            for checkpoint in checkpoints:
                try:
                    checkpoint_date = datetime.fromisoformat(checkpoint["timestamp"])
                    if checkpoint_date >= cutoff_date:
                        recent_data.append(checkpoint)
                except:
                    continue
            
            return recent_data
        except:
            return []
    
    def analyze_startup_data(self):
        """Analyze data at startup and give advice"""
        if not self.is_ollama_available():
            print("Ollama not available - AI advice disabled")
            return None
        
        print("Analyzing history...")
        
        recent_data = self.load_recent_data(days=7)
        if not recent_data:
            print("No history available.")
            return None
        
        # Prepare data summary
        total_entries = len(recent_data)
        avg_posture = sum(d.get("posture_score", 0) for d in recent_data) / total_entries
        avg_sleep = sum(d.get("sleep_hours", 0) for d in recent_data) / total_entries
        avg_hydration = sum(d.get("hydration_liters", 0) for d in recent_data) / total_entries
        
        # Posture trends
        posture_scores = [d.get("posture_score", 0) for d in recent_data[-5:]]
        posture_trend = "stable"
        if len(posture_scores) >= 3:
            if posture_scores[-1] > posture_scores[0]:
                posture_trend = "improving"
            elif posture_scores[-1] < posture_scores[0]:
                posture_trend = "declining"
        
        prompt = f"""You are a health coach. Analyze this data from the last 7 days and give 2-3 short advice:

Data:
- {total_entries} measurements over 7 days
- Average posture: {avg_posture:.1f}/100 (trend: {posture_trend})
- Average sleep: {avg_sleep:.1f}h/night
- Average hydration: {avg_hydration:.1f}L/day

Respond in English, be concrete and direct. Maximum 3 short sentences."""

        advice = self.call_ollama(prompt)
        if advice:
            print("\nAdvice based on your history:")
            print(f"{advice}")
        
        return advice
    
    def should_give_advice(self):
        """Check if advice should be given (cooldown)"""
        current_time = time.time()
        return (current_time - self.last_advice_time) >= self.advice_cooldown
    
    def add_posture_score(self, score):
        """Add posture score and analyze trend"""
        self.last_posture_scores.append(score)
        
        # Keep only recent scores
        if len(self.last_posture_scores) > self.max_history:
            self.last_posture_scores.pop(0)
        
        # Analyze if advice should be given
        if len(self.last_posture_scores) >= 5 and self.should_give_advice():
            return self.check_posture_trend()
        
        return None
    
    def check_posture_trend(self):
        """Check posture trend and give advice if needed"""
        if not self.is_ollama_available() or len(self.last_posture_scores) < 3:
            return None
        
        recent_scores = self.last_posture_scores[-5:]
        avg_recent = sum(recent_scores) / len(recent_scores)
        
        # Only give advice if posture is declining or poor
        if avg_recent < 60 or (len(recent_scores) >= 3 and recent_scores[-1] < recent_scores[0] - 10):
            
            trend_desc = "declining" if recent_scores[-1] < recent_scores[0] - 10 else "poor"
            
            prompt = f"""You are a posture coach. The user's posture shows {trend_desc} performance:
Recent scores: {recent_scores}
Recent average: {avg_recent:.1f}/100

Give ONE short advice to improve posture now. 1 sentence maximum, direct and actionable."""

            advice = self.call_ollama(prompt, max_tokens=80)
            if advice:
                self.last_advice_time = time.time()
                print(f"\nPosture advice: {advice}")
                return advice
        
        return None
    
    def give_closing_summary(self):
        """Give summary and advice at closing"""
        if not self.is_ollama_available():
            return None
        
        # Analyze current session
        session_scores = self.last_posture_scores
        if not session_scores:
            return None
        
        session_avg = sum(session_scores) / len(session_scores)
        session_min = min(session_scores)
        session_max = max(session_scores)
        
        # Load recent data for context
        recent_data = self.load_recent_data(days=3)
        recent_avg = 0
        if recent_data:
            recent_avg = sum(d.get("posture_score", 0) for d in recent_data) / len(recent_data)
        
        prompt = f"""You are a health coach giving a work session summary.

Current session:
- {len(session_scores)} measurements
- Average posture: {session_avg:.1f}/100
- Minimum: {session_min}/100, Maximum: {session_max}/100
- Last 3 days average: {recent_avg:.1f}/100

Give an encouraging summary in 2-3 sentences and 1-2 tips for tomorrow. Be direct and constructive."""

        advice = self.call_ollama(prompt, max_tokens=200)
        if advice:
            print(f"\nSession summary:")
            print(f"{advice}")
        
        return advice
    
    def give_bad_posture_advice(self, current_score):
        """Specific advice when posture is very bad"""
        if not self.is_ollama_available() or not self.should_give_advice():
            return None
        
        if current_score < 40:
            prompt = f"""The user has very bad posture (score: {current_score}/100). 
Give ONE immediate and actionable advice to correct it now. 1 short and direct sentence."""
            
            advice = self.call_ollama(prompt, max_tokens=60)
            if advice:
                self.last_advice_time = time.time()
                return advice
        
        return None
        