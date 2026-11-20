# 📝 Rapport — Projet C : Détection d'Objets avec YOLOv8

**Master 2 - Deep Learning**  
**By DRISS Amine**  
**Date : 07/04/2026**

---

## 1️⃣ Qu'est-ce que l'IoU ? Expliquez avec un exemple numérique.

### Définition
L'**IoU (Intersection over Union)** est une métrique fondamentale en détection d'objets qui mesure le chevauchement entre une boîte englobante prédite par le modèle et la boîte de vérité terrain (ground truth). Elle quantifie la précision de la localisation.

### Formule
```
IoU = Aire(Intersection) / Aire(Union)
    = Aire(Bbox_pred ∩ Bbox_gt) / Aire(Bbox_pred ∪ Bbox_gt)
```

### Exemple numérique détaillé

**Boîte vérité terrain (ground truth)** : `[1, 1, 5, 5]`
- Coordonnées : (x1=1, y1=1, x2=5, y2=5)
- Aire = (5-1) × (5-1) = **16 unités²**

**Boîte prédite** : `[1.5, 1.5, 5.5, 5.5]`
- Coordonnées : (x1=1.5, y1=1.5, x2=5.5, y2=5.5)
- Aire = (5.5-1.5) × (5.5-1.5) = **16 unités²**

**Intersection** :
- x1_intersection = max(1, 1.5) = 1.5
- y1_intersection = max(1, 1.5) = 1.5
- x2_intersection = min(5, 5.5) = 5
- y2_intersection = min(5, 5.5) = 5
- Aire_intersection = (5-1.5) × (5-1.5) = 3.5 × 3.5 = **12.25 unités²**

**Union** :
- Aire_union = Aire_gt + Aire_pred - Aire_intersection
- Aire_union = 16 + 16 - 12.25 = **19.75 unités²**

**IoU** :
- IoU = 12.25 / 19.75 ≈ **0.620**

### Interprétation
- **IoU = 1** : Prédiction parfaite (superposition totale)
- **IoU > 0.5** : Détection considérée comme correcte (seuil courant)
- **IoU < 0.5** : Détection incorrecte
- **IoU = 0** : Aucun chevauchement

Dans notre exemple, **IoU ≈ 0.620 > 0.5** → la détection est **correcte** ✅

---

## 2️⃣ Quelle est la différence entre precision et recall ? Comment le seuil de confiance joue-t-il sur ce compromis ?

### Définitions

#### Precision (Précision)
```
Precision = Vrais Positifs (VP) / (Vrais Positifs + Faux Positifs)
          = VP / (VP + FP)
```
**Question répondue** : *"Parmi tous les objets détectés, quelle proportion est correcte ?"*

- **Haute precision** → Peu de faux positifs (détections fiables)
- **Basse precision** → Beaucoup de fausses alarmes

#### Recall (Rappel)
```
Recall = Vrais Positifs (VP) / (Vrais Positifs + Faux Négatifs)
       = VP / (VP + FN)
```
**Question répondue** : *"Parmi tous les objets réels présents, quelle proportion a été détectée ?"*

- **Haut recall** → Peu d'objets manqués
- **Bas recall** → Beaucoup d'objets non détectés

### Exemple concret
Sur une image contenant **10 voitures réelles** :
- Le modèle détecte **8 voitures**
- Parmi ces 8 détections, **6 sont correctes** (vraies voitures) et **2 sont fausses** (faux positifs)
- Il reste **4 voitures non détectées** (faux négatifs)

Calculs :
- **Precision** = 6 / (6 + 2) = 6/8 = **0.75 (75%)**
- **Recall** = 6 / (6 + 4) = 6/10 = **0.60 (60%)**

### Impact du seuil de confiance

Le **seuil de confiance** (confidence threshold) est la probabilité minimale requise pour qu'une détection soit conservée.

#### Seuil BAS (ex: 0.1)
- Le modèle est **peu exigeant**
- **Conséquences** :
  - Beaucoup de détections (même avec faible confiance)
  - Recall **élevé** (peu d'objets manqués)
  - Precision **faible** (beaucoup de faux positifs)
- **Cas d'usage** : Quand manquer un objet est critique (sécurité, médical)

#### Seuil ÉLEVÉ (ex: 0.75)
- Le modèle est **très exigeant**
- **Conséquences** :
  - Peu de détections (seules les plus confiantes)
  - Precision **élevée** (détections très fiables)
  - Recall **faible** (beaucoup d'objets manqués)
- **Cas d'usage** : Quand les fausses alarmes sont coûteuses

#### Seuil MOYEN (ex: 0.25-0.5)
- **Compromis équilibré** entre precision et recall
- Valeur par défaut de YOLOv8 : **0.25**

### Le compromis fondamental
Il est **impossible de maximiser simultanément** precision et recall :
- Augmenter le seuil → Precision ↗️ mais Recall ↘️
- Diminuer le seuil → Recall ↗️ mais Precision ↘️

La **courbe Precision-Recall** et la **métrique mAP** (mean Average Precision) permettent de résumer ce compromis.

---

## 3️⃣ Dans quels cas d'usage préféreriez-vous YOLOv8n à YOLOv8s ? Et inversement ?

### 🚀 Préférez YOLOv8n (nano) quand :

#### Contraintes de temps réel strict
- **Besoin de >30 FPS** (images par seconde)
- Applications où **la latence est critique**
- Exemples : Robotique, drones, véhicules autonomes

#### Matériel limité
- **Mobile, tablette, embarqué** (Raspberry Pi, Jetson Nano)
- **Edge computing** avec ressources CPU/GPU limitées
- Mémoire RAM restreinte (< 4 Go)

#### Priorité à la vitesse
- Surveillance vidéo en temps réel
- Applications grand public (apps mobiles)
- Traitement de flux vidéo continu

#### Tolérance à une précision réduite
- Quand une légère baisse de mAP est acceptable
- Détection "suffisante" pour l'usage

**Exemples concrets** :
- App de réalité augmentée sur smartphone
- Drone de surveillance
- Robot aspirateur détectant des obstacles
- Application de comptage de personnes en temps réel

---

### 🎯 Préférez YOLOv8s (small) quand :

#### La précision est prioritaire
- **Applications critiques** où chaque détection compte
- Quand le **mAP élevé** est essentiel
- Détection de petits objets ou détails fins

#### Matériel puissant disponible
- **Serveur, cloud, workstation** avec GPU dédié
- Ressources computationnelles suffisantes
- Pas de contrainte de latence stricte

#### Temps de réponse flexible
- **10-20 FPS** sont suffisants
- Traitement par batch possible
- Applications non temps réel

#### Sécurité et fiabilité
- **Systèmes de sécurité** (détection d'intrus)
- **Médical** (détection de tumeurs)
- **Industriel** (contrôle qualité)

**Exemples concrets** :
- Système de vidéosurveillance avec serveur GPU
- Analyse médicale d'images radiologiques
- Contrôle qualité automatisé en usine
- Analyse postérieure de vidéos (pas de temps réel)

---

### 📊 Comparaison chiffrée (sur COCO128)

| Métrique | YOLOv8n | YOLOv8s | Différence |
|----------|---------|---------|------------|
| **Paramètres** | 3.2M | 11.2M | 3.5x plus grand |
| **mAP50** | ~0.65 | ~0.70 | +0.05 (+7.7%) |
| **mAP50-95** | ~0.45 | ~0.50 | +0.05 (+11.1%) |
| **Latence** | ~15 ms | ~25 ms | +10 ms (+67%) |
| **FPS** | ~67 FPS | ~40 FPS | -27 FPS |

### 🎯 Règle de décision

```
SI (temps_réel_strict OU matériel_limité) ALORS YOLOv8n
SINON SI (précision_critique OU matériel_puissant) ALORS YOLOv8s
SINON YOLOv8n (par défaut pour la vitesse)
```

---

## 4️⃣ Documentez vos 3 cas d'échec et expliquez les causes probables

### Cas d'échec 1 : Faux négatif en faible luminosité

**Image** : `night_city.jpg` (scène urbaine de nuit)

**Échec observé** :
- **Objets manqués** : Véhicules peu éclairés, piétons dans l'ombre
- **Détections** : Seuls les objets bien éclairés (enseignes lumineuses, phares) sont détectés

**Cause probable** :
- **Faible luminosité** → Contraste insuffisant pour extraire les contours
- Le modèle YOLOv8n a été entraîné majoritairement sur COCO (images de jour)
- Les features visuelles (bords, textures) sont atténuées la nuit

**Solutions potentielles** :
1. **Prétraitement** : Augmentation de la luminosité, égalisation d'histogramme
2. **Fine-tuning** : Ré-entraîner sur un dataset d'images nocturnes
3. **Modèle spécialisé** : Utiliser un modèle entraîné spécifiquement pour la nuit

---

### Cas d'échec 2 : Faux positif par confusion de forme

**Image** : `furniture.jpg` (intérieur avec meubles)

**Échec observé** :
- **Fausse détection** : Un coussin/oreiller détecté comme "personne" (confiance: 0.32)
- **Confusion** : Le modèle interprète une forme allongée sur un canapé comme une personne allongée

**Cause probable** :
- **Similarité de forme** : Le coussin a une forme vaguement humanoïde (allongée)
- **Contexte ambigu** : Dans un salon, la présence de personnes est plausible
- **Texture** : Le tissu peut ressembler à des vêtements

**Solutions potentielles** :
1. **Augmenter le seuil de confiance** (ex: 0.5 au lieu de 0.25)
2. **Fine-tuning** avec des exemples négatifs (coussins, oreillers)
3. **Utiliser le contexte** : Vérifier la cohérence sémantique de la scène

---

### Cas d'échec 3 : Confusion entre classes similaires

**Images** : `dog.jpg` et `cat.jpg`

**Échec observé** :
- **Mauvaise classification** : Un chat siamois détecté comme "chien" (confiance: 0.41)
- **Inversement** : Un petit chien détecté comme "chat" dans certaines images

**Cause probable** :
- **Similarité visuelle** dans COCO : Chiens et chats partagent des features communes (4 pattes, queue, fourrure)
- **Variabilité intra-classe** : Certaines races de chiens ressemblent à des chats (ex: Chihuahua) et vice-versa
- **Angle de vue** : Vue de dos ou de profil rend la distinction difficile

**Solutions potentielles** :
1. **Fine-tuning** avec un dataset équilibre chats/chats
2. **Augmentation de données** : Plus de variations de races, angles, éclairages
3. **Modèle spécialisé** : Entraîner un classifieur binaire chien/chat en post-traitement

---

### 🔍 Analyse transversale des échecs

Les échecs de YOLOv8 (et des modèles de détection en général) surviennent principalement dans ces situations :

#### 1. Conditions d'éclairage difficiles
- **Nuit**, contre-jour, ombres portées
- **Solution** : Prétraitement, fine-tuning, modèles spécialisés

#### 2. Occlusions partielles
- **Objets cachés** en partie par d'autres objets
- **Solution** : Modèles avec attention, datasets avec occlusions

#### 3. Classes visuellement similaires
- **Chien/chat**, chaise/canapé, voiture/camion
- **Solution** : Fine-tuning, features plus discriminantes

#### 4. Objets très petits
- **< 32×32 pixels** dans l'image
- **Solution** : Modèles multi-échelles, super-résolution

#### 5. Angles de vue inhabituels
- **Vue de dessus**, perspective extrême, objets inversés
- **Solution** : Augmentation de données avec transformations

#### 6. Objets absents de COCO
- **Classes non présentes** dans le dataset d'entraînement
- **Solution** : Fine-tuning sur dataset personnalisé

---

## 5️⃣ Expériences supplémentaires testées

### Expérience A - YOLOv8m (Medium)

**Description** : Modèle plus grand que YOLOv8n et YOLOv8s, avec plus de paramètres.

**Résultats** :
- **Détections** : 8 objets détectés sur l'image de test
- **Usage** : Applications où la précision est prioritaire sur la vitesse

**Comparaison** :
| Modèle | Paramètres | Vitesse | Précision |
|--------|------------|---------|-----------|
| YOLOv8n | 3.2M | ++ | + |
| YOLOv8s | 11.2M | + | ++ |
| YOLOv8m | 25.9M | - | +++ |

---

### Expérience C - YOLOv8n-seg (Segmentation d'instances)

**Description** : Variante de YOLOv8 pour la segmentation sémantique au niveau des objets.

**Résultats** :
- **Masks de segmentation** : 9 masks détectés
- **Application** : Comptage d'objets, médical, agriculture

**Cas d'usage** :
- Détection de cellules tumorales
- Comptage de fruits dans une plantation
- Segmentation de pièces mécaniques

---

### Expérience D - YOLOv8n-pose (Estimation de pose)

**Description** : Variante de YOLOv8 pour détecter les points clés du corps humain (17 points).

**Résultats** :
- **Personnes détectées** : 4 personnes avec keypoints
- **Points par personne** : 17 keypoints (nez, yeux, oreilles, épaules, coudes, poignets, hanches, genoux, chevilles)

**Cas d'usage** :
- Analyse sportive (golf, tennis, course)
- Surveillance comportementale
- Interaction humain-machine
- Réalité augmentée

---

### 📊 Comparaison des variantes YOLOv8

| Variante | Usage principal | Métier推荐 |
|----------|-----------------|------------|
| yolov8n | Détection rapide | Edge/Mobile/Embappé |
| yolov8s | Détection équilibrée | Serveur/Cloud |
| yolov8m | Détection précise | Précision maximale |
| yolov8n-seg | Segmentation d'instances | Médical/Agriculture/Vision industrielle |
| yolov8n-pose | Estimation de pose | Sport/Surveillance/Interaction |

---

## 🎯 Conclusion générale

Ce projet a permis de :

✅ **Maîtriser l'API Ultralytics YOLOv8**  
✅ **Comprendre les métriques** : IoU, mAP, precision, recall  
✅ **Analyser le compromis vitesse/précision** entre YOLOv8n et YOLOv8s  
✅ **Identifier les limites** des modèles pré-entraînés  
✅ **Documenter les cas d'échec** et leurs causes  
✅ **Explorer les variantes YOLOv8** : segmentation (YOLOv8n-seg), pose estimation (YOLOv8n-pose)
✅ **Tester YOLOv8m** : modèle medium avec plus de paramètres

**Résultats expérimentaux** :
- YOLOv8n : 3.2M paramètres, 56.7 FPS, mAP50=0.607
- YOLOv8s : 11.2M paramètres, 47.3 FPS, mAP50=0.760
- YOLOv8n-seg : 9 masks de segmentation détectés
- YOLOv8n-pose : 4 personnes détectées avec 17 keypoints chacune

**Perspectives d'amélioration** :
- Fine-tuning sur un dataset personnalisé (ex: détection de casques sur chantier)
- Optimisation pour déploiement embarqué (TensorRT, ONNX, quantification)
- Intégration dans une application temps réel complète
- Exploration du fine-tuning sur YOLOv8-seg pour la détection de défauts industriels

---

**Note** : Toutes les visualisations, courbes et résultats chiffrés sont disponibles dans le notebook `projet_C_yolov8_detection.ipynb` et le dossier `runs/detect/`.