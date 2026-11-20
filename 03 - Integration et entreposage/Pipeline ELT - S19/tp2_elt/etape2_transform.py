"""
=============================================================
TP2 ELT — Étape 2 : TRANSFORM
=============================================================
Objectif :
  - Lire les données brutes depuis SQLite (couche Raw)
  - Appliquer les transformations (nettoyage + enrichissement)
  - Stocker le résultat dans la table 'ventes_clean' (couche Métier)

Transformations réalisées :
  1. Gestion des valeurs manquantes (quantite → 0)
  2. Suppression des doublons (basée sur id)
  3. Calcul de la colonne 'total' = quantite * prix
  4. Extraction du 'mois' pour analyses temporelles
  5. Calcul du CA par produit (agrégation)

Concepts du cours appliqués :
  - Ch.2 : Transform → nettoyage, doublons, calculs métier
  - Ch.3 : ELT → transformations DANS le système cible
  - Ch.3 : Organisation en couches (brut → intermédiaire → métier)
  - Ch.2 : Agrégation → SUM, COUNT par produit
=============================================================
"""

import pandas as pd
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "data_warehouse.db")

def transform():
    """Étape TRANSFORM : nettoyer et enrichir les données dans la base."""
    conn = sqlite3.connect(DB_PATH)

    # ── Lecture depuis la couche brute ──────────────────────
    print("\n🔄 [TRANSFORM] Lecture de la couche brute...")
    df = pd.read_sql("SELECT * FROM ventes_brutes", conn)
    print(f"   Lignes initiales : {len(df)}")

    # ── 1. Valeurs manquantes ───────────────────────────────
    nb_manquants = df['quantite'].isna().sum()
    df['quantite'] = df['quantite'].fillna(0).astype(int)
    print(f"   ✅ {nb_manquants} valeur(s) manquante(s) dans 'quantite' → remplacée(s) par 0")

    # ── 2. Suppression des doublons ─────────────────────────
    nb_avant = len(df)
    df = df.drop_duplicates(subset=['id'])
    doublons = nb_avant - len(df)
    print(f"   ✅ {doublons} doublon(s) supprimé(s) → {len(df)} lignes restantes")

    # ── 3. Calcul du total ──────────────────────────────────
    df['total'] = (df['quantite'] * df['prix']).round(2)
    print(f"   ✅ Colonne 'total' calculée (quantite × prix)")

    # ── 4. Extraction du mois ───────────────────────────────
    df['date_vente'] = pd.to_datetime(df['date_vente'])
    df['mois'] = df['date_vente'].dt.to_period('M').astype(str)
    print(f"   ✅ Colonne 'mois' extraite depuis 'date_vente'")

    # ── 5. Agrégation par produit (table de synthèse) ───────
    df_agg = (df.groupby('produit')
                .agg(nb_ventes=('id', 'count'),
                     total_ca=('total', 'sum'),
                     qte_totale=('quantite', 'sum'))
                .reset_index()
                .sort_values('total_ca', ascending=False))
    df_agg['total_ca'] = df_agg['total_ca'].round(2)

    # ── Stocker les deux couches dans SQLite ────────────────
    df.to_sql('ventes_clean', conn, if_exists='replace', index=False)
    df_agg.to_sql('ventes_par_produit', conn, if_exists='replace', index=False)

    print(f"\n   📊 Résumé des données transformées :")
    print(df.to_string(index=False))
    print(f"\n   📊 CA par produit :")
    print(df_agg.to_string(index=False))

    conn.close()
    print("\n   ✅ Tables créées dans SQLite : 'ventes_clean', 'ventes_par_produit'")

if __name__ == "__main__":
    print("=" * 55)
    print("  TP2 ELT — Étape 2 : Transform")
    print("=" * 55)
    transform()
    print("\n✔  Étape 2 terminée avec succès.\n")
