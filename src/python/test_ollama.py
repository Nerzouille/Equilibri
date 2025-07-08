#!/usr/bin/env python3
"""
Test script pour vérifier l'intégration Ollama
"""

from ollama_advisor import OllamaAdvisor
from pathlib import Path

def test_ollama_connection():
    """Test de base pour vérifier la connexion Ollama"""
    print("Test de l'intégration Ollama")
    print("=" * 40)
    
    # Créer advisor avec un fichier de test
    data_file = Path("../../data/daily.json")
    advisor = OllamaAdvisor(data_file)
    
    # Test 1: Connexion Ollama
    print("Test connexion Ollama...")
    is_available = advisor.is_ollama_available()
    if is_available:
        print("✓ Ollama est disponible")
    else:
        print("✗ Ollama non disponible")
        print("  Assurez-vous qu'Ollama est démarré: ollama serve")
        return False
    
    # Test 2: Appel simple
    print("\nTest appel simple...")
    response = advisor.call_ollama("Dis bonjour en français en une phrase.", max_tokens=50)
    if response:
        print(f"✓ Réponse reçue: {response}")
    else:
        print("✗ Pas de réponse d'Ollama")
        return False
    
    # Test 3: Analyse des données (si disponibles)
    print("\nTest analyse des données...")
    recent_data = advisor.load_recent_data(days=7)
    if recent_data:
        print(f"✓ {len(recent_data)} entrées trouvées dans l'historique")
        advice = advisor.analyze_startup_data()
        if advice:
            print("✓ Analyse réussie")
        else:
            print("⚠ Analyse sans conseil (normal si peu de données)")
    else:
        print("ℹ Pas de données d'historique (normal pour un premier test)")
    
    # Test 4: Simulation scores de posture
    print("\nTest simulation scores posture...")
    test_scores = [85, 78, 65, 45, 40, 38, 42]  # Scores en dégradation
    for i, score in enumerate(test_scores):
        print(f"  Ajout score {i+1}: {score}/100")
        advice = advisor.add_posture_score(score)
        if advice:
            print(f"  > Conseil reçu: {advice}")
    
    print("\n✓ Test terminé avec succès!")
    return True

if __name__ == "__main__":
    test_ollama_connection() 