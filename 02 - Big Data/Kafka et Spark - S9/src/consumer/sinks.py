"""Sorties des résultats agrégés (Tâche 2.3) : fichiers CSV/JSON + SQLite.

Conçu pour foreachBatch : on reçoit un DataFrame Spark statique (un micro-batch),
on collecte ses lignes (les agrégats sont petits) puis on écrit :
  - results/<requete>/<AAAA-MM-JJ>/<requete>_<HHMMSS_us>.csv et .json
  - une table <requete> dans la base SQLite streaming_analytics.db

Volontairement sans pandas : pyspark.toPandas() importe distutils, supprimé de
Python 3.12+. On reste sur la bibliothèque standard (csv, json, sqlite3).
"""
from __future__ import annotations

import csv
import json
import sqlite3
from datetime import date, datetime
from pathlib import Path

from pyspark.sql import DataFrame

from config import settings


def _to_serializable(value):
    """Rend une valeur sérialisable (timestamps -> ISO 8601)."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def _write_files(columns: list[str], rows: list[dict], query_name: str, ts: datetime) -> None:
    """Écrit un CSV et un JSON, rangés par requête puis par date."""
    date_dir = Path(settings.RESULTS_DIR) / query_name / ts.strftime("%Y-%m-%d")
    date_dir.mkdir(parents=True, exist_ok=True)
    base = date_dir / f"{query_name}_{ts.strftime('%H%M%S_%f')}"

    with open(f"{base}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({c: _to_serializable(row.get(c)) for c in columns})

    with open(f"{base}.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2, default=_to_serializable)


def _write_sqlite(columns: list[str], rows: list[dict], query_name: str) -> None:
    """Ajoute le batch dans la table SQLite du même nom que la requête."""
    con = sqlite3.connect(settings.SQLITE_DB)
    try:
        col_defs = ", ".join(f'"{c}"' for c in columns)
        con.execute(f'CREATE TABLE IF NOT EXISTS "{query_name}" ({col_defs})')
        placeholders = ", ".join("?" * len(columns))
        data = [[_to_serializable(row.get(c)) for c in columns] for row in rows]
        con.executemany(
            f'INSERT INTO "{query_name}" ({col_defs}) VALUES ({placeholders})', data
        )
        con.commit()
    finally:
        con.close()


def write_batch(batch_df: DataFrame, query_name: str, batch_id: int,
                *, files: bool = True, sqlite: bool = True) -> int:
    """Persiste un micro-batch agrégé. Renvoie le nombre de lignes écrites (0 si vide)."""
    collected = batch_df.collect()
    if not collected:
        return 0

    ts = datetime.now()
    stamp = ts.isoformat(timespec="seconds")
    columns = ["batch_id", *batch_df.columns, "ingested_at"]
    rows = []
    for record in collected:
        row = {"batch_id": batch_id}
        row.update(record.asDict())
        row["ingested_at"] = stamp
        rows.append(row)

    if files:
        _write_files(columns, rows, query_name, ts)
    if sqlite:
        _write_sqlite(columns, rows, query_name)
    return len(rows)
