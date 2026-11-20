# Guide de Test - OCR Document v2.0

## 🚀 Tests rapides (1 minute)

### Test 1 : Vérifier les composants
```bash
cd document_detection
python -c "from src.ocr import DocumentPreprocessor, OCREngine, FieldExtractor; print('✓ Module OCR OK')"
```

### Test 2 : Test EasyOCR simple
```bash
python test_easyocr_only.py "dataset/images/driver_license/permis-de-conduire-fr.png"
```

### Test 3 : Pipeline complet (détection + OCR)
```bash
python test_full_ocr.py "dataset/images/driver_license/permis-de-conduire-fr.png"
```

---

## 📸 Tests par type de document

### Pour les documents de bonne qualité (scans)

**Méthode recommandée :** EasyOCR sans prétraitement

```python
import easyocr
import cv2

reader = easyocr.Reader(['fr', 'en'], gpu=False)
image = cv2.imread('document.jpg')

results = reader.readtext(image)
for (bbox, text, conf) in results:
    print(f"{text} (conf: {conf:.2f})")
```

### Pour les photos de téléphone (moyenne qualité)

**Méthode recommandée :** Quick fix + EasyOCR

```bash
python test_low_quality.py "chemin/vers/ma_photo.jpg"
```

### Pour les photos floues/bruitées

**Méthode recommandée :** Traitement agressif

```bash
python test_low_quality.py "chemin/vers/photo_floue.jpg"
```

---

## 🧪 Tests approfondis

### Analyser la qualité d'une image

```bash
python test_low_quality.py "votre_image.jpg"
```

**Sortie attendue :**
```
ANALYZING IMAGE QUALITY
File: votre_image.jpg

[1] Quality Analysis:
--------------------------------------------------
  Resolution: 1452x2064
  Blur Score: 150.32
  Brightness: 128.5
  Contrast: 45.2
  Noise Level: 8.5
```

### Comparer les méthodes de traitement

```bash
python test_low_quality.py "votre_image.jpg" --compare
```

---

## 🔍 Dépannage

### Problème : "tesseract is not installed"

**Solution :** Utilisez EasyOCR uniquement

```python
from src.ocr.engine import OCREngine

ocr = OCREngine()
text, conf = ocr._recognize_easyocr(image)  # Force EasyOCR
```

### Problème : Texte illisible (charabia)

**Cause :** Prétraitement trop agressif

**Solution :** Pas de binarisation, utiliser EasyOCR

```python
import cv2
import easyocr

# Charger l'image
image = cv2.imread('photo.jpg')

# PAS de conversion en niveaux de gris
# PAS de seuillage
# PAS de morphologie

# Utiliser directement EasyOCR
reader = easyocr.Reader(['fr'])
results = reader.readtext(image)
```

### Problème : Texte trop petit

**Solution :** Upscale avant OCR

```python
h, w = image.shape[:2]
if w < 1000:
    scale = 2000 / w
    image = cv2.resize(image, None, fx=scale, fy=scale)
```

---

## 📝 Scripts de test disponibles

| Script | Usage | Description |
|--------|-------|-------------|
| `test_easyocr_only.py` | `python test_easyocr_only.py <image>` | Test simple avec EasyOCR |
| `test_full_ocr.py` | `python test_full_ocr.py <image>` | Pipeline complet |
| `test_low_quality.py` | `python test_low_quality.py <image>` | Traitement photos mauvaise qualité |
| `test_tesseract_only.py` | `python test_tesseract_only.py <image>` | Test avec Tesseract |
| `test_photo_fix.py` | `python test_photo_fix.py <image>` | Plusieurs méthodes de prétraitement |
| `debug_ocr.py` | `python debug_ocr.py <image>` | Analyse détaillée |

---

## 🎯 Tests de scénarios réels

### Scénario 1 : Photo de CNI prise au téléphone

```bash
# Copier votre photo dans le dossier test
python test_low_quality.py "chemin/vers/ma_cni.jpg"
```

**Attendu :**
- Détection automatique des problèmes (flou, bruit, etc.)
- Traitement adaptatif
- Extraction des champs : nom, prénom, date_naissance

### Scénario 2 : Document scanné

```bash
python test_easyocr_only.py "document_scanne.pdf"
```

**Attendu :**
- OCR rapide
- Texte bien reconnu
- Pas besoin de prétraitement

### Scénario 3 : Photo de permis (glare/reflets)

```bash
python test_low_quality.py "permis_avec_reflets.jpg"
```

**Attendu :**
- Détection des reflets
- Correction automatique
- Extraction malgré les reflets

---

## 📊 Interprétation des résultats

### Score de qualité

| Métrique | Bon | Moyen | Mauvais |
|----------|-----|-------|---------|
| Blur Score | >100 | 50-100 | <50 |
| Brightness | 80-180 | 50-80 | <50 ou >200 |
| Contrast | >40 | 20-40 | <20 |
| Noise | <10 | 10-20 | >20 |

### Score OCR

| Confidence | Qualité |
|------------|---------|
| >0.90 | Excellente |
| 0.70-0.90 | Bonne |
| 0.50-0.70 | Moyenne |
| <0.50 | Faible (prétraitement nécessaire) |

---

## 💡 Astuces

### Pour améliorer les résultats :

1. **Upscale toujours** les petites images (<1000px)
2. **Utilisez EasyOCR** pour les photos (pas de binarisation)
3. **Testez plusieurs méthodes** avec `--compare`
4. **Vérifiez les images** dans `ocr_low_quality_results/`

### Pour déboguer :

1. **Regardez les images intermédiaires** dans `ocr_debug_analysis/`
2. **Comparez les méthodes** avec `test_low_quality.py --compare`
3. **Analysez les scores** de qualité pour identifier le problème

---

## 📁 Fichiers générés

Après les tests, vous trouverez dans `ocr_low_quality_results/` :

- `*_00_original.jpg` - Image originale
- `*_01_processed.jpg` - Image traitée
- `*_quick_fix.jpg` - Version traitement rapide
- `*_full_processing.jpg` - Version traitement complet

---

## ✅ Checklist de validation

- [ ] EasyOCR fonctionne (`test_easyocr_only.py`)
- [ ] Pipeline complet fonctionne (`test_full_ocr.py`)
- [ ] Qualité d'image analysée (`test_low_quality.py`)
- [ ] Champs extraits correctement
- [ ] API démarrée (`start_api_improved.bat`)
- [ ] Interface web accessible (http://localhost:8000/dashboard)

---

## 🆘 Besoin d'aide ?

1. **Vérifiez les images de debug** dans `ocr_low_quality_results/`
2. **Comparez les méthodes** avec `--compare`
3. **Consultez** `OCR_TROUBLESHOOTING.md` pour les erreurs courantes
4. **Testez avec EasyOCR uniquement** si Tesseract échoue

**Email de support** : Votre professeur de Deep Learning 😄
