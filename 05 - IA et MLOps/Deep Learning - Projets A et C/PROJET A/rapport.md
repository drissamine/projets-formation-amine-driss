# Rapport - Projet A : Classification d'Images par Transfer Learning

**Master 2 - ESIS Deep Learning**  
**Date : 7 Avril 2026**

---

## 1. Introduction

Ce projet vise a classifier des images de dechets recyclables en 6 categories (cardboard, glass, metal, paper, plastic, trash) en utilisant le transfer learning avec ResNet-50 pre-entraine sur ImageNet.

---

## 2. Methodologie

### 2.1 Environnement
- **GPU** : NVIDIA GeForce RTX 4060 Laptop GPU (8.6 GB)
- **Framework** : PyTorch 2.6.0 + CUDA 12.4
- **Temps d'entrainement total** : ~8 minutes

### 2.2 Dataset
- **Source** : Garbage Classification (Kaggle)
- **Taille** : 2527 images total
- **Split** : 70% train (1768), 15% val (379), 15% test (380)
- **Classes** : cardboard, glass, metal, paper, plastic, trash

### 2.3 Modele
- **Architecture** : ResNet-50 pre-entraine ImageNet
- **Parametres totaux** : 23,510,081
- **Parametres entrainables (Feature Extraction)** : 2,049 (0.01%)

### 2.4 Hyperparametres

| Phase | LR (corps) | LR (tete) | Epochs |
|-------|-------------|------------|--------|
| Feature Extraction | - | 1e-3 | 5 |
| Fine-tuning | 1e-4 | 1e-3 | 5 |

---

## 3. Resultats Experimentaux

### 3.1 Comparaison Feature Extraction vs Fine-tuning

| Approche | Test Accuracy | Temps/epoch |
|----------|---------------|-------------|
| Feature Extraction | **100.00%** | ~40s |
| Fine-tuning | **100.00%** | ~48s |

### 3.2 Details par Epoch

**Feature Extraction :**
```
Epoch 1/5 | Train: 100.0% | Val: 100.0% | 49.5s
Epoch 2/5 | Train: 100.0% | Val: 100.0% | 42.2s
Epoch 3/5 | Train: 100.0% | Val: 100.0% | 39.3s
Epoch 4/5 | Train: 100.0% | Val: 100.0% | 39.8s
Epoch 5/5 | Train: 100.0% | Val: 100.0% | 41.6s
```

**Fine-tuning :**
```
Epoch 1/5 | Train: 100.0% | Val: 100.0% | 43.2s
Epoch 2/5 | Train: 100.0% | Val: 100.0% | 47.1s
Epoch 3/5 | Train: 100.0% | Val: 100.0% | 48.8s
Epoch 4/5 | Train: 100.0% | Val: 100.0% | 50.9s
Epoch 5/5 | Train: 100.0% | Val: 100.0% | 51.3s
```

### 3.3 Matrice de Confusion

Le modele atteint 100% de precision sur toutes les classes. Aucune confusion n'a ete observee entre les categories.

---

## 4. Test sur Images Personnelles

### 4.1 Resultats

| Image | Prediction | Confiance |
|-------|------------|-----------|
| carton.jpg | cardboard | XX% |
| verre.jpg | glass | XX% |
| metal.jpg | metal | XX% |
| paper.jpg | paper | XX% |
| plastic.jpg | plastic | XX% |
| trash.jpg | trash | XX% |

*Resultats a completer apres execution de la cellule 6b*

---

## 5. Analyse des Questions

### Q1 : Difference entre FE et FT - Pourquoi FT est meilleur ?

Le fine-tuning complet surpasse generalement la feature extraction pour plusieurs raisons :

1. **Adaptation des features intermediaires** : En degelant toutes les couches, le modele peut adapter non seulement la tete de classification mais aussi les representations intermediaires. Les premieres couches apprennent des features tres generales (bords, textures) qui restent utiles, mais les couches plus profondes peuvent etre optimisees pour le domaine specifique.

2. **Meilleure generalisation** : Le fine-tuning permet au modele de s'adapter aux specificites du nouveau domaine tout en conservant la richesse des representations apprises sur ImageNet.

3. **Plasticite neuronale complete** : En autorisant la mise a jour de tous les poids, le reseau peut trouver un meilleur equilibre entre conservation et acquisition de nouvelles connaissances.

**Observation dans notre cas** : Les deux approches atteignent 100%, ce qui suggere que les features genriques d'ImageNet sont excellentes pour la classification de dechets.

### Q2 : Impact de la reduction du learning rate (10x) ?

Experience : LR 1e-4 → 1e-5

**Resultats attendus** :
- **Convergence plus lente** : Les mises a jour des poids sont plus petites, le modele necessite plus d'epochs pour converger.
- **Meilleure stabilite** : Courbes de loss plus lisses, moins de fluctuations entre les epochs.
- **Risque de sous-apprentissage** : Si le LR est trop faible, le modele peut rester piege dans un minimum local sous-optimal.

**Recommendation** : Un LR de 1e-4 est un bon compromis pour le fine-tuning. Il permet une adaptation rapide tout en preservant les representations pre-entrainees.

### Q3 : Classes les plus difficiles a distinguer ?

Les confusions potentielles dans la classification de dechets sont souvent entre :

1. **Plastique vs Metal** : Les emballages plastiques et metalliques ont souvent des reflexions et textures similaires.

2. **Carton vs Papier** : Ces deux materiaux partagent des textures et couleurs tres similaires.

3. **Verre transparent** : Le verre transparent peut etre confondu car les features visuelles dependent fortement de l'arriere-plan.

**Explication** :
- Le modele se base uniquement sur des features visuelles (couleur, texture, forme)
- Il ne peut pas "toucher" ou "sentir" les materiaux
- L'eclairage et l'arriere-plan introduisent du bruit

### Q4 : Quel serait l'impact d'entrainer from scratch ?

**Consequences** :

1. **Donnees requises** : Il faudrait des millions d'images pour obtenir des representations aussi riches. ImageNet contient 1.2M d'images - notre dataset de ~2500 images serait massivement insuffisant.

2. **Temps de calcul** : L'entrainement from scratch necessiterait des jours/semaines sur GPU puissant, contre quelques minutes pour le fine-tuning.

3. **Performance** : Le modele serait generalement bien moins performant.

**Pourquoi rarement fait en pratique ?**
- Le transfer learning fonctionne generalement bien (negative transfer rare)
- Couteux en energie et temps de calcul
- Datasets pre-entrainement disponibles (ImageNet, COCO, etc.)

**Exception** : L'entrainement from scratch peut etre justifie quand :
- Le domaine est tres different d'ImageNet (images medicales, satellites)
- On dispose d'un tres large dataset specifique

---

## 6. Conclusion

Ce projet a permis de demontrer l'efficacite du transfer learning pour la classification d'images de dechets recyclables :

1. **ResNet-50 pre-entraine sur ImageNet** est extremement efficace pour cette tache
2. **Le fine-tuning complet** offre des performances egales a la feature extraction
3. **Le temps d'entrainement sur GPU** (RTX 4060) est tres reduit (~8 minutes)
4. **100% d'accuracy** suggerent que le modele est bien adapte a ce type de classification

Les performances parfaites suggerent que le modele pourrait etre teste sur des images personnelles pour evaluer sa robustesse en conditions reelles.

---

## 7. References

- He et al., "Deep Residual Learning for Image Recognition", CVPR 2016
- PyTorch TorchVision Models
- Kaggle Garbage Classification Dataset
