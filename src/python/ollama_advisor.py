#!/usr/bin/env python3
"""
Ollama Health Advisor - Conseils intelligents basés sur l'IA locale
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
        self.advice_cooldown = 300  # 5 minutes minimum entre conseils
        self.last_posture_scores = []
        self.max_history = 10  # Garder les 10 derniers scores
        
    def is_ollama_available(self):
        """Vérifier si Ollama est disponible"""
        try:
            ollama.list()
            return True
        except:
            return False
    
    def call_ollama(self, prompt, max_tokens=200):
        """Appeler Ollama avec un prompt"""
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
            print(f"Erreur Ollama: {e}")
            return None
    
    def load_recent_data(self, days=7):
        """Charger les données récentes"""
        try:
            if not self.data_file.exists():
                return []
            
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            checkpoints = data.get("checkpoints", [])
            
            # Filtrer les données récentes
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
        """Analyser les données au démarrage et donner des conseils"""
        if not self.is_ollama_available():
            print("Ollama non disponible - conseils IA désactivés")
            return None
        
        print("Analyse de l'historique...")
        
        recent_data = self.load_recent_data(days=7)
        if not recent_data:
            print("Pas d'historique disponible.")
            return None
        
        # Préparer le résumé des données
        total_entries = len(recent_data)
        avg_posture = sum(d.get("posture_score", 0) for d in recent_data) / total_entries
        avg_sleep = sum(d.get("sleep_hours", 0) for d in recent_data) / total_entries
        avg_hydration = sum(d.get("hydration_liters", 0) for d in recent_data) / total_entries
        
        # Tendances posture
        posture_scores = [d.get("posture_score", 0) for d in recent_data[-5:]]
        posture_trend = "stable"
        if len(posture_scores) >= 3:
            if posture_scores[-1] > posture_scores[0]:
                posture_trend = "amélioration"
            elif posture_scores[-1] < posture_scores[0]:
                posture_trend = "dégradation"
        
        prompt = f"""Tu es un coach santé. Analyse ces données des 7 derniers jours et donne 2-3 conseils courts:

Données:
- {total_entries} mesures sur 7 jours
- Posture moyenne: {avg_posture:.1f}/100 (tendance: {posture_trend})
- Sommeil moyen: {avg_sleep:.1f}h/nuit
- Hydratation moyenne: {avg_hydration:.1f}L/jour

Réponds en français, sois concret et direct. Maximum 3 phrases courtes."""

        advice = self.call_ollama(prompt)
        if advice:
            print("\nConseils basés sur votre historique:")
            print(f"{advice}")
        
        return advice
    
    def should_give_advice(self):
        """Vérifier s'il faut donner un conseil (cooldown)"""
        current_time = time.time()
        return (current_time - self.last_advice_time) >= self.advice_cooldown
    
    def add_posture_score(self, score):
        """Ajouter un score de posture et analyser la tendance"""
        self.last_posture_scores.append(score)
        
        # Garder seulement les derniers scores
        if len(self.last_posture_scores) > self.max_history:
            self.last_posture_scores.pop(0)
        
        # Analyser si on doit donner un conseil
        if len(self.last_posture_scores) >= 5 and self.should_give_advice():
            return self.check_posture_trend()
        
        return None
    
    def check_posture_trend(self):
        """Vérifier la tendance de posture et donner des conseils si nécessaire"""
        if not self.is_ollama_available() or len(self.last_posture_scores) < 3:
            return None
        
        recent_scores = self.last_posture_scores[-5:]
        avg_recent = sum(recent_scores) / len(recent_scores)
        
        # Seulement donner conseil si posture se dégrade ou est mauvaise
        if avg_recent < 60 or (len(recent_scores) >= 3 and recent_scores[-1] < recent_scores[0] - 10):
            
            trend_desc = "dégradation" if recent_scores[-1] < recent_scores[0] - 10 else "faible"
            
            prompt = f"""Tu es un coach posture. La posture de l'utilisateur montre une {trend_desc}:
Scores récents: {recent_scores}
Moyenne récente: {avg_recent:.1f}/100

Donne UN conseil court pour améliorer la posture maintenant. 1 phrase maximum, direct et actionnable."""

            advice = self.call_ollama(prompt, max_tokens=80)
            if advice:
                self.last_advice_time = time.time()
                print(f"\nConseil posture: {advice}")
                return advice
        
        return None
    
    def give_closing_summary(self):
        """Donner un résumé et des conseils à la fermeture"""
        if not self.is_ollama_available():
            return None
        
        # Analyser la session actuelle
        session_scores = self.last_posture_scores
        if not session_scores:
            return None
        
        session_avg = sum(session_scores) / len(session_scores)
        session_min = min(session_scores)
        session_max = max(session_scores)
        
        # Charger données récentes pour contexte
        recent_data = self.load_recent_data(days=3)
        recent_avg = 0
        if recent_data:
            recent_avg = sum(d.get("posture_score", 0) for d in recent_data) / len(recent_data)
        
        prompt = f"""Tu es un coach santé qui fait le bilan de la session de travail.

Session actuelle:
- {len(session_scores)} mesures
- Posture moyenne: {session_avg:.1f}/100
- Minimum: {session_min}/100, Maximum: {session_max}/100
- Moyenne des 3 derniers jours: {recent_avg:.1f}/100

Fais un bilan encourageant en 2-3 phrases et donne 1-2 conseils pour demain. Sois direct et constructif."""

        advice = self.call_ollama(prompt, max_tokens=200)
        if advice:
            print(f"\nBilan de session:")
            print(f"{advice}")
        
        return advice
    
    def give_bad_posture_advice(self, current_score):
        """Conseil spécifique quand la posture est mauvaise"""
        if not self.is_ollama_available() or not self.should_give_advice():
            return None
        
        if current_score < 40:
            prompt = f"""L'utilisateur a une très mauvaise posture (score: {current_score}/100). 
Donne UN conseil immédiat et actionnable pour corriger maintenant. 1 phrase courte et directe."""
            
            advice = self.call_ollama(prompt, max_tokens=60)
            if advice:
                self.last_advice_time = time.time()
                return advice
        
        return None
        