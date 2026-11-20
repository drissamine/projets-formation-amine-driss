"""Monitoring des performances du pipeline (Tâche 3.1).

Enregistre un StreamingQueryListener (throughput + lag Kafka) et calcule la
latence end-to-end par micro-batch. Idéal à lancer EN CONTINU pendant que le
producteur tourne, pour des mesures réalistes.

Exemples :
    # Monitoring temps réel (à lancer puis produire des événements en parallèle)
    python -m src.consumer.metrics_app

    # Mesure sur le backlog existant puis arrêt
    python -m src.consumer.metrics_app --once --from-beginning
"""
from __future__ import annotations

import argparse
import sys

from pyspark.sql import DataFrame

from config import settings
from src.common.spark_schema import parse_kafka_stream, split_valid_invalid
from src.consumer import metrics
from src.consumer.spark_consumer import build_spark, read_kafka


def main() -> int:
    # Affichage temps réel même quand la sortie est redirigée vers un fichier
    sys.stdout.reconfigure(line_buffering=True)
    args = parse_args()
    spark = build_spark("metrics-monitor")

    listener = metrics.MetricsListener(to_sqlite=not args.no_sqlite, to_csv=not args.no_files)
    spark.streams.addListener(listener)

    raw = read_kafka(spark, args)
    parsed = parse_kafka_stream(raw)
    valid, _invalid = split_valid_invalid(parsed)

    def _batch(batch_df: DataFrame, batch_id: int) -> None:
        stats = metrics.latency_stats(batch_df)
        if stats is None:
            return
        stats["batch_id"] = batch_id
        print(
            f"[latency] batch={batch_id} rows={stats['rows']} "
            f"e2e avg={stats['avg_e2e_ms']}ms min={stats['min_e2e_ms']}ms max={stats['max_e2e_ms']}ms "
            f"| kafka->spark avg={stats['avg_kafka_to_spark_ms']}ms"
        )
        metrics.record_latency(stats, to_sqlite=not args.no_sqlite, to_csv=not args.no_files)

    trigger = {"availableNow": True} if args.once else {"processingTime": "5 seconds"}
    query = (
        valid.writeStream.outputMode("append")
        .foreachBatch(_batch)
        .queryName("latency-monitor")
        .trigger(**trigger)
        .start()
    )

    print(f"[app] monitoring démarré (trigger={'availableNow' if args.once else '5s'}) "
          f"| métriques -> console"
          f"{' + csv' if not args.no_files else ''}"
          f"{' + sqlite' if not args.no_sqlite else ''}")

    query.awaitTermination()
    return 0


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Monitoring de performance Spark (Tâche 3.1)")
    p.add_argument("--bootstrap", default=settings.KAFKA_BOOTSTRAP_SERVERS)
    p.add_argument("--topic", default=settings.KAFKA_TOPIC)
    p.add_argument("--from-beginning", action="store_true",
                   help="Lire depuis le début du topic (startingOffsets=earliest)")
    p.add_argument("--once", action="store_true",
                   help="Traiter le backlog puis s'arrêter (trigger availableNow)")
    p.add_argument("--no-files", action="store_true", help="Ne pas écrire les CSV")
    p.add_argument("--no-sqlite", action="store_true", help="Ne pas écrire dans SQLite")
    return p.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
