"""Génère un rapport de monitoring de dérive avec Evidently (HTML).

Rapports:
- DataSummaryPreset : qualité globale (missing, types, etc.)
- DataDriftPreset   : drift statistique entre reference et current

Sortie:
- artifacts/evidently_drift_report.html
"""
import json
import re
from pathlib import Path
import pandas as pd

from evidently import Report
from evidently.presets import DataDriftPreset, DataSummaryPreset

EVIDENTLY_TRANSLATIONS = {
    # General headers & labels
    "Dataset Summary": "Résumé du Jeu de Données",
    "Dataset Drift": "Dérive du Jeu de Données",
    "Columns": "Colonnes",
    "Drifted Columns": "Colonnes avec Dérive",
    "Share of Drifted Columns": "Part de Colonnes avec Dérive",
    "Data Drift Summary": "Résumé de la Dérive des Données",
    "Metric": "Métrique",
    "Current": "Courant",
    "Reference": "Référence",
    "Column": "Colonne",
    "Type": "Type",
    "Reference Distribution": "Distribution de Référence",
    "Current Distribution": "Distribution Courante",
    "Data Drift": "Dérive des Données",
    "Stat Test": "Test Statistique",
    "Drift Score": "Score de Dérive",
    "Detected": "Détectée",
    "Not Detected": "Non détectée",
    "DATA DRIFT": "DÉRIVE DES DONNÉES",
    "DATA DISTRIBUTION": "DISTRIBUTION DES DONNÉES",
    
    # Table rows (metrics labels in dataset summary)
    "id column": "Colonne d'identifiant (ID)",
    "target column": "Colonne cible (Target)",
    "prediction column": "Colonne de prédiction",
    "date column": "Colonne de date",
    "number of columns": "Nombre de colonnes",
    "number of rows": "Nombre de lignes",
    "missing values": "Valeurs manquantes",
    "categorical columns": "Colonnes catégorielles",
    "numeric columns": "Colonnes numériques",
    "text columns": "Colonnes de texte",
    "datetime columns": "Colonnes temporelles (Datetime)",
    "empty columns": "Colonnes vides",
    "constant columns": "Colonnes constantes",
    "almost constant features": "Caractéristiques presque constantes",
    "duplicated columns": "Colonnes dupliquées",
    "almost duplicated features": "Caractéristiques presque dupliquées",

    # Metric labels in rich data panels
    "count": "Nombre total",
    "missing": "Valeurs manquantes",
    "unique": "Valeurs uniques",
    "most_common": "Valeur la plus fréquente",
    "most_common_percentage": "Part de la valeur la plus fréquente",
    "min": "Minimum",
    "max": "Maximum",
    "mean": "Moyenne",
    "std": "Écart-type",
    "low": "Faible",
    "med": "Moyen",
    "high": "Élevé",

    # Stat tests
    "Wasserstein distance (normed)": "Distance de Wasserstein (normalisée)",
    "Jensen-Shannon distance": "Distance de Jensen-Shannon",
}


def translate_text(text: str) -> str:
    if not isinstance(text, str):
        return text
    
    # Direct match translation
    if text in EVIDENTLY_TRANSLATIONS:
        return EVIDENTLY_TRANSLATIONS[text]
    
    # Dynamic/Regex translations for dataset drift counters
    if text.startswith("Dataset Drift is NOT detected."):
        # e.g., Dataset Drift is NOT detected. Dataset drift detection threshold is 0.5
        threshold = text.split("is ")[-1]
        return f"Aucune dérive globale du jeu de données n'est détectée (seuil de détection : {threshold})."
    
    if text.startswith("Dataset Drift is detected."):
        threshold = text.split("is ")[-1]
        return f"Une dérive globale du jeu de données est détectée (seuil de détection : {threshold})."

    if "Drift is detected for" in text:
        # e.g., Drift is detected for 40.0% of columns (2 out of 5).
        m = re.match(r"Drift is detected for ([\d\.]+)% of columns \((\d+) out of (\d+)\)\.", text)
        if m:
            pct, cnt, tot = m.groups()
            return f"Une dérive est détectée pour {pct}% des colonnes ({cnt} sur {tot})."
            
    return text


def translate_json_obj(obj):
    """Traduit récursivement l'ensemble de l'état JSON de l'interface Evidently."""
    if isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
            if k in ["title", "label", "value", "header", "description", "data_drift", "stattest_name"]:
                if isinstance(v, str):
                    new_dict[k] = translate_text(v)
                elif isinstance(v, list):
                    new_dict[k] = [translate_text(x) if isinstance(x, str) else translate_json_obj(x) for x in v]
                else:
                    new_dict[k] = translate_json_obj(v)
            else:
                new_dict[k] = translate_json_obj(v)
        return new_dict
    elif isinstance(obj, list):
        return [translate_json_obj(x) for x in obj]
    elif isinstance(obj, str):
        return translate_text(obj)
    else:
        return obj


def post_process_evidently_html(html_path: Path) -> None:
    """Charge le fichier HTML, extrait la variable JSON d'état, la traduit et la réinjecte."""
    if not html_path.exists():
        return
    
    content = html_path.read_text(encoding="utf-8")
    
    # 1. Extraction du bloc de script JSON d'état
    match = re.search(r'var\s+(metric_[a-f0-9]+)\s*=\s*(\{.*?\});', content, re.DOTALL)
    if not match:
        print("  Avertissement: bloc JSON d'état Evidently introuvable.")
        return
        
    var_name = match.group(1)
    json_str = match.group(2)
    
    # 2. Traduction récursive du JSON
    data = json.loads(json_str)
    translated_data = translate_json_obj(data)
    
    # 3. Réinjection du JSON traduit
    translated_json_str = json.dumps(translated_data, ensure_ascii=False)
    content = content.replace(
        f"var {var_name} = {json_str};",
        f"var {var_name} = {translated_json_str};",
        1
    )
    
    # 4. Remplacement de quelques termes globaux résiduels dans l'application
    content = content.replace('"Share of drifted features"', '"Part de colonnes avec dérive"')
    content = content.replace('"Dataset Summary"', '"Résumé du Jeu de Données"')
    content = content.replace('"Data Drift Summary"', '"Résumé de la Dérive des Données"')
    content = content.replace('"Data Quality"', '"Qualité des Données"')
    content = content.replace('"Data Drift"', '"Dérive des Données"')
    
    # Sauvegarde
    html_path.write_text(content, encoding="utf-8")
    print(f"  Rapport Evidently post-traité et traduit en français avec succès.")


def main():
    repo = Path(__file__).resolve().parents[1]
    ref = pd.read_csv(repo / "data" / "reference.csv")
    cur = pd.read_csv(repo / "data" / "current.csv")

    report = Report(metrics=[DataSummaryPreset(), DataDriftPreset()])
    snapshot = report.run(reference_data=ref, current_data=cur)

    out = repo / "artifacts" / "evidently_drift_report.html"
    out.parent.mkdir(exist_ok=True)
    snapshot.save_html(str(out))
    print(f"OK: rapport Evidently initial généré -> {out}")

    # Post-traitement de traduction
    post_process_evidently_html(out)


if __name__ == "__main__":
    main()
