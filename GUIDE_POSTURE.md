# Guide d'utilisation - Détection de Posture

## 🎯 Objectif
Ce système de détection de posture vous aide à maintenir une bonne posture pendant que vous travaillez sur votre ordinateur. Il utilise l'intelligence artificielle pour détecter votre position et vous alerter en cas de mauvaise posture.

## 🚀 Installation et Démarrage

### 1. Installation des dépendances
```bash
pip install -r requirements.txt
```

### 2. Lancement de l'application
```bash
python src/python/posture_score.py
```

## 🛠️ Utilisation

### Première utilisation - Calibration
1. **Installez-vous confortablement** devant votre ordinateur dans votre position de travail habituelle
2. **Lancez l'application** - une fenêtre s'ouvre avec votre caméra
3. **Appuyez sur 'c'** pour commencer la calibration
4. **Restez immobile** pendant 2-3 secondes pendant que le système apprend votre position de référence
5. **Calibration terminée !** - Le système s'adapte maintenant à votre morphologie

### Contrôles
- **'c'** : Démarrer la calibration
- **'r'** : Réinitialiser la calibration
- **'q'** ou **ESC** : Quitter l'application

## 📊 Métriques affichées

### Score de posture (0-100)
- **🟢 70-100** : Excellente posture
- **🟡 50-69** : Posture correcte mais perfectible
- **🔴 0-49** : Mauvaise posture - correction nécessaire

### Indicateurs détaillés
- **Shoulder diff** : Différence de hauteur entre les épaules
- **Head forward** : Position de la tête par rapport aux épaules
- **Ear diff** : Inclinaison latérale de la tête
- **Shoulder width** : Largeur des épaules (indicateur de distance)
- **Distance** : TROP PROCHE / OK / TROP LOIN

## 🔔 Alertes

### Alerte "Redresse-toi !"
- S'affiche après **3 secondes** de mauvaise posture (score < 50)
- Disparaît automatiquement quand vous corrigez votre position

## 🎯 Ce que le système détecte

### ✅ Problèmes de posture détectés
1. **Épaules inclinées** - Une épaule plus haute que l'autre
2. **Tête trop en avant** - Tête penchée vers l'écran
3. **Inclinaison latérale** - Tête penchée sur le côté
4. **Distance inadéquate** - Trop proche ou trop loin de l'écran

### 🎯 Recommandations pour une bonne posture
- **Épaules droites** et détendues
- **Tête droite** alignée avec la colonne vertébrale
- **Distance appropriée** de l'écran (bras tendu)
- **Dos droit** contre le dossier de la chaise

## 🔧 Personnalisation

### Ajustement des seuils
Si vous trouvez que les alertes sont trop sensibles ou pas assez, vous pouvez modifier les seuils dans le fichier `posture_score.py` :

```python
# Ligne ~95 - Seuil d'alerte
if score < 50:  # Changez cette valeur (30-70)

# Ligne ~97 - Délai avant alerte
elif current_time - bad_posture_start_time > 3:  # Changez cette valeur (1-10 secondes)
```

## 🎪 Tips et astuces

### Pour une calibration optimale
- Utilisez un éclairage uniforme
- Évitez les contre-jours
- Assurez-vous que vos épaules sont bien visibles
- Maintenez une position naturelle et confortable

### Pour de meilleurs résultats
- **Calibrez régulièrement** si vous changez de position de travail
- **Portez des vêtements contrastés** pour une meilleure détection
- **Gardez votre espace de travail dégagé** derrière vous

## 🚨 Dépannage

### Problèmes courants
- **"Aucune posture détectée"** : Vérifiez votre éclairage et votre position face à la caméra
- **Score toujours à 0** : Effectuez une nouvelle calibration
- **Alertes trop fréquentes** : Recalibrez ou ajustez les seuils

### Performance
- **Fermer autres applications** utilisant la caméra
- **Vérifier les permissions** d'accès à la caméra
- **Redémarrer l'application** en cas de problème

## 📈 Intégration avec Equilibri

Ce module fait partie du système **Equilibri** - une application complète de suivi de la santé au travail. Les données de posture peuvent être intégrées avec d'autres métriques de santé pour un suivi global de votre bien-être.

---

*Developed for Raise Your Hack - Qualcomm Track*
*Edge AI Consumer Utility Application*
