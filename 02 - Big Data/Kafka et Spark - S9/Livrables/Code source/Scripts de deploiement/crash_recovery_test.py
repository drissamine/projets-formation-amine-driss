# Auteur : DRISS Amine  —  ESIS 2 (2025-2026)

"""Test de crash et de reprise sur checkpoint (Tâche 3.3).

Orchestrateur :
  1. crée un topic dédié et y produit V événements (tous valides),
  2. lance un worker Spark (streaming + checkpoint) qui enregistre chaque
     event_id traité dans la table SQLite crash_ids (clé primaire = dédup),
  3. TUE brutalement le worker en plein traitement (simulation de crash),
  4. relance le worker : il reprend depuis le checkpoint,
  5. vérifie que le nombre d'event_id distincts traités == V (aucune perte).

Le comptage par event_id distinct neutralise les éventuels rejeux at-least-once
des effets de bord de foreachBatch : ce qui compte est l'absence de PERTE.

    python -m scripts.crash_recovery_test --volume 30000
"""
from __future__ import annotations

import argparse
import shutil
import sqlite3
import subprocess
import sys
import time

from config import settings
from src.common.event_schema import EventGenerator
from src.common.spark_schema import parse_kafka_stream, split_valid_invalid
from src.consumer.spark_consumer import build_spark

CRASH_TABLE = "crash_ids"


# ---------------------------------------------------------------------------
# Worker : streaming + checkpoint, enregistre les event_id traités
# ---------------------------------------------------------------------------
def run_worker(args: argparse.Namespace) -> int:
    spark = build_spark("crash-worker")
    raw = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", settings.KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", args.topic)
        .option("startingOffsets", "earliest")
        .option("maxOffsetsPerTrigger", str(args.max_offsets))
        .load()
    )
    parsed = parse_kafka_stream(raw)
    valid, _invalid = split_valid_invalid(parsed)

    def _batch(batch_df, batch_id: int) -> None:  # noqa: ARG001
        ids = [r["event_id"] for r in batch_df.select("event_id").collect()]
        if not ids:
            return
        con = sqlite3.connect(settings.SQLITE_DB)
        try:
            con.execute(f'CREATE TABLE IF NOT EXISTS {CRASH_TABLE} (event_id TEXT PRIMARY KEY)')
            con.executemany(f'INSERT OR IGNORE INTO {CRASH_TABLE}(event_id) VALUES (?)',
                            [(i,) for i in ids])
            con.commit()
        finally:
            con.close()

    trigger = {"availableNow": True} if args.drain else {"processingTime": "2 seconds"}
    query = (
        valid.writeStream.foreachBatch(_batch)
        .option("checkpointLocation", args.checkpoint)
        .queryName("crash-worker")
        .trigger(**trigger)
        .start()
    )
    query.awaitTermination()
    return 0


# ---------------------------------------------------------------------------
# Orchestrateur
# ---------------------------------------------------------------------------
def _count_ids() -> int:
    con = sqlite3.connect(settings.SQLITE_DB)
    try:
        try:
            return con.execute(f'SELECT COUNT(*) FROM {CRASH_TABLE}').fetchone()[0]
        except sqlite3.OperationalError:
            return 0
    finally:
        con.close()


def _produce(topic: str, volume: int) -> None:
    from src.producer.producer import build_producer
    gen = EventGenerator()
    producer = build_producer(settings.KAFKA_BOOTSTRAP_SERVERS)
    for _ in range(volume):
        e = gen.generate()
        producer.send(topic, key=e["user_id"], value=e)
    producer.flush()
    producer.close()


def _create_topic(name: str) -> None:
    from kafka.admin import KafkaAdminClient, NewTopic
    from kafka.errors import TopicAlreadyExistsError
    admin = KafkaAdminClient(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(","))
    try:
        admin.create_topics([NewTopic(name, num_partitions=3, replication_factor=1)])
    except TopicAlreadyExistsError:
        pass
    finally:
        admin.close()


def _kill_tree(pid: int) -> None:
    subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)],
                   capture_output=True, check=False)


def run_orchestrator(args: argparse.Namespace) -> int:
    volume = args.volume
    topic = f"crashtest-{int(time.time())}"
    print(f"[setup] topic={topic} volume={volume}")
    _create_topic(topic)
    _produce(topic, volume)

    # Repartir propre : checkpoint vide + table vide
    checkpoint = settings.checkpoint_path("crash")
    shutil.rmtree(checkpoint, ignore_errors=True)
    checkpoint = settings.checkpoint_path("crash")
    con = sqlite3.connect(settings.SQLITE_DB)
    con.execute(f'DROP TABLE IF EXISTS {CRASH_TABLE}')
    con.commit()
    con.close()

    max_offsets = max(1000, volume // 20)
    worker_cmd = [
        sys.executable, "-m", "scripts.crash_recovery_test", "--worker",
        "--topic", topic, "--checkpoint", checkpoint, "--max-offsets", str(max_offsets),
    ]

    # Phase 1 : worker continu, tué en plein traitement
    print("[phase 1] démarrage du worker (sera tué en cours de route)...")
    proc = subprocess.Popen(worker_cmd)
    deadline = time.time() + 120
    while time.time() < deadline:
        time.sleep(1)
        n = _count_ids()
        if 0 < n < volume:
            break
    processed_before = _count_ids()
    _kill_tree(proc.pid)
    print(f"[crash] worker TUÉ après {processed_before}/{volume} événements traités")

    if processed_before == 0:
        print("[warn] aucun événement traité avant le kill (démarrage trop lent) — "
              "le test de reprise reste valide mais ne démontre pas le crash en cours de route")
    if processed_before == volume:
        print("[warn] tout a été traité avant le kill — augmenter le volume pour mieux démontrer")

    # Phase 2 : reprise depuis le checkpoint, drainage du reste
    print("[phase 2] reprise du worker depuis le checkpoint...")
    subprocess.run(worker_cmd + ["--drain"], check=False)
    total = _count_ids()

    print("\n=== Résultat reprise sur incident ===")
    print(f"  événements produits         : {volume}")
    print(f"  traités avant le crash      : {processed_before}")
    print(f"  traités au total (distincts): {total}")
    ok = total == volume
    print(f"  REPRISE {'OK — aucune perte' if ok else 'ÉCHEC — perte de données'} "
          f"({total}/{volume})")
    return 0 if ok else 1


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Test de crash & reprise (Tâche 3.3)")
    p.add_argument("--worker", action="store_true", help="(interne) lance le worker Spark")
    p.add_argument("--drain", action="store_true", help="(interne) worker en mode availableNow")
    p.add_argument("--topic", help="(interne) topic du worker")
    p.add_argument("--checkpoint", help="(interne) dossier checkpoint du worker")
    p.add_argument("--max-offsets", type=int, default=1500, help="(interne) maxOffsetsPerTrigger")
    p.add_argument("--volume", type=int, default=30000, help="Nombre d'événements à produire")
    return p.parse_args(argv)


def main() -> int:
    args = parse_args()
    return run_worker(args) if args.worker else run_orchestrator(args)


if __name__ == "__main__":
    raise SystemExit(main())
