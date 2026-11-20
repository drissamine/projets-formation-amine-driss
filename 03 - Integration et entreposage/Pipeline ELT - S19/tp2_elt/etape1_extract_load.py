"""
=============================================================
TP2 ELT — Étape 1 : EXTRACT + LOAD
=============================================================
Objectif :
  - Lire le fichier CSV source (données brutes)
  - Charger les données TELLES QUELLES dans SQLite
    (pas de transformation = principe ELT)
  - Afficher un résumé de ce qui a été chargé

Concepts du cours appliqués :
  - Ch.3 : ELT → on charge d'abord les données brutes
  - Ch.2 : Sources de données → fichier CSV (format structuré)
  - Ch.3 : Couche brute (Raw Layer) du Data Warehouse
=============================================================
"""

import pandas as pd
import sqlite3
import os

# ── Chemins ────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
CSV_PATH  = os.path.join(BASE_DIR, "ventes.csv")
DB_PATH   = os.path.join(BASE_DIR, "data_warehouse.db")

def extract():
    """Étape EXTRACT : lire le CSV source."""
    print("\n📥 [EXTRACT] Lecture du fichier source...")
    df = pd.read_csv(CSV_PATH)
    print(f"   ✅ {len(df)} lignes extraites depuis : {CSV_PATH}")
    print(f"   Colonnes : {list(df.columns)}")
    print(f"   Aperçu :\n{df.head(3).to_string(index=False)}")
    return df

def load(df: pd.DataFrame):
    """Étape LOAD : charger les données brutes dans SQLite."""
    print("\n📤 [LOAD] Chargement brut dans SQLite...")
    conn = sqlite3.connect(DB_PATH)
    # if_exists='replace' → recharge complet à chaque exécution
    df.to_sql("ventes_brutes", conn, if_exists="replace", index=False)
    loaded = pd.read_sql("SELECT COUNT(*) as n FROM ventes_brutes", conn).iloc[0, 0]
    conn.close()
    print(f"   ✅ {loaded} lignes chargées dans la table 'ventes_brutes' (base : {DB_PATH})")
    print("   ℹ️  Les données sont brutes : doublons et valeurs manquantes conservés.")

if __name__ == "__main__":
    print("=" * 55)
    print("  TP2 ELT — Étape 1 : Extract + Load")
    print("=" * 55)
    df = extract()
    load(df)
    print("\n✔  Étape 1 terminée avec succès.\n")
