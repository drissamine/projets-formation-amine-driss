# Auteur : DRISS Amine  —  ESIS 2 (2025-2026)

"""Application Spark Structured Streaming — agrégations + sorties (Tâches 2.2 & 2.3).

Câble : Kafka -> parsing/validation (2.1) -> agrégations fenêtrées (2.2)
        -> sorties console + CSV/JSON + SQLite (2.3).

Chaque requête passe par UN seul foreachBatch (un seul consumer Kafka par requête)
qui écrit vers les destinations activées.

Exemples :
    # Backlog puis arrêt, toutes les requêtes, toutes les sorties
    python -m src.consumer.streaming_app --once --from-beginning

    # Continu, anomalies seules, sans écrire de fichiers
    python -m src.consumer.streaming_app --query anomalies --no-files
"""
from __future__ import annotations

import argparse

from pyspark.sql import DataFrame
from pyspark.sql.streaming import StreamingQuery

from config import settings
from src.common.spark_schema import parse_kafka_stream, split_valid_invalid
from src.consumer import sinks
from src.consumer import transformations as T
from src.consumer.spark_consumer import build_spark, read_kafka

QUERIES = ["popularity", "engagement", "genre", "anomalies", "all"]


def _start(df: DataFrame, name: str, trigger: dict, args: argparse.Namespace,
           top_n: int | None = None) -> StreamingQuery:
    """Démarre une requête : foreachBatch -> console + fichiers + SQLite (selon flags)."""

    def _batch(batch_df: DataFrame, batch_id: int) -> None:
        out = T.top_n_videos(batch_df, top_n) if top_n is not None else batch_df
        out.persist()
        try:
            if out.isEmpty():
                return
            if not args.no_console:
                print(f"\n=== {name} (batch {batch_id}) ===")
                out.show(40, truncate=False)
            written = sinks.write_batch(
                out, name, batch_id,
                files=not args.no_files, sqlite=not args.no_sqlite,
            )
            dests = [d for d, on in (("console", not args.no_console),
                                     ("fichiers", not args.no_files),
                                     ("sqlite", not args.no_sqlite)) if on]
            print(f"[sink] {name}: {written} lignes -> {', '.join(dests) or 'aucune sortie'}")
        finally:
            out.unpersist()

    writer = (
        df.writeStream.outputMode("update")
        .foreachBatch(_batch)
        .queryName(name)
        .trigger(**trigger)
    )
    if args.checkpoint:
        writer = writer.option("checkpointLocation", settings.checkpoint_path(name))
    return writer.start()


def start_queries(valid: DataFrame, selected: str, trigger: dict,
                  args: argparse.Namespace) -> list[StreamingQuery]:
    want = set(QUERIES[:-1]) if selected == "all" else {selected}
    queries: list[StreamingQuery] = []

    if "popularity" in want:
        queries.append(_start(T.video_popularity(valid), "video_popularity", trigger, args, top_n=10))
    if "engagement" in want:
        queries.append(_start(T.user_engagement(valid), "user_engagement", trigger, args))
        queries.append(_start(T.inactive_users(valid), "inactive_users", trigger, args))
    if "genre" in want:
        queries.append(_start(T.genre_analysis(valid), "genre_analysis", trigger, args))
    if "anomalies" in want:
        queries.append(_start(T.anomaly_user_many_videos(valid), "anomaly_user_videos", trigger, args))
        queries.append(_start(T.anomaly_device_flood(valid), "anomaly_device_flood", trigger, args))
    return queries


def main() -> int:
    args = parse_args()
    spark = build_spark("streaming-aggregations")

    raw = read_kafka(spark, args)
    parsed = parse_kafka_stream(raw)
    valid, _invalid = split_valid_invalid(parsed)

    trigger = {"availableNow": True} if args.once else {"processingTime": "10 seconds"}
    queries = start_queries(valid, args.query, trigger, args)

    print(f"[app] {len(queries)} requête(s) : {args.query} "
          f"(fenêtre {settings.WINDOW_DURATION}/{settings.SLIDE_DURATION}) "
          f"| results={settings.RESULTS_DIR} | db={settings.SQLITE_DB}")

    if args.once:
        for q in queries:
            q.awaitTermination()
    else:
        spark.streams.awaitAnyTermination()
    return 0


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Agrégations + sorties Spark (Tâches 2.2 & 2.3)")
    p.add_argument("--bootstrap", default=settings.KAFKA_BOOTSTRAP_SERVERS)
    p.add_argument("--topic", default=settings.KAFKA_TOPIC)
    p.add_argument("--from-beginning", action="store_true",
                   help="Lire depuis le début du topic (startingOffsets=earliest)")
    p.add_argument("--once", action="store_true",
                   help="Traiter le backlog puis s'arrêter (trigger availableNow)")
    p.add_argument("--query", choices=QUERIES, default="all",
                   help="Requête(s) à exécuter (défaut: all)")
    p.add_argument("--no-console", action="store_true", help="Ne pas afficher en console")
    p.add_argument("--no-files", action="store_true", help="Ne pas écrire les CSV/JSON")
    p.add_argument("--no-sqlite", action="store_true", help="Ne pas écrire dans SQLite")
    p.add_argument("--checkpoint", action="store_true",
                   help="Activer les checkpoints (reprise sur incident, Tâche 3.2)")
    return p.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
