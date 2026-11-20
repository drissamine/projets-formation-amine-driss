# Explications Détaillées - TP2 Tâches de la Vision par Ordinateur

Ce document fournit une explication détaillée pour chaque exercice du TP2, incluant les objectifs, les concepts théoriques, la démarche de résolution, l'interprétation des résultats et les conclusions.

---

## Module 1 : Classification d'Images

### Exercice 1.1 : Implémentation de la Classification Softmax

#### 1) Objectif et Concepts Théoriques

**Objectif :**
Implémenter un classifieur Softmax (régression logistique multiclasse) entraîné par descente de gradient sur les features HOG+LBP+couleur.

**Concepts théoriques :**

La classification Softmax est une généralisation de la régression logistique pour plusieurs classes. Le principe fondamental est de transformer les scores linéaires en probabilités помощью la fonction softmax :

$$\hat{p}_k = \frac{e^{z_k}}{\sum_{j=1}^{C} e^{z_j}}$$

Où $z = W^T x + b$ est le score linéaire pour chaque classe.

La fonction de perte est la cross-entropie :
$$L = -\frac{1}{N}\sum_{i=1}^{N} \log \hat{p}_{y_i}$$

Le gradient de la perte par rapport aux poids est :
$$\frac{\partial L}{\partial W} = \frac{1}{N} X^T (\hat{P} - Y_{onehot})$$

#### 2) Démarche de Résolution

**Étape 1 : Implémentation de la fonction softmax stable**
```python
def softmax(self, z):
    z_stable = z - z.max(axis=1, keepdims=True)  # Évite l'overflow numérique
    e = np.exp(z_stable)
    return e / e.sum(axis=1, keepdims=True)
```
La soustraction du maximum par ligne empêche l'explosion des exponentielles (overflow).

**Étape 2 : Initialisation des poids**
```python
self.W = np.random.randn(D, self.n_classes) * 0.01  # Petites valeurs aléatoires
self.b = np.zeros(self.n_classes)  # Biais initialisés à zéro
```

**Étape 3 : One-hot encoding des labels**
```python
Y_oh = np.eye(self.n_classes)[y]  # Transforme [0,1,2] en [[1,0,0],[0,1,0],[0,0,1]]
```

**Étape 4 : Boucle d'entraînement**
- Forward pass : calcul des scores z et des probabilités
- Calcul de la loss cross-entropy
- Calcul des gradients
- Mise à jour des poids par gradient descent

#### 3) Interprétation des Résultats

**Courbe de convergence :**
La loss doit décroître au fil des époques, indiquant que le modèle apprend. Une courbe typique montre une décroissance rapide au début, puis une stabilisation.

**Métriques attendues :**
- Accuracy : ~85-95% sur le dataset synthétique
- La loss initiale dépend de l'initialisation aléatoire
- La loss finale doit être proche de 0 pour une classification parfaite

**Visualisation conseillée :**
- Courbe de loss vs époques
- Comparaison avec d'autres classifieurs (SVM, k-NN)

#### 4) Conclusion

**Apprentissages clés :**
- Comprendre le fonctionnement de la softmax et son lien avec la régression logistique
- Maîtriser le gradient descent pour l'entraînement des réseaux de neurones
- L'importance de la stabilité numérique dans les implémentations

**Points importants :**
- La softmax est la fonction d'activation standard pour la classification multiclasse
- La cross-entropie est la loss standard car ellegradue bien avec les probabilités
- L'initialisation des poids est cruciale pour la convergence

---

### Exercice 1.2 : Impact du Descripteur sur les Performances

#### 1) Objectif et Concepts Théoriques

**Objectif :**
Comparer les performances d'un SVM en utilisant chaque type de feature séparément (HOG seul, LBP seul, couleur seul) et en combinaison, pour déterminer le descripteur le plus discriminant.

**Concepts théoriques :**

Les descripteurs sont des représentations numériques des images qui capturent différents aspects visuels :

| Descripteur | Principe | Usage |
|-------------|----------|-------|
| **HOG** | Histogramme de gradients orientés | Formes, contours |
| **LBP** | Comparaison pixel avec voisins | Textures |
| **Couleur** | Distribution des couleurs HSV | Couleur dominante |

#### 2) Démarche de Résolution

**Étape 1 : Extraction séparée des features**
```python
X_hog = np.array([extract_hog(img)[0] for img in dataset_imgs])
X_lbp = np.array([extract_lbp(img)[0] for img in dataset_imgs])
X_color = np.array([extract_color_hist(img) for img in dataset_imgs])
X_all = np.concatenate([X_hog, X_lbp, X_color], axis=1)
```

**Étape 2 : Entraînement SVM pour chaque feature**
```python
for name, X_feat in feature_sets.items():
    clf = SVC(kernel="rbf", C=10, gamma="scale")
    clf.fit(X_train, y_train)
    acc = accuracy_score(y_test, clf.predict(X_test))
```

#### 3) Interprétation des Résultats

**Résultats typiques :**

| Descripteur | Accuracy |
|-------------|----------|
| HOG seul | ~80-90% |
| LBP seul | ~60-75% |
| Couleur seul | ~70-85% |
| **Combiné** | **~90-98%** |

**Analyse :**
- HOG est généralement le plus performant car il capture les contours
- La combinaison est toujours meilleure car elle capture des informations complémentaires
- LBP seul est moins performant car les textures sont moins discriminantes

#### 4) Conclusion

**Apprentissages clés :**
- L'importance de combiner plusieurs types de features
- Chaque descripteur capture des informations différentes
- La complémentarité des descripteurs améliore les performances

---

### Exercice 1.3 : CNN avec PyTorch (Transfer Learning)

#### 1) Objectif et Concepts Théoriques

**Objectif :**
Utiliser ResNet-18 pré-entraîné comme extracteur de features, puis entraîner un SVM sur ces features profondes.

**Concepts théoriques :**

Le transfer learning permet d'utiliser des réseaux entraînés sur ImageNet pour d'autres tâches. ResNet-18 produit des features de 512 dimensions qui capturent des concepts visuels de haut niveau.

#### 2) Démarche de Résolution

**Étape 1 : Charger ResNet-18**
```python
resnet = models.resnet18(weights="IMAGENET1K_V1")
feature_extractor = torch.nn.Sequential(*list(resnet.children())[:-1])
```

**Étape 2 : Extraire les features**
```python
transform = T.Compose([T.Resize((224,224)), T.ToTensor(),
                     T.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])])
feat = feature_extractor(transform(img)).squeeze().numpy()
```

#### 3) Interprétation des Résultats

Les features ResNet-18 sont généralement plus performantes que les features classiques :
- Accuracy attendue : ~95-100%
- Amélioration par rapport à HOG+LBP+SVM

#### 4) Conclusion

Le deep learning surpasse les méthodes classiques quand suffiamment de données sont disponibles.

---

## Module 2 : Détection d'Objets

### Exercice 2.1 : IoU et mAP

#### 1) Objectif et Concepts Théoriques

**Objectif :**
Calculer l'IoU vectorisé entre toutes les paires de boîtes et calculer la mAP@0.5.

**Concepts théoriques :**

**IoU (Intersection over Union)** :
$$IoU(A, B) = \frac{|A \cap B|}{|A \cup B|}$$

C'est la métrique standard pour évaluer les détections :
- IoU ≥ 0.5 = Vrai Positif (PASCAL VOC)
- IoU ≥ 0.5:0.95 = mAP COCO (10 seuils)

**NMS (Non-Maximum Suppression)** : Élimine les doublons en gardant seulement la détection avec le score le plus élevé.

#### 2) Démarche de Résolution

**Calcul de l'IoU pour une paire :**
```python
def compute_iou(box_a, box_b):
    ix1 = max(box_a[0], box_b[0])
    iy1 = max(box_a[1], box_b[1])
    ix2 = min(box_a[2], box_b[2])
    iy2 = min(box_a[3], box_b[3])
    inter = max(0, ix2-ix1) * max(0, iy2-iy1)
    union = area_a + area_b - inter
    return inter / (union + 1e-8)
```

**Matrice IoU (N prédictions × M GT) :**
```python
def compute_iou_matrix(pred_boxes, gt_boxes):
    N, M = len(pred_boxes), len(gt_boxes)
    iou_mat = np.zeros((N, M))
    for i, pb in enumerate(pred_boxes):
        for j, gb in enumerate(gt_boxes):
            iou_mat[i, j] = compute_iou(pb, gb)
    return iou_mat
```

**Calcul de l'AP :**
- Trier les prédictions par score décroissant
- Pour chaque prédiction, calculer TP/FP en fonction du IoU avec les GT
- Calculer précision et rappel cumulés
- L'AP est l'aire sous la courbe précision-rappel

#### 3) Interprétation des Résultats

**Exemple de matrice IoU :**

| Prédictions \ GT | Voiture | Roue |
|-----------------|---------|------|
| Détection 1 | ~0.9 | ~0.1 |
| Détection 2 | ~0.85 | ~0.1 |
| Détection 3 | ~0.1 | ~0.1 |
| Détection 4 | ~0.1 | ~0.8 |

**Métriques attendues :**
- AP@0.5 : ~0.7-0.9
- Impact du seuil IoU sur les résultats

#### 4) Conclusion

L'IoU est essentiel pour évaluer la qualité des localisations. La mAP est la métrique standard en détection d'objets.

---

### Exercice 2.2 : Template Matching

#### 1) Objectif et Concepts Théoriques

**Objectif :**
Implémenter un détecteur par template matching pour localiser la voiture.

**Concepts théoriques :**

Le template matching calcule la corrélation entre un template et chaque région de l'image :
$$R(x,y) = \sum_{x',y'} T(x',y') \cdot I(x+x', y+y')$$

#### 2) Démarche de Résolution

```python
# Extraire le template
template = gray_scene[88:175, 30:230]

# Appliquer le matching
result = cv2.matchTemplate(gray_full, template, cv2.TM_CCOEFF_NORMED)

# Trouver le maximum
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
```

#### 3) Interprétation des Résultats

- **Corrélation max** : proche de 1 = bonne correspondance
- **Position** : coordonnées du maximum = localisation de l'objet

#### 4) Conclusion

Le template matching est simple mais limité (sensible aux échelles et rotations).

---

### Exercice 2.3 : torchvision.ops

#### 1) Objectif et Concepts Théoriques

Utiliser les fonctions optimisées de PyTorch pour IoU et NMS.

#### 2) Démarche de Résolution

```python
from torchvision.ops import box_iou, nms as torch_nms
iou_mat = box_iou(boxes_t, gt_t)
kept_idx = torch_nms(boxes_t, scores_t, iou_threshold=0.5)
```

#### 3) Interprétation des Résultats

Les résultats doivent être identiques à l'implémentation NumPy.

---

## Module 3 : Segmentation d'Images

### Exercice 3.1 : Métriques Dice et mIoU

#### 1) Objectif et Concepts Théoriques

Calculer Dice et mIoU entre un masque prédit (K-Means) et un masque GT.

**Formules :**

$$\text{Dice}_c = \frac{2 \cdot TP_c}{2TP_c + FP_c + FN_c}$$

$$\text{IoU}_c = \frac{TP_c}{TP_c + FP_c + FN_c}$$

$$\text{mIoU} = \frac{1}{C} \sum_{c} \text{IoU}_c$$

#### 2) Démarche de Résolution

```python
def compute_dice(pred_mask, gt_mask, n_classes=2):
    for c in range(n_classes):
        tp = ((pred == c) & (gt == c)).sum()
        fp = ((pred == c) & (gt != c)).sum()
        fn = ((pred != c) & (gt == c)).sum()
        dice_c = 2*tp / (2*tp + fp + fn + 1e-8)
```

#### 3) Interprétation des Résultats

- Dice : 0-1 (1 = parfait)
- mIoU : 0-1 (1 = parfait)

#### 4) Conclusion

Dice et mIoU sont les métriques standards pour la segmentation sémantique.

---

### Exercice 3.2 : Segmentation Multi-classes HSV

#### 1) Objectif et Concepts Théoriques

Implémenter une segmentation sémantique à 4 classes par plages HSV.

#### 2) Démarche de Résolution

```python
def segment_by_color(img, n_classes=4):
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    
    # Ciel (bleu)
    mask[cv2.inRange(hsv, lower_sky, upper_sky) > 0] = 1
    
    # Sol (vert)
    mask[cv2.inRange(hsv, lower_ground, upper_ground) > 0] = 2
    
    # Rouge (voiture/maison)
    mask_red = cv2.bitwise_or(...)
    mask[mask_red > 0] = 3
```

#### 3) Interprétation des Résultats

Chaque classe correspond à une plage HSV spécifique.

#### 4) Conclusion

La segmentation par couleur est intuitive mais sensible aux variations d'éclairage.

---

### Exercice 3.3 : Segmentation d'Instances

#### 1) Objectif et Concepts Théoriques

Identifier et numéroter chaque instance distincte par composantes connexes.

#### 2) Démarche de Résolution

```python
from skimage.measure import regionprops, label
labels = label(binary_mask)
props = regionprops(labels)

for prop in props:
    print(f"Aire: {prop.area}, Barycentre: {prop.centroid}")
```

#### 3) Interprétation des Résultats

- Nombre d'instances = nombre de composantes connexes
- Propriétés : aire, barycentre, bounding box

#### 4) Conclusion

Les composantes connexes permettent de séparer les instances d'objets.

---

### Exercice 3.4 : U-Net

#### 1) Objectif et Concepts Théoriques

Définir l'architecture U-Net pour la segmentation sémantique.

#### 2) Démarche de Résolution

```python
class EncoderBlock(nn.Module):
    def forward(self, x):
        x = self.conv(x)
        return self.pool(x), x  # pooled + skip

class DecoderBlock(nn.Module):
    def forward(self, x, skip):
        x = self.up(x)
        x = torch.cat([x, skip], dim=1)
        return self.conv(x)
```

#### 3) Interprétation des Résultats

U-Net combine encodeur-décodeur avec des skip connections pour une segmentation précise.

#### 4) Conclusion

U-Net est l'architecture de référence pour la segmentation biomédicale.

---

## Projet Final : Pipeline Complet

Le pipeline intègre :
1. Prétraitement (normalisation, débruitage)
2. Classification (SVM)
3. Localisation (bounding box)
4. Segmentation (masque)

**Métriques finales :**
- Accuracy classification
- IoU segmentation
- Temps d'inférence
