# Crée les topics Kafka du projet (Tâche 1.2) - version Windows / PowerShell.
# Usage : pwsh scripts/create_topic.ps1   (ou clic droit > Exécuter avec PowerShell)
$ErrorActionPreference = "Stop"

$broker = "kafka:9092"
$retentionMs = 7 * 24 * 60 * 60 * 1000   # 7 jours

Write-Host "==> Création du topic principal : streaming-events (3 partitions, rétention 7j)"
docker exec kafka /opt/kafka/bin/kafka-topics.sh `
  --bootstrap-server $broker `
  --create --if-not-exists `
  --topic streaming-events `
  --partitions 3 `
  --replication-factor 1 `
  --config "retention.ms=$retentionMs"

Write-Host "==> Création de la dead-letter queue : streaming-events-dlq"
docker exec kafka /opt/kafka/bin/kafka-topics.sh `
  --bootstrap-server $broker `
  --create --if-not-exists `
  --topic streaming-events-dlq `
  --partitions 1 `
  --replication-factor 1 `
  --config "retention.ms=$retentionMs"

Write-Host "==> Topics existants :"
docker exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server $broker --list

Write-Host "==> Détail de streaming-events :"
docker exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server $broker --describe --topic streaming-events
