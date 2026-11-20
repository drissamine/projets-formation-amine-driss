# TP — Tests & monitoring ML avec Deepchecks + Evidently

Projet MLOps de tests automatisés et de monitoring de dérive pour un modèle de classification de fraude.

## Datasets
- data/reference.csv : baseline (référence)
- data/current.csv   : données "courantes" (drift simulé)

## Artefacts
- artifacts/model.joblib : pipeline sklearn entraîné
- artifacts/deepchecks_report.html : rapport tests Deepchecks (généré)
- artifacts/evidently_drift_report.html : rapport drift Evidently (généré)
- rapport.html : rapport de synthèse du travail étape par étape

## Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Sous Windows PowerShell :
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Exécution
1) (Optionnel) régénérer data + modèle
```bash
python scripts/01_generate_and_train.py
```

2) Lancer les tests Deepchecks
```bash
python scripts/02_deepchecks_tests.py
```

3) Générer le rapport de monitoring Evidently (HTML)
```bash
python scripts/03_evidently_drift_report.py
```

4) Visualiser les rapports sans serveur
```bash
python scripts/ouvrir_rapports.py
```

Ou ouvrir directement :
- rapport.html
- artifacts/deepchecks_report.html
- artifacts/evidently_drift_report.html

5) Optionnel : visualiser via serveur local
```bash
python scripts/serveur_reports.py
```

Le serveur expose :
- http://localhost:8765/rapport.html
- http://localhost:8765/artifacts/deepchecks_report.html
- http://localhost:8765/artifacts/evidently_drift_report.html

## Interprétation des résultats

Deepchecks joue le rôle de quality gate ML :
- vérifie l'intégrité des données de référence,
- compare reference.csv et current.csv,
- évalue le comportement du modèle sur les données courantes.

Evidently joue le rôle de monitoring post-déploiement :
- résume la qualité globale des données,
- compare les distributions reference/current,
- met en évidence les colonnes avec dérive statistique.

Dans les données générées, une dérive est volontairement simulée. Le rapport Evidently détecte notamment une dérive sur les colonnes `amt` et `merchant_risk`. Le rapport Deepchecks met aussi en évidence un drift de prédiction et une performance modèle limitée, ce qui montre l'intérêt du monitoring continu en production.

## Positionnement MLOps

Dans un pipeline industriel :
- Deepchecks peut être exécuté en CI/CD avant validation d'un modèle ou d'un lot de données,
- Evidently peut être lancé régulièrement pour surveiller la production,
- les rapports HTML peuvent être archivés et comparés dans le temps.
