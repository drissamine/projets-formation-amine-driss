"""
=============================================================
TP2 ELT — Étape 4 : Export pour Power BI Desktop
=============================================================
Objectif :
  - Exporter les tables transformées depuis SQLite vers CSV
  - Préparer les fichiers prêts à être importés dans Power BI
  - Afficher les statistiques finales du pipeline

Tables exportées :
  - ventes_clean.csv       → données détaillées transformées
  - ventes_par_produit.csv → CA agrégé par produit
  - ventes_par_mois.csv    → CA agrégé par mois
=============================================================
"""

import pandas as pd
import sqlite3
import os

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DB_PATH     = os.path.join(BASE_DIR, "data_warehouse.db")
EXPORT_DIR  = os.path.join(BASE_DIR, "export_powerbi")


def export_pour_powerbi():
    """Exporte toutes les tables utiles en CSV pour Power BI."""
    os.makedirs(EXPORT_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    # ── Table 1 : Ventes nettoyées (détail) ─────────────────
    df_clean = pd.read_sql("SELECT * FROM ventes_clean", conn)
    path1 = os.path.join(EXPORT_DIR, "ventes_clean.csv")
    df_clean.to_csv(path1, index=False)
    print(f"✅ Export : ventes_clean.csv ({len(df_clean)} lignes)")

    # ── Table 2 : CA par produit ─────────────────────────────
    df_produit = pd.read_sql("SELECT * FROM ventes_par_produit", conn)
    path2 = os.path.join(EXPORT_DIR, "ventes_par_produit.csv")
    df_produit.to_csv(path2, index=False)
    print(f"✅ Export : ventes_par_produit.csv ({len(df_produit)} lignes)")

    # ── Table 3 : CA par mois (calculée à la volée) ──────────
    df_mois = (df_clean.groupby('mois')
                       .agg(total_ca=('total', 'sum'),
                            nb_ventes=('id', 'count'))
                       .reset_index()
                       .sort_values('mois'))
    df_mois['total_ca'] = df_mois['total_ca'].round(2)
    path3 = os.path.join(EXPORT_DIR, "ventes_par_mois.csv")
    df_mois.to_csv(path3, index=False)
    print(f"✅ Export : ventes_par_mois.csv ({len(df_mois)} lignes)")

    conn.close()

    # ── Statistiques finales ─────────────────────────────────
    print("\n" + "─" * 45)
    print("  📊  RÉSUMÉ FINAL DU PIPELINE ELT")
    print("─" * 45)
    print(f"  Total ventes   : {df_clean['id'].nunique()} transactions")
    print(f"  CA total       : {df_clean['total'].sum():.2f} €")
    print(f"  Produit top    : {df_produit.iloc[0]['produit']} "
          f"({df_produit.iloc[0]['total_ca']:.2f} €)")
    print(f"  Mois meilleur  : {df_mois.loc[df_mois['total_ca'].idxmax(), 'mois']} "
          f"({df_mois['total_ca'].max():.2f} €)")
    print("─" * 45)
    print(f"\n  📁 Fichiers CSV exportés dans : {EXPORT_DIR}")
    print("  ➡  Ouvrir Power BI Desktop")
    print("  ➡  Accueil → Obtenir des données → Texte/CSV")
    print("  ➡  Importer ventes_clean.csv, ventes_par_produit.csv,")
    print("      ventes_par_mois.csv")
    print("\n  Visualisations à créer dans Power BI :")
    print("  1. Graphique en barres : CA par produit")
    print("     (Axe X = produit / Valeur = total_ca)")
    print("  2. Graphique linéaire  : CA par mois")
    print("     (Axe X = mois / Valeur = total_ca)")
    print("  3. Carte KPI           : CA total")
    print("     (Valeur = total_ca, agrégation = Somme)")
    print("  4. Slicers             : sur produit et mois")


if __name__ == "__main__":
    print("=" * 55)
    print("  TP2 ELT — Étape 4 : Export Power BI")
    print("=" * 55)
    export_pour_powerbi()
    print("\n✔  Étape 4 terminée avec succès.\n")
