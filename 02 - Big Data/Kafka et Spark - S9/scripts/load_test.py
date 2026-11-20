"""Test de charge et d'évolutivité (Tâche 3.3).

Pour chaque volume demandé :
  1. crée un topic dédié (vide) à 3 partitions,
  2. produit N événements en mesurant le débit de production,
  3. lit + parse + compte les événements avec Spark (lecture batch) en mesurant
     le débit de traitement,
  4. consigne les métriques (console + results/metrics/load_test.csv).

Inclut le test demandé à 100 000 événements et permet de comparer plusieurs volumes.

Exemple :
    python -m scripts.load_test --volumes 10000,50000,100000
"""
from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

from config import settings
from src.common.event_schema import EventGenerator
from src.common.spark_schema import parse_kafka_stream, split_valid_invalid
from src.consumer.spark_consumer import build_spark
from src.producer.producer import build_producer


def _create_topic(name: str, partitions: int = 3) -> None:
    admin = KafkaAdminClient(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(","))
    try:
        admin.create_topics([NewTopic(name, num_partitions=partitions, replication_factor=1)])
    except TopicAlreadyExistsError:
        pass
    finally:
        admin.close()


def _produce(topic: str, volume: int) -> float:
    """Produit `volume` événements aussi vite que possible. Renvoie la durée (s)."""
    gen = EventGenerator()
    producer = build_producer(settings.KAFKA_BOOTSTRAP_SERVERS)
    start = time.time()
    for _ in range(volume):
        event = gen.generate()
        producer.send(topic, key=event["user_id"], value=event)
    producer.flush()
    producer.close()
    return time.time() - start


def _process(spark, topic: str) -> tuple[float, int, int]:
    """Lit le topic en batch, parse et compte valides/invalides. Renvoie (durée, valides, invalides)."""
    start = time.time()
    raw = (
        spark.read.format("kafka")
        .option("kafka.bootstrap.servers", settings.KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", topic)
        .option("startingOffsets", "earliest")
        .option("endingOffsets", "latest")
        .load()
    )
    parsed = parse_kafka_stream(raw)
    valid, invalid = split_valid_invalid(parsed)
    valid_count = valid.count()
    invalid_count = invalid.count()
    return time.time() - start, valid_count, invalid_count


def _write_csv(rows: list[dict]) -> Path:
    out_dir = Path(settings.RESULTS_DIR) / "metrics"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "load_test.csv"
    new = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        if new:
            writer.writeheader()
        writer.writerows(rows)
    return path


def main() -> int:
    args = parse_args()
    volumes = [int(v) for v in args.volumes.split(",")]
    run_id = int(time.time())
    spark = build_spark("load-test")

    results = []
    for volume in volumes:
        topic = f"loadtest-{volume}-{run_id}"
        _create_topic(topic)
        print(f"\n=== Volume {volume:,} (topic {topic}) ===")

        prod_s = _produce(topic, volume)
        prod_rate = volume / prod_s if prod_s else 0
        print(f"  Production : {prod_s:.1f}s  ->  {prod_rate:,.0f} evt/s")

        proc_s, valid, invalid = _process(spark, topic)
        proc_rate = (valid + invalid) / proc_s if proc_s else 0
        print(f"  Traitement : {proc_s:.1f}s  ->  {proc_rate:,.0f} evt/s "
              f"(valides={valid:,} invalides={invalid:,})")

        results.append({
            "volume": volume,
            "produce_s": round(prod_s, 2),
            "produce_rate": round(prod_rate),
            "process_s": round(proc_s, 2),
            "process_rate": round(proc_rate),
            "valid": valid,
            "invalid": invalid,
        })

    path = _write_csv(results)
    print("\n=== Récapitulatif évolutivité ===")
    print(f"{'volume':>10} | {'prod evt/s':>11} | {'proc evt/s':>11} | {'proc (s)':>9}")
    for r in results:
        print(f"{r['volume']:>10,} | {r['produce_rate']:>11,} | {r['process_rate']:>11,} | {r['process_s']:>9}")
    print(f"\nMétriques écrites dans {path}")
    return 0


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Test de charge & évolutivité (Tâche 3.3)")
    p.add_argument("--volumes", default="10000,50000,100000",
                   help="Volumes à tester, séparés par des virgules")
    return p.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
