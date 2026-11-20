"""
=============================================================
TP2 ELT — Étape 3 : ORCHESTRATION (Option A — Apache Airflow)
=============================================================
Objectif :
  - Définir un DAG Airflow qui orchestre le pipeline ELT
  - Tâche 1 : extract  → lit le CSV
  - Tâche 2 : load     → charge les données brutes dans SQLite
  - Tâche 3 : transform → nettoie et enrichit les données
  - Planification : exécution quotidienne (@daily)

Concepts du cours appliqués :
  - Ch.4/5 : Orchestration = coordonner, planifier, dépendances
  - Ch.4/5 : DAG = Directed Acyclic Graph (graphe sans cycle)
  - Ch.4/5 : PythonOperator = tâche qui exécute une fonction Python
  - Ch.4/5 : Dépendances : t1 >> t2 >> t3
  - Ch.4/5 : Scheduler : @daily = cron-based scheduling
=============================================================

INSTALLATION AIRFLOW :
  pip install "apache-airflow==2.8.0" --constraint
    "https://raw.githubusercontent.com/apache/airflow/constraints-2.8.0/constraints-3.11.txt"

  airflow db init
  airflow users create --username admin --password admin \
      --firstname Admin --lastname TP2 --role Admin --email tp2@m2.com

  airflow webserver --port 8080   (dans un terminal)
  airflow scheduler               (dans un autre terminal)

  Puis copiez ce fichier dans : ~/airflow/dags/elt_tp2.py
  Interface web : http://localhost:8080
=============================================================
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import sqlite3
import os

# ── Chemins absolus (à adapter selon votre machine) ─────────
BASE_DIR = r"d:\M2\S19\tp2_elt"
CSV_PATH = os.path.join(BASE_DIR, "ventes.csv")
DB_PATH  = os.path.join(BASE_DIR, "data_warehouse.db")

# ── Arguments par défaut du DAG ─────────────────────────────
default_args = {
    "owner": "etudiant_m2",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 2,                         # 2 tentatives en cas d'échec
    "retry_delay": timedelta(minutes=5),  # attente entre tentatives
}

# ── Fonctions métier ─────────────────────────────────────────

def extract(**context):
    """Tâche 1 — Extract : lire le CSV source."""
    df = pd.read_csv(CSV_PATH)
    print(f"[EXTRACT] {len(df)} lignes lues depuis {CSV_PATH}")
    # Passer les données via XCom pour la tâche suivante (optionnel)
    context['ti'].xcom_push(key='nb_lignes', value=len(df))

def load(**context):
    """Tâche 2 — Load : charger les données brutes dans SQLite."""
    df = pd.read_csv(CSV_PATH)
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("ventes_brutes", conn, if_exists="replace", index=False)
    conn.close()
    print(f"[LOAD] {len(df)} lignes brutes chargées dans 'ventes_brutes'")

def transform(**context):
    """Tâche 3 — Transform : nettoyer et enrichir dans la base."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM ventes_brutes", conn)

    # Nettoyage
    df['quantite'] = df['quantite'].fillna(0).astype(int)
    df = df.drop_duplicates(subset=['id'])

    # Enrichissement
    df['total'] = (df['quantite'] * df['prix']).round(2)
    df['date_vente'] = pd.to_datetime(df['date_vente'])
    df['mois'] = df['date_vente'].dt.to_period('M').astype(str)

    # Agrégation par produit
    df_agg = (df.groupby('produit')
                .agg(nb_ventes=('id', 'count'),
                     total_ca=('total', 'sum'),
                     qte_totale=('quantite', 'sum'))
                .reset_index()
                .sort_values('total_ca', ascending=False))

    # Stocker
    df.to_sql('ventes_clean', conn, if_exists='replace', index=False)
    df_agg.to_sql('ventes_par_produit', conn, if_exists='replace', index=False)
    conn.close()
    print(f"[TRANSFORM] Tables 'ventes_clean' et 'ventes_par_produit' mises à jour.")

# ── Définition du DAG ────────────────────────────────────────
with DAG(
    dag_id="elt_tp2_ventes",
    description="Pipeline ELT : Extract → Load → Transform (TP2 M2 IA & Data)",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule_interval="@daily",   # exécution quotidienne (cron : 0 0 * * *)
    catchup=False,                # ne pas rejouer les exécutions passées
    tags=["elt", "tp2", "m2"],
) as dag:

    t1_extract = PythonOperator(
        task_id="extract",
        python_callable=extract,
    )

    t2_load = PythonOperator(
        task_id="load",
        python_callable=load,
    )

    t3_transform = PythonOperator(
        task_id="transform",
        python_callable=transform,
    )

    # ── Dépendances : extract → load → transform ─────────────
    # t2 ne démarre que si t1 réussit
    # t3 ne démarre que si t2 réussit
    t1_extract >> t2_load >> t3_transform
