# Guide de dépannage OCR

## Problème : L'OCR produit du charabia

Si vous obtenez des résultats comme:
```
a / m7) MAN e na Ht Aen nny deed...
```

C'est un problème classique avec les photos de documents. Voici les solutions.

---

## Causes possibles

### 1. **Résolution insuffisante**
Tesseract fonctionne mieux avec des images de 300 DPI minimum.

### 2. **Perspective/angle**
Les photos de téléphone ont souvent une perspective qui déforme le texte.

### 3. **Éclairage inégal**
Zones sombres et zones claires sur le même document.

### 4. **Bruit numérique**
Compression JPEG, artefacts, pixels parasites.

### 5. **Contraste faible**
Texte gris sur fond gris.

---

## Solutions

### Solution 1 : Redimensionnement simple

```python
import cv2

# Charger
image = cv2.imread('photo.jpg')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Agrandir (Tesseract aime les grandes images)
h, w = gray.shape
scale = 2000 / w  # Target 2000px width
resized = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

# Seuillage Otsu
_, binary = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# Sauvegarder et tester
cv2.imwrite('processed.jpg', binary)
```

### Solution 2 : Correction de perspective

```python
# Détecter les contours du document
edges = cv2.Canny(gray, 50, 150)
contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Trouver le plus grand contour (probablement le document)
largest = max(contours, key=cv2.contourArea)

# Redresser (warp perspective)
# ... code de transformation ...
```

### Solution 3 : Amélioration du contraste

```python
# CLAHE (Contrast Limited Adaptive Histogram Equalization)
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
enhanced = clahe.apply(gray)
```

### Solution 4 : Débruitage

```python
# Non-local means denoising (préserve les bords)
denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
```

---

## Tests rapides

### Test avec Python

```bash
# Aller dans le dossier
cd document_detection

# Test avec Tesseract seul
python test_tesseract_only.py chemin/vers/photo.jpg

# Test avec toutes les méthodes
python test_photo_fix.py chemin/vers/photo.jpg
```

### Test avec Tesseract directement

```bash
# Installer Tesseract d'abord
# Puis:
tesseract photo.jpg output -l fra+eng

cat output.txt
```

---

## Paramètres recommandés

### Pour documents scannés (bonne qualité)
- Prétraitement minimal
- Seuillage Otsu
- Pas de redimensionnement nécessaire

### Pour photos de téléphone
- Redimensionnement 2x minimum
- Débruitage léger
- CLAHE pour contraste
- Correction de perspective si possible

### Pour documents anciens/fanés
- CLAHE plus fort (clipLimit=3.0)
- Seuillage adaptatif
- Débruitage modéré

---

## Outils de debug

Les scripts créés enregistrent les images intermédiaires:

- `ocr_debug/method1_original.jpg`
- `ocr_debug/method2_resize_otsu.jpg`
- `ocr_debug/method3_denoise.jpg`
- etc.

Vérifiez ces images pour voir quel prétraitement fonctionne le mieux.

---

## Alternative : EasyOCR

Si Tesseract ne fonctionne pas, essayez EasyOCR:

```python
import easyocr
reader = easyocr.Reader(['fr', 'en'])
result = reader.readtext('photo.jpg')
for (bbox, text, conf) in result:
    print(f"{text} (conf: {conf:.2f})")
```

EasyOCR est parfois plus robuste pour les photos de mauvaise qualité.

---

## Checklist

- [ ] Image en couleur ou niveaux de gris ?
- [ ] Résolution suffisante (>1000px de large) ?
- [ ] Document bien visible (pas flou) ?
- [ ] Éclairage uniforme ?
- [ ] Pas de reflets brillants ?
- [ ] Texte lisible à l'œil nu ?

Si le texte n'est pas lisible pour vous, l'OCR ne pourra pas le lire non plus.

---

## Besoin d'aide ?

1. Vérifiez les images de test dans `ocr_debug/`
2. Testez avec Tesseract directement
3. Comparez les résultats des différentes méthodes
4. Ajustez les paramètres de prétraitement

**Règle d'or** : Le prétraitement doit rendre le texte **noir sur blanc**, bien net, sans bruit.
