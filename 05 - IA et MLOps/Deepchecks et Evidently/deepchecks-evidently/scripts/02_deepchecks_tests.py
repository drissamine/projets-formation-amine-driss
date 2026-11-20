"""Exécute des tests automatiques avec Deepchecks (tabular).

Suites utilisées:
1) data_integrity() : qualité intrinsèque des données de référence
2) train_test_validation() : drift entre reference et current
3) model_evaluation() : évaluation modèle sur current

Sortie:
- artifacts/deepchecks_report.html  (page avec iframes)
- artifacts/_integrity.html
- artifacts/_ttv.html
- artifacts/_model.html

Pour visualiser : lancer le serveur puis ouvrir http://localhost:8765
    python -m http.server 8765 -d artifacts/
"""
import json
import re
from html.parser import HTMLParser
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import plotly.io as pio

from deepchecks.tabular import Dataset
from deepchecks.tabular.suites import data_integrity, train_test_validation, model_evaluation
from sklearn.inspection import permutation_importance

_to_html_orig = pio.to_html
def _to_html_fr(fig, **kwargs):
    kwargs.setdefault("config", {})
    kwargs["config"].setdefault("locale", "fr")
    return _to_html_orig(fig, **kwargs)
pio.to_html = _to_html_fr


def _inject_locale_in_state(state: dict) -> None:
    for model_id, model_data in state.get("state", {}).items():
        s = model_data.get("state", {})
        for key in list(s.keys()):
            v = s[key]
            if isinstance(v, dict) and "_config" in v:
                v["_config"]["locale"] = "fr"


DEEPCHECKS_REPLACEMENTS = {
    # Headers
    ">Status<": ">Statut<",
    ">Check<": ">Test<",
    ">Condition<": ">Condition<",
    ">More Info<": ">Plus d'infos<",
    "<h2>Check With Conditions Output</h2>": "<h2>Détails des Tests et Conditions</h2>",
    "<h2>Conditions Summary</h2>": "<h2>Résumé des Conditions de Test</h2>",
    "<h5><b>Conditions Summary</b></h5>": "<h5><b>Résumé des Conditions</b></h5>",
    "<th>Check</th>": "<th>Test</th>",
    "<th>Status</th>": "<th>Statut</th>",
    "<th>Condition</th>": "<th>Condition</th>",
    "<th>More Info</th>": "<th>Plus d'infos</th>",
    
    # Global Suite Titles
    "Data Integrity Suite</h1>": "Suite d'Intégrité des Données</h1>",
    "Train Test Validation Suite</h1>": "Suite de Validation Train-Test</h1>",
    "Model Evaluation Suite</h1>": "Suite d'Évaluation du Modèle</h1>",
    "<h2>Data Integrity Suite</h2>": "<h2>Suite d'Intégrité des Données</h2>",
    "<h2>Train Test Validation Suite</h2>": "<h2>Suite de Validation Train-Test</h2>",
    "<h2>Model Evaluation Suite</h2>": "<h2>Suite d'Évaluation du Modèle</h2>",
    
    # Sections and extra headers
    "<h2>Check Without Conditions Output</h2>": "<h2>Détails des Tests sans Condition</h2>",
    "<h2>Other Checks That Weren't Displayed</h2>": "<h2>Autres Tests non Affichés</h2>",
    "<h5><b>Additional Outputs</b></h5>": "<h5><b>Visualisations Additionnelles</b></h5>",
    "New Category Train Test": "Nouvelle catégorie dans le jeu de test",
    "Feature Label Correlation Change": "Changement de corrélation caractéristiques-étiquette",
    "Confusion Matrix Report - Train Dataset": "Rapport de la matrice de confusion - Jeu d'entraînement",
    "Confusion Matrix Report - Test Dataset": "Rapport de la matrice de confusion - Jeu de test",
    "Calibration Metric - Train Dataset": "Métrique de calibration - Jeu d'entraînement",
    "Calibration Metric - Test Dataset": "Métrique de calibration - Jeu de test",
    
    # Common Check Names in tables and titles
    "Feature-Feature Correlation": "Corrélation Caractéristiques-Caractéristiques",
    "Feature Label Correlation": "Corrélation Caractéristiques-Étiquette",
    "Special Characters": "Caractères Spéciaux",
    "Single Value in Column": "Valeur Unique dans la Colonne",
    "Mixed Data Types": "Types de Données Mixtes",
    "String Mismatch": "Écarts de Chaînes de Caractères",
    "Data Duplicates": "Doublons de Données",
    "Mixed Nulls": "Nulles Mixtes",
    "String Length Out Of Bounds": "Longueur de Chaîne Hors Limites",
    "Conflicting Labels": "Étiquettes Conflictuelles",
    "Feature Drift": "Dérive des Caractéristiques (Drift)",
    "Label Drift": "Dérive de l'Étiquette",
    "Multivariate Drift": "Dérive Multivariée (Drift)",
    "Category Mismatch Train Test": "Incohérence des Catégories Train-Test",
    "Dominant Similarities": "Similitudes Dominantes",
    "Missing Value Report": "Rapport des Valeurs Manquantes",
    "Class Imbalance": "Déséquilibre des Classes",
    "Date Drift": "Dérive des Dates",
    "Index Drift": "Dérive de l'Index",
    "Train Test Samples Mix": "Mélange d'Échantillons Train-Test",
    "Datasets Size Comparison": "Comparaison de Taille des Jeux de Données",
    "Model Inference Time - Train Dataset": "Temps d'Inférence du Modèle - Jeu d'Entraînement",
    "Model Inference Time - Test Dataset": "Temps d'Inférence du Modèle - Jeu de Test",
    "ROC Report - Train Dataset": "Rapport ROC - Jeu d'Entraînement",
    "ROC Report - Test Dataset": "Rapport ROC - Jeu de Test",
    "Prediction Drift": "Dérive des Prédictions",
    "Confusion Matrix Report": "Rapport de la Matrice de Confusion",
    "Unused Features": "Caractéristiques Inutilisées",
    "Train Test Performance": "Performance Train-Test",
    "Boosting Overfit": "Surapprentissage du Boosting",
    "Weak Segments Performance - Train Dataset": "Performance des Segments Faibles - Jeu d'Entraînement",
    "Weak Segments Performance - Test Dataset": "Performance des Segments Faibles - Jeu de Test",
    "Columns Info": "Informations sur les Colonnes",
    "Columns Info - Train Dataset": "Informations sur les Colonnes - Jeu d'Entraînement",
    
    # Results text
    "Passed for ": "Réussi pour ",
    " relevant columns": " colonnes pertinentes",
    " relevant column": " colonne pertinente",
    " columns passed": " colonnes ont réussi",
    " column passed": " colonne a réussi",
    "relevant features": "caractéristiques pertinentes",
    "relevant feature": "caractéristique pertinente",
    "No relevant columns to check were found": "Aucune colonne pertinente à tester n'a été trouvée",
    "Found 0% duplicate data": "0% de données dupliquées trouvées",
    "Ratio of samples with conflicting labels: 0%": "Ratio d'échantillons avec étiquettes conflictuelles : 0%",
    "Not more than 0 pairs are correlated above 0.9": "Pas plus de 0 paires corrélées au-dessus de 0.9",
    "Correlation is greater than 0.9 for pairs": "La corrélation est supérieure à 0.9 pour les paires",
    "Ratio of samples containing solely special character is less or equal to 0.1%": "Le ratio d'échantillons contenant uniquement des caractères spéciaux est inférieur ou égal à 0.1%",
    "Does not contain only a single value": "Ne contient pas une seule valeur unique",
    "Rare data types in column are either more than 10% or less than 1% of the data": "Les types de données rares dans la colonne sont soit supérieurs à 10%, soit inférieurs à 1% des données",
    "No string variants": "Aucune variante de chaîne de caractères trouvée",
    "Number of different null types is less or equal to 1": "Le nombre de types de valeurs nulles différents est inférieur ou égal à 1",
    "Ratio of string length outliers is less or equal to 0%": "Le ratio d'outliers de longueur de chaîne est inférieur ou égal à 0%",
    "Ambiguous sample ratio is less or equal to 0%": "Le ratio d'échantillons ambigus est inférieur ou égal à 0%",
    "Passed for all features": "Réussi pour toutes les caractéristiques",
    "Passed for 4 columns out of 4 columns.": "Réussi pour 4 colonnes sur 4 colonnes.",
    "AUC score for all the classes is greater than 0.7": "Le score AUC pour toutes les classes est supérieur à 0.7",
    "Average model inference time for one sample is less than 0.001": "Le temps d'inférence moyen pour un échantillon est inférieur à 0.001s",
    "Found classes with AUC below threshold:": "Classes trouvées avec une AUC sous le seuil :",
    "Found average inference time (seconds):": "Temps d'inférence moyen trouvé (secondes) :",
    "Prediction drift score < 0.15": "Score de dérive des prédictions < 0.15",
    "Found model prediction Kolmogorov-Smirnov drift score of": "Score de dérive Kolmogorov-Smirnov des prédictions trouvé :",
    "Check is irrelevant for classification tasks": "Le test est non applicable pour les tâches de classification",
    "The suite is composed of various checks such as:": "La suite est composée de différents tests tels que :",
    "Calculate the ROC curve for each class.": "Calcule la courbe ROC pour chaque classe.",
    "Checks for pairwise correlation between the features.": "Vérifie la corrélation par paire entre les caractéristiques.",
    "Show Description": "Afficher la Description",
    "Hide Description": "Masquer la Description",
    "Read More...": "En savoir plus...",
}


def make_individual_html(result, path: Path) -> None:
    """Sauvegarde un rapport individuel avec locale injectée dans le widget state et traduction en français."""
    if path.exists():
        path.unlink()
    result.save_as_html(str(path), as_widget=False, requirejs=False, connected=False)
    raw = path.read_text(encoding="utf-8")

    # Application des traductions en français
    for eng, fre in DEEPCHECKS_REPLACEMENTS.items():
        raw = raw.replace(eng, fre)

    # Supprime requirejs pour que le bundle Plotly embarqué s'attache à window.Plotly
    # et convertit les graphes en appels directs. C'est plus fiable en ouverture file://.
    raw = re.sub(
        r'<script type="text/javascript">\s*var requirejs,require,define;.*?</script>',
        '',
        raw,
        flags=re.DOTALL
    )
    raw = re.sub(
        r'<script type="text/javascript">\s*require\(\["plotly"\], function\(Plotly\) \{(.*?)\}\);\s*</script>',
        r'<script type="text/javascript">(function(Plotly) {\1})(window.Plotly);</script>',
        raw,
        flags=re.DOTALL,
    )

    collector = _ScriptCollector()
    collector.feed(raw)
    for typ, content in collector.scripts:
        if typ and "widget-state" in typ:
            try:
                state = json.loads(content.strip())
                _inject_locale_in_state(state)
                raw = raw.replace(
                    f'<script type="{typ}">{content}</script>',
                    f'<script type="{typ}">' + json.dumps(state, ensure_ascii=False) + '</script>',
                    1,
                )
            except json.JSONDecodeError:
                pass

    path.write_text(raw, encoding="utf-8")


class _ScriptCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts: list[tuple[str | None, str]] = []
        self._type: str | None = None
        self._parts: list[str] = []
        self._capture = False

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self._capture = True
            self._type = dict(attrs).get("type")
            self._parts = []

    def handle_endtag(self, tag):
        if tag == "script" and self._capture:
            self.scripts.append((self._type, "".join(self._parts)))
            self._capture = False

    def handle_data(self, data):
        if self._capture:
            self._parts.append(data)


def main():
    repo = Path(__file__).resolve().parents[1]
    df_ref = pd.read_csv(repo / "data" / "reference.csv")
    df_cur = pd.read_csv(repo / "data" / "current.csv")

    artifact = joblib.load(repo / "artifacts" / "model.joblib")
    model = artifact["model"]
    features = artifact["features"]
    target = artifact["target"]

    cat_features = ["gender", "merchant_risk"]
    ds_ref = Dataset(df_ref[features + [target]], label=target, cat_features=cat_features)
    ds_cur = Dataset(df_cur[features + [target]], label=target, cat_features=cat_features)
    permutation_result = permutation_importance(
        estimator=model,
        X=df_cur[features],
        y=df_cur[target],
        scoring="roc_auc",
        n_repeats=30,
        random_state=42,
    )
    importance = np.maximum(permutation_result.importances_mean, 0)
    if importance.sum() == 0:
        importance = np.ones(len(features))
    feature_importance = pd.Series(importance / importance.sum(), index=features)

    suites = [
        ("_integrity", "Intégrité des données (Référence)", data_integrity().run(ds_ref)),
        ("_ttv", "Validation Train-Test (Référence vs Current)",
         train_test_validation().run(train_dataset=ds_ref, test_dataset=ds_cur)),
        ("_model", "Évaluation du modèle (sur Current)",
         model_evaluation().run(
             train_dataset=ds_ref,
             test_dataset=ds_cur,
             model=model,
             feature_importance=feature_importance,
         )),
    ]

    out_dir = repo / "artifacts"
    out_dir.mkdir(exist_ok=True)

    sub_files = []
    for key, title, result in suites:
        path = out_dir / f"{key}.html"
        make_individual_html(result, path)
        sub_files.append((title, path.name))
        print(f"  {path.name} généré")

    wrapper = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Deepchecks — Rapport Global</title>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0b0f19;
      --card: rgba(17, 24, 39, 0.7);
      --border: rgba(255, 255, 255, 0.08);
      --text: #f3f4f6;
      --text-muted: #9ca3af;
      --primary: #6366f1;
      --primary-glow: rgba(99, 102, 241, 0.15);
      --success: #10b981;
      --info: #0ea5e9;
      --warning: #f59e0b;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; transition: all 0.2s ease; }
    body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      padding: 3rem 2rem;
      background-image: radial-gradient(circle at 50% 10%, rgba(99, 102, 241, 0.04) 0%, transparent 50%);
    }
    .container { max-width: 1100px; width: 100%; margin: 0 auto; display: flex; flex-direction: column; gap: 2.5rem; }
    header h1 {
      font-family: 'Outfit', sans-serif;
      font-size: 2.2rem;
      font-weight: 800;
      background: linear-gradient(135deg, #ffffff 40%, #a5b4fc 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      letter-spacing: -0.03em;
      margin-bottom: 0.5rem;
    }
    header p { color: var(--text-muted); font-size: 0.95rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-top: 1rem; }
    .card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 2rem;
      backdrop-filter: blur(10px);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      height: 250px;
      position: relative;
      overflow: hidden;
    }
    .card::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 4px; }
    .card:nth-child(1)::before { background: var(--success); }
    .card:nth-child(2)::before { background: var(--info); }
    .card:nth-child(3)::before { background: var(--warning); }
    
    .card:nth-child(1):hover { border-color: rgba(16, 185, 129, 0.3); box-shadow: 0 8px 24px rgba(16, 185, 129, 0.08); }
    .card:nth-child(2):hover { border-color: rgba(14, 165, 233, 0.3); box-shadow: 0 8px 24px rgba(14, 165, 233, 0.08); }
    .card:nth-child(3):hover { border-color: rgba(245, 158, 11, 0.3); box-shadow: 0 8px 24px rgba(245, 158, 11, 0.08); }
    
    .card-title { font-family: 'Outfit', sans-serif; font-size: 1.25rem; font-weight: 700; color: #ffffff; margin-bottom: 0.5rem; }
    .card-desc { color: var(--text-muted); font-size: 0.88rem; line-height: 1.5; }
    
    .btn-link {
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      padding: 0.65rem 1.25rem;
      border-radius: 10px;
      font-size: 0.85rem;
      font-weight: 600;
      color: #ffffff;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.08);
      cursor: pointer;
      margin-top: 1.5rem;
      width: fit-content;
    }
    .btn-link:hover {
      background: #ffffff;
      color: var(--bg);
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(255, 255, 255, 0.15);
    }
    .notice {
      background: rgba(245, 158, 11, 0.05);
      border: 1px solid rgba(245, 158, 11, 0.15);
      color: #fbbf24;
      padding: 1rem;
      border-radius: 10px;
      font-size: 0.85rem;
      display: flex;
      align-items: center;
      gap: 0.75rem;
      line-height: 1.4;
    }
    footer { text-align: center; color: var(--text-muted); font-size: 0.8rem; margin-top: 2rem; border-top: 1px solid var(--border); padding-top: 1.5rem; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>Deepchecks — Suite Globale de Tests</h1>
      <p>Rapports détaillés de validation de l'intégrité, de la dérive et des performances du modèle.</p>
    </header>

    <div class="notice">
      <span>💡</span>
      <span><strong>Accès Direct Activé :</strong> Les rapports ci-dessous s'ouvrent directement dans votre navigateur. Aucun serveur web local n'est requis pour visualiser ces fichiers.</span>
    </div>

    <div class="grid">
"""
    for title, fname in sub_files:
        desc = ""
        if "_integrity" in fname:
            desc = "Vérifie les anomalies de structure, les doublons, les types erronés et la conformité globale du jeu de données de référence."
        elif "_ttv" in fname:
            desc = "Compare le jeu d'entraînement (référence) et le jeu courant pour identifier la fuite de données et le glissement de caractéristiques."
        else:
            desc = "Évalue les métriques clés de performance du classifieur de fraude et détaille la distribution des erreurs de prédictions."

        wrapper += f"""      <div class="card">
        <div>
          <div class="card-title">{title}</div>
          <div class="card-desc">{desc}</div>
        </div>
        <a href="{fname}" target="_blank" class="btn-link">
          Consulter le rapport
          <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </a>
      </div>
"""
    wrapper += """    </div>

    <footer>
      Suite de Validation Tabulaire Deepchecks
    </footer>
  </div>
</body>
</html>"""

    (out_dir / "deepchecks_report.html").write_text(wrapper, encoding="utf-8")
    print(f"OK: rapport Deepchecks généré -> {out_dir / 'deepchecks_report.html'}")

    # Copie du rapport Data Integrity propre, traduit et fonctionnel hors-ligne vers output.html à la racine du projet
    import shutil
    shutil.copy(out_dir / "_integrity.html", repo / "output.html")
    print(f"OK: copie de _integrity.html vers la racine -> {repo / 'output.html'}")

    print(f"\nPour visualiser, lance :")
    print(f"    cd {out_dir}")
    print(f"    python -m http.server 8765")
    print(f"    puis ouvre http://localhost:8765/deepchecks_report.html")


if __name__ == "__main__":
    main()
