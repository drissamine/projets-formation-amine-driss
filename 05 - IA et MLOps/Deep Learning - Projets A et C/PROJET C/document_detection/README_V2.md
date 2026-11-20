# Document OCR API v2.0 - Guide Complet

## 🚀 Démarrage rapide

### Option 1 : Script batch (recommandé)
```bash
start_complete.bat
```
Puis ouvrez : http://localhost:8000/dashboard

### Option 2 : Commande manuelle
```bash
cd document_detection
python -m uvicorn api.main_improved:app --reload --port 8000
```

---

## 📡 Endpoints disponibles

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `GET /` | - | Info API |
| `GET /health` | - | Statut système |
| `POST /detect` | Upload | Détection documents |
| `POST /ocr` | Upload | OCR rapide |
| `POST /ocr-smart` | Upload | OCR avec prétraitement |
| `POST /ocr-file` | JSON | OCR depuis chemin |
| `GET /dashboard` | - | Interface web |

---

## 🖥️ Interface Web

Ouvrez http://localhost:8000/dashboard

### Fonctionnalités :
- 📤 **Drag & drop** de fichiers
- ⚡ **2 modes** : Smart (qualité) / Rapide (vitesse)
- 🎯 **Détection automatique** du type de document
- 📝 **Extraction des champs** : Nom, Prénom, Date, Numéro...
- 📊 **Métriques** en temps réel

---

## 📁 Structure du projet

```
document_detection/
├── api/
│   ├── main_improved.py          # API v2.0
│   ├── index.html                # Interface web
│   └── ocr_dashboard.html        # Dashboard alternatif
├── src/
│   └── ocr/
│       ├── __init__.py
│       ├── preprocessor.py       # Prétraitement standard
│       ├── preprocessor_v2.py    # Prétraitement avancé
│       ├── low_quality_processor.py # Photos de mauvaise qualité
│       ├── engine.py              # Moteurs OCR
│       └── extractor.py           # Extraction de champs
├── models/
│   └── document_detector.pt      # Modèle YOLO
├── tests/
│   ├── test_easyocr_only.py     # Test EasyOCR
│   ├── test_full_ocr.py          # Pipeline complet
│   ├── test_low_quality.py       # Photos mauvaise qualité
│   └── ...
├── start_complete.bat            # Démarrage complet
└── GUIDE_TESTS.md               # Guide de test
```

---

## 🔧 Tests disponibles

### Test rapide
```bash
# EasyOCR seul
python test_easyocr_only.py chemin/vers/image.jpg

# Pipeline complet
python test_full_ocr.py chemin/vers/image.jpg

# Photos de mauvaise qualité
python test_low_quality.py chemin/vers/image.jpg
```

---

## 📊 Types de documents supportés

| Type | Classe | Champs extraits |
|------|--------|-----------------|
| Carte d'identité | `id_card` | nom, prénom, date_naissance, lieu_naissance, numéro, nationalité, sexe |
| Permis de conduire | `driver_license` | nom, prénom, date_naissance, numéro, catégorie, dates |
| Titre de séjour | `residence_permit` | nom, prénom, date_naissance, nationalité, numéro |
| Passeport | `passport` | nom, prénom, date_naissance, nationalité, numéro, dates |

---

## 💡 Conseils d'utilisation

### Pour les documents scannés (bonne qualité)
- Utilisez le mode **Rapide**
- Pas de prétraitement nécessaire

### Pour les photos de téléphone
- Utilisez le mode **Smart**
- Le prétraitement améliorera les résultats

### Pour les photos floues/bruitées
- Utilisez `test_low_quality.py` pour analyse avancée
- Le système détecte automatiquement les problèmes

---

## 🐛 Dépannage

### Erreur "tesseract not found"
```bash
# Utilisez EasyOCR uniquement
python test_easyocr_only.py image.jpg
```

### OCR produit du charabia
- Le prétraitement est trop agressif
- Utilisez le mode Smart qui optimise automatiquement
- Vérifiez les images dans `ocr_debug/`

### API ne démarre pas
```bash
# Vérifiez les dépendances
pip install -r requirements.txt

# Vérifiez le modèle
ls models/document_detector.pt
```

---

## 📦 Dépendances principales

```
ulalytics>=8.0.0      # YOLO
easyocr>=1.7.0        # OCR
opencv-python>=4.8.0  # Traitement image
fastapi>=0.100.0      # API
pytesseract           # OCR alternatif (optionnel)
```

---

## 🔗 Liens utiles

- Dashboard : http://localhost:8000/dashboard
- Health : http://localhost:8000/health
- API Docs : http://localhost:8000/docs (Swagger)

---

## ✨ Améliorations v2.0

- ✅ Modèle YOLO corrigé (`document_detector.pt`)
- ✅ Rogange intelligent sur région détectée
- ✅ Prétraitement avancé (CLAHE, débruitage, deskew)
- ✅ Support EasyOCR (meilleur pour photos)
- ✅ Extraction de champs améliorée
- ✅ Interface web moderne
- ✅ Gestion des photos de mauvaise qualité

---

**Version** : 2.0.0  
**Auteur** : OpenCode  
**Date** : Avril 2024
