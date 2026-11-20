"""Producteur Kafka d'événements de streaming (Tâche 1.1).

Exemples :
    # Débit par défaut (.env), en continu, jusqu'à Ctrl+C
    python -m src.producer.producer

    # 100 000 événements à 5000 evt/s (test de charge, Tâche 3.3)
    python -m src.producer.producer --total 100000 --rate 5000

    # Injecter 2% de messages corrompus pour tester la dead-letter queue
    python -m src.producer.producer --corrupt-rate 0.02
"""
from __future__ import annotations

import argparse
import json
import signal
import sys
import time

from kafka import KafkaProducer
from kafka.errors import KafkaError
from kafka.serializer import Serializer

from config import settings
from src.common.event_schema import EventGenerator


class KeySerializer(Serializer):
    """Sérialise la clé (user_id) en UTF-8."""

    def serialize(self, topic, headers, key):  # noqa: ARG002
        return key.encode("utf-8") if key is not None else None


class JsonValueSerializer(Serializer):
    """Sérialise la valeur en JSON UTF-8. Laisse passer les chaînes brutes (messages corrompus)."""

    def serialize(self, topic, headers, value):  # noqa: ARG002
        if value is None:
            return None
        if isinstance(value, str):
            return value.encode("utf-8")
        return json.dumps(value).encode("utf-8")

# Drapeau d'arrêt propre (Ctrl+C)
_running = True


def _handle_sigint(signum, frame):  # noqa: ARG001
    global _running
    print("\n[producer] Arrêt demandé, vidage du buffer...")
    _running = False


def build_producer(bootstrap_servers: str) -> KafkaProducer:
    """Crée un KafkaProducer JSON robuste (acks=all, retries)."""
    return KafkaProducer(
        bootstrap_servers=bootstrap_servers.split(","),
        # La clé partitionne : on regroupe les événements d'un même user
        key_serializer=KeySerializer(),
        value_serializer=JsonValueSerializer(),
        acks="all",
        retries=5,
        linger_ms=20,        # micro-batching -> meilleur throughput
        compression_type="gzip",
    )


def run(args: argparse.Namespace) -> int:
    gen = EventGenerator()
    producer = build_producer(args.bootstrap)

    interval = 1.0 / args.rate if args.rate > 0 else 0.0
    sent = 0
    errors = 0
    last_report = time.time()
    last_report_count = 0

    print(
        f"[producer] topic={args.topic} bootstrap={args.bootstrap} "
        f"rate={args.rate}/s total={args.total or 'illimite'} corrupt={args.corrupt_rate:.0%}"
    )

    start = time.time()
    while _running:
        if args.total and sent >= args.total:
            break

        event = gen.generate()
        key = event["user_id"]

        # Injection optionnelle de messages invalides -> dead-letter queue (Tâche 3.2)
        if args.corrupt_rate and gen.rng.random() < args.corrupt_rate:
            payload = "{ ceci n'est pas du JSON valide"
        else:
            payload = event

        try:
            producer.send(args.topic, key=key, value=payload).add_errback(_on_error)
            sent += 1
        except KafkaError as exc:
            errors += 1
            print(f"[producer] erreur envoi: {exc}", file=sys.stderr)

        # Rapport de débit toutes les 5 s
        now = time.time()
        if now - last_report >= 5.0:
            rate = (sent - last_report_count) / (now - last_report)
            print(f"[producer] envoyes={sent} debit~{rate:.0f} evt/s erreurs={errors}")
            last_report, last_report_count = now, sent

        if interval:
            time.sleep(interval)

    producer.flush()
    producer.close()
    elapsed = time.time() - start
    avg = sent / elapsed if elapsed else 0
    print(f"[producer] Termine : {sent} evenements en {elapsed:.1f}s (~{avg:.0f} evt/s), erreurs={errors}")
    return 0


def _on_error(exc: Exception) -> None:
    print(f"[producer] échec livraison: {exc}", file=sys.stderr)


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Producteur Kafka d'événements de streaming vidéo")
    p.add_argument("--bootstrap", default=settings.KAFKA_BOOTSTRAP_SERVERS,
                   help="Serveurs Kafka (défaut: %(default)s)")
    p.add_argument("--topic", default=settings.KAFKA_TOPIC,
                   help="Topic cible (défaut: %(default)s)")
    p.add_argument("--rate", type=float, default=settings.EVENTS_PER_SECOND,
                   help="Événements par seconde (0 = max, défaut: %(default)s)")
    p.add_argument("--total", type=int, default=0,
                   help="Nombre total d'événements à envoyer (0 = illimité)")
    p.add_argument("--corrupt-rate", type=float, default=0.0,
                   help="Proportion de messages invalides à injecter (0.0 à 1.0)")
    return p.parse_args(argv)


def main() -> int:
    signal.signal(signal.SIGINT, _handle_sigint)
    return run(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
