"""
=============================================================
TP2 ELT — Étape 3 : ORCHESTRATION (Option B — Script autonome)
=============================================================
Objectif :
  - Exécuter le pipeline ELT complet depuis un seul script
  - Simuler l'orchestration avec un enchaînement séquentiel
  - Planifiable avec Task Scheduler (Windows) ou cron (Linux)

Avantage : ne nécessite PAS l'installation d'Airflow.
=============================================================

PLANIFICATION WINDOWS (Task Scheduler) :
  1. Ouvrir "Task Scheduler" → "Create Basic Task"
  2. Trigger : Daily à 02:00
  3. Action : "Start a program"
       Programme : python.exe  (ex: C:\Python314\python.exe)
       Arguments : pipeline_elt_complet.py
       Démarrer dans : D:\M2\S19\tp2_elt
=============================================================
"""

import sys
import os
import time
import logging
from datetime import datetime

# ── Configuration du logging ────────────────────────────────
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

log_file = os.path.join(LOG_DIR, f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger(__name__)

# ── Import des fonctions des étapes ─────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from etape1_extract_load import extract, load
from etape2_transform import transform


def run_step(name: str, func, *args, retries: int = 2):
    """
    Exécuter une étape avec gestion des erreurs et retries.
    Simule le comportement de l'orchestrateur Airflow.
    """
    for attempt in range(1, retries + 2):
        try:
            log.info(f"▶  Démarrage : {name} (tentative {attempt})")
            start = time.time()
            result = func(*args)
            elapsed = round(time.time() - start, 2)
            log.info(f"✅ Succès : {name} ({elapsed}s)")
            return result
        except Exception as e:
            log.error(f"❌ Erreur dans '{name}' : {e}")
            if attempt <= retries:
                log.info(f"   ⟳ Nouvelle tentative dans 3 secondes...")
                time.sleep(3)
            else:
                log.critical(f"   Pipeline arrêté après {retries + 1} tentatives échouées.")
                raise


def run_pipeline():
    """Pipeline ELT complet : Extract → Load → Transform."""
    log.info("=" * 55)
    log.info("  PIPELINE ELT — Démarrage")
    log.info(f"  Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info("=" * 55)

    pipeline_start = time.time()

    # ── Tâche 1 : Extract ────────────────────────────────────
    df = run_step("Tâche 1 — Extract", extract)

    # ── Tâche 2 : Load ───────────────────────────────────────
    run_step("Tâche 2 — Load", load, df)

    # ── Tâche 3 : Transform ──────────────────────────────────
    run_step("Tâche 3 — Transform", transform)

    total_time = round(time.time() - pipeline_start, 2)
    log.info("=" * 55)
    log.info(f"  PIPELINE terminé avec succès en {total_time}s")
    log.info(f"  Log enregistré : {log_file}")
    log.info("=" * 55)


if __name__ == "__main__":
    run_pipeline()
