"""Métriques de performance (Tâche 3.1) : throughput, latence end-to-end, lag Kafka.

- MetricsListener : écoute les QueryProgress de Spark et enregistre, à chaque
  micro-batch, le throughput (entrée/traitement) et le lag du consommateur Kafka.
- latency_stats : calcule la latence end-to-end sur les données d'un micro-batch
  (producteur -> Spark) et le délai Kafka -> Spark.

Sorties : console + CSV (results/metrics/) + tables SQLite perf_metrics / latency_metrics.
"""
from __future__ import annotations

import csv
import json
import sqlite3
from datetime import datetime
from pathlib import Path

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.streaming import StreamingQueryListener

from config import settings

PERF_TABLE = "perf_metrics"
LATENCY_TABLE = "latency_metrics"


# ---------------------------------------------------------------------------
# Petites aides de persistance (schéma fixe par table)
# ---------------------------------------------------------------------------
def _append_sqlite(table: str, row: dict) -> None:
    con = sqlite3.connect(settings.SQLITE_DB)
    try:
        cols = list(row)
        col_defs = ", ".join(f'"{c}"' for c in cols)
        placeholders = ", ".join("?" * len(cols))
        con.execute(f'CREATE TABLE IF NOT EXISTS "{table}" ({col_defs})')
        con.execute(f'INSERT INTO "{table}" ({col_defs}) VALUES ({placeholders})',
                    [row[c] for c in cols])
        con.commit()
    finally:
        con.close()


def _append_csv(table: str, row: dict) -> None:
    out_dir = Path(settings.RESULTS_DIR) / "metrics"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{table}.csv"
    new_file = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row))
        if new_file:
            writer.writeheader()
        writer.writerow(row)


def _record(table: str, row: dict, *, to_sqlite: bool, to_csv: bool) -> None:
    if to_csv:
        _append_csv(table, row)
    if to_sqlite:
        _append_sqlite(table, row)


# ---------------------------------------------------------------------------
# Listener : throughput + lag Kafka (Tâche 3.1)
# ---------------------------------------------------------------------------
class MetricsListener(StreamingQueryListener):
    def __init__(self, *, to_sqlite: bool = True, to_csv: bool = True) -> None:
        self.to_sqlite = to_sqlite
        self.to_csv = to_csv

    def onQueryStarted(self, event) -> None:  # noqa: N802
        print(f"[metrics] requête démarrée : {event.name or event.id}")

    def onQueryProgress(self, event) -> None:  # noqa: N802
        raw = event.progress.json
        progress = json.loads(raw() if callable(raw) else raw)

        duration = progress.get("durationMs") or {}
        trigger_ms = duration.get("triggerExecution")

        # Lag du consommateur Kafka : exposé par la source Kafka dans les métriques
        lag_max = lag_avg = None
        for source in progress.get("sources", []):
            metrics = source.get("metrics") or {}
            if "maxOffsetsBehindLatest" in metrics:
                lag_max = metrics.get("maxOffsetsBehindLatest")
                lag_avg = metrics.get("avgOffsetsBehindLatest")

        row = {
            "ts": progress.get("timestamp"),
            "query": progress.get("name"),
            "batch_id": progress.get("batchId"),
            "num_input_rows": progress.get("numInputRows"),
            "input_rows_per_sec": progress.get("inputRowsPerSecond"),
            "processed_rows_per_sec": progress.get("processedRowsPerSecond"),
            "trigger_exec_ms": trigger_ms,
            "kafka_max_lag": lag_max,
            "kafka_avg_lag": lag_avg,
        }
        print(
            f"[throughput] batch={row['batch_id']} rows={row['num_input_rows']} "
            f"in={_fmt(row['input_rows_per_sec'])}/s proc={_fmt(row['processed_rows_per_sec'])}/s "
            f"durée={trigger_ms}ms lag_max={lag_max}"
        )
        _record(PERF_TABLE, row, to_sqlite=self.to_sqlite, to_csv=self.to_csv)

    def onQueryIdle(self, event) -> None:  # noqa: N802 - présent dans Spark 3.5
        pass

    def onQueryTerminated(self, event) -> None:  # noqa: N802
        print(f"[metrics] requête terminée : {event.id}")


def _fmt(value) -> str:
    return f"{value:.0f}" if isinstance(value, (int, float)) else str(value)


# ---------------------------------------------------------------------------
# Latence end-to-end (calculée sur les données d'un micro-batch)
# ---------------------------------------------------------------------------
def latency_stats(valid_batch: DataFrame) -> dict | None:
    """Latence producteur->Spark et Kafka->Spark (en ms) sur un micro-batch."""
    # cast(timestamp -> double) = epoch en secondes fractionnaires -> précision ms
    enriched = valid_batch.select(
        ((F.col("processing_time").cast("double") - F.col("event_time").cast("double")) * 1000).alias("e2e_ms"),
        ((F.col("processing_time").cast("double") - F.col("kafka_timestamp").cast("double")) * 1000).alias("kafka_ms"),
    )
    agg = enriched.agg(
        F.count("*").alias("rows"),
        F.round(F.avg("e2e_ms"), 1).alias("avg_e2e_ms"),
        F.round(F.min("e2e_ms"), 1).alias("min_e2e_ms"),
        F.round(F.max("e2e_ms"), 1).alias("max_e2e_ms"),
        F.round(F.avg("kafka_ms"), 1).alias("avg_kafka_to_spark_ms"),
    ).collect()
    if not agg or agg[0]["rows"] == 0:
        return None
    row = agg[0].asDict()
    row["ts"] = datetime.now().isoformat(timespec="seconds")
    return row


def record_latency(row: dict, *, to_sqlite: bool = True, to_csv: bool = True) -> None:
    _record(LATENCY_TABLE, row, to_sqlite=to_sqlite, to_csv=to_csv)
