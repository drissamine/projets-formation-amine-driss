# Document Detection Project - Specification

## Objectif
Système de détection et classification de documents d'identité pour intégration React.

## Documents à détecter
1. **Carte d'identité nationale** (CNI, CIN, ID card)
2. **Permis de conduire** (Driver's license)
3. **Titre de séjour** (Residence permit, permesso di soggiorno)
4. **Passeport** (Passport)

## Architecture

```
document_detection/
├── dataset/              # Images et annotations
│   ├── images/
│   └── labels/
├── models/              # Modèles entraînés
├── src/
│   ├── train.py        # Entraînement YOLOv8
│   ├── predict.py      # Prédiction
│   └── validate.py   # Évaluation
├── api/               # FastAPI
│   └── main.py
├── notebook/           # Jupyter experiments
└── requirements.txt
```

## Pipeline

1. **Dataset Collection** → Web scraping images documents
2. **Filtering** → Nettoyage données invalides
3. **Annotation** → LabelImg / Roboflow
4. **Training** → YOLOv8 fine-tuning
5. **Export** → ONNX pour compatibilité
6. **API** → FastAPI endpoint
7. **React Integration** → Fetch API depuis React

## Classes (YOLO format)

```
0: id_card      (Carte d'identité nationale)
1: driver_license  (Permis de conduire)
2: residence_permit (Titre de séjour)
3: passport    (Passeport)
```

## Scraping Strategy
- Sources: Google Images, Bing, dataset publics
- Outils: icrawler, selenium, requests
- Filtres: qualité, taille, format
- Validation: examen manuel des images

## Métriques
- mAP@0.5 > 0.8
- Precision > 0.85
- Recall > 0.85
- Inference < 100ms par image