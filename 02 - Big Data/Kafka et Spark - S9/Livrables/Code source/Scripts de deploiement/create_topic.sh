#!/usr/bin/env bash
# Crée les topics Kafka du projet (Tâche 1.2).
# Usage : bash scripts/create_topic.sh
set -euo pipefail

BROKER="kafka:9092"
RETENTION_MS=$((7 * 24 * 60 * 60 * 1000))   # 7 jours

echo "==> Création du topic principal : streaming-events (3 partitions, rétention 7j)"
docker exec kafka /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server "$BROKER" \
  --create --if-not-exists \
  --topic streaming-events \
  --partitions 3 \
  --replication-factor 1 \
  --config retention.ms="$RETENTION_MS"

echo "==> Création de la dead-letter queue : streaming-events-dlq"
docker exec kafka /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server "$BROKER" \
  --create --if-not-exists \
  --topic streaming-events-dlq \
  --partitions 1 \
  --replication-factor 1 \
  --config retention.ms="$RETENTION_MS"

echo "==> Topics existants :"
docker exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server "$BROKER" --list

echo "==> Détail de streaming-events :"
docker exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server "$BROKER" --describe --topic streaming-events
