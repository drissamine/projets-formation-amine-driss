# Auteur : DRISS Amine  —  ESIS 2 (2025-2026)

"""Routeur Dead-Letter Queue + checkpoint (Tâche 3.2).

Lit le topic principal, isole les messages invalides et les republie dans le
topic streaming-events-dlq, en JSON enrichi (raison, message brut, offset source).
La requête utilise un checkpointLocation : en cas de crash, elle reprend là où
elle s'était arrêtée (exactly-once côté offsets Kafka source).

Exemples :
    # Traite le backlog puis s'arrête
    python -m src.consumer.dlq_app --once --from-beginning

    # Continu, en repartant de zéro (efface le checkpoint)
    python -m src.consumer.dlq_app --reset
"""
from __future__ import annotations

import argparse
import shutil

from config import settings
from src.common.spark_schema import parse_kafka_stream, split_valid_invalid
from src.consumer.error_handling import to_kafka_dlq
from src.consumer.spark_consumer import build_spark, read_kafka


def main() -> int:
    args = parse_args()
    spark = build_spark("dlq-router")

    raw = read_kafka(spark, args)
    parsed = parse_kafka_stream(raw)
    _valid, invalid = split_valid_invalid(parsed)
    dlq = to_kafka_dlq(invalid)

    checkpoint = settings.checkpoint_path("dlq")
    if args.reset:
        shutil.rmtree(checkpoint, ignore_errors=True)
        checkpoint = settings.checkpoint_path("dlq")

    trigger = {"availableNow": True} if args.once else {"processingTime": "10 seconds"}
    query = (
        dlq.writeStream.format("kafka")
        .option("kafka.bootstrap.servers", args.bootstrap)
        .option("topic", settings.KAFKA_TOPIC_DLQ)
        .option("checkpointLocation", checkpoint)
        .outputMode("append")
        .queryName("dlq-router")
        .trigger(**trigger)
        .start()
    )

    print(f"[dlq] routage des messages invalides -> topic '{settings.KAFKA_TOPIC_DLQ}' "
          f"| checkpoint={checkpoint}")

    query.awaitTermination()
    return 0


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Routeur DLQ + checkpoint (Tâche 3.2)")
    p.add_argument("--bootstrap", default=settings.KAFKA_BOOTSTRAP_SERVERS)
    p.add_argument("--topic", default=settings.KAFKA_TOPIC)
    p.add_argument("--from-beginning", action="store_true",
                   help="Lire depuis le début du topic (startingOffsets=earliest)")
    p.add_argument("--once", action="store_true",
                   help="Traiter le backlog puis s'arrêter (trigger availableNow)")
    p.add_argument("--reset", action="store_true",
                   help="Effacer le checkpoint avant de démarrer (rejeu complet)")
    return p.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
