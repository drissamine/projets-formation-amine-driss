# Monitoring and Metrics Collection

## Description
Système de monitoring et de collecte de métriques pour le pipeline Kafka-Spark Streaming.

## Fonctionnalités

### Métriques de Performance
- **Throughput**: Événements traités par seconde (global et récent)
- **Latence**: Temps de traitement des événements (moyenne, min, max, P95, P99)
- **Temps d'exécution**: Durée totale du pipeline

### Métriques Système
- **CPU**: Utilisation processeur
- **Mémoire**: Utilisation RAM (totale, disponible, pourcentage)
- **Disque**: Espace disque (total, libre, pourcentage utilisé)

### Métriques Kafka
- **Consumer Lag**: Retard du consommateur par partition
- **Partitions**: Nombre et état des partitions
- **Offsets**: Derniers offsets consommés

### Métriques Spark
- **Jobs**: Nombre de jobs actifs et terminés
- **Stages**: Nombre de stages actifs et terminés
- **Web UI**: Accès aux métriques via l'interface Spark

## Architecture

### PipelineMetrics Class
```python
class PipelineMetrics:
    def __init__(self, kafka_bootstrap_servers, kafka_topic, spark_ui_url)
    def start_monitoring(self, interval=30)  # Démarrage monitoring
    def stop_monitoring()                    # Arrêt monitoring
    def record_event(event_timestamp)        # Enregistrement événement
    def get_throughput()                     # Calcul throughput
    def get_latency_stats()                  # Calcul latence
    def get_system_stats()                   # Stats système
    def generate_report()                    # Génération rapport
    def save_report(filepath)                # Sauvegarde rapport
```

### Monitoring en Arrière-plan
- **Thread dédié**: Exécution asynchrone du monitoring
- **Intervalle configurable**: Fréquence de collecte (défaut: 30s)
- **Gestion des erreurs**: Reprise automatique en cas d'erreur

## Installation

### Dépendances Python
```bash
pip install psutil requests kafka-python
```

### Configuration
```python
metrics = PipelineMetrics(
    kafka_bootstrap_servers='localhost:9092',
    kafka_topic='streaming-events',
    spark_ui_url='http://localhost:4040'
)
```

## Utilisation

### Monitoring de Base
```python
from monitoring.metrics import PipelineMetrics

# Initialisation
metrics = PipelineMetrics()

# Démarrage monitoring
metrics.start_monitoring(interval=30)

# Enregistrement d'événements
metrics.record_event(event_timestamp)

# Arrêt monitoring
metrics.stop_monitoring()
```

### Monitoring Intégré avec Spark
```python
# Dans spark_streaming_app.py
class SparkStreamingProcessor:
    def __init__(self, ...):
        # ... existing code ...
        self.metrics = PipelineMetrics()
        self.metrics.start_monitoring()
    
    def process_batch(self, batch_df, batch_id):
        # Enregistrement du traitement
        start_time = time.time()
        
        # Traitement batch
        # ... processing logic ...
        
        # Enregistrement métriques
        self.metrics.record_event(start_time)
```

### Monitoring Intégré avec Kafka Producer
```python
# Dans kafka_producer.py
class KafkaStreamingProducer:
    def __init__(self, ...):
        # ... existing code ...
        self.metrics = PipelineMetrics()
        self.metrics.start_monitoring()
    
    def send_event(self, event):
        # Enregistrement envoi
        send_time = time.time()
        
        # Envoi Kafka
        # ... send logic ...
        
        # Enregistrement métriques
        self.metrics.record_event(send_time)
```

## Sorties et Rapports

### Console Output
```
============================================================
PIPELINE METRICS REPORT
============================================================
Time: 2024-01-01T10:00:00
Total Events: 1500
Throughput: 25.5 events/sec (recent), 24.8 events/sec (total)
Latency - Avg: 0.125s, Min: 0.045s, Max: 0.892s
Latency - P95: 0.234s, P99: 0.456s
System - CPU: 45.2%, Memory: 67.8%, Disk: 23.4%
============================================================
```

### JSON Report
```json
{
  "timestamp": "2024-01-01T10:00:00",
  "throughput": {
    "total_events": 1500,
    "total_throughput": 24.8,
    "recent_throughput": 25.5,
    "elapsed_time": 60.5
  },
  "latency": {
    "avg_latency": 0.125,
    "min_latency": 0.045,
    "max_latency": 0.892,
    "p95_latency": 0.234,
    "p99_latency": 0.456,
    "sample_count": 1000
  },
  "system_stats": {
    "cpu_usage": 45.2,
    "memory": {
      "total": 17179869184,
      "available": 5432109876,
      "percent": 67.8
    },
    "disk": {
      "total": 512105932800,
      "free": 392105932800,
      "percent": 23.4
    }
  }
}
```

### Monitoring Web Dashboard
Accéder aux interfaces de monitoring:
- **Spark Web UI**: http://localhost:4040
- **Kafka Manager**: http://localhost:9000 (si installé)
- **Custom Dashboard**: À implémenter avec Grafana/InfluxDB

## Configuration Avancée

### Intervalle de Monitoring
```python
# Monitoring toutes les 10 secondes
metrics.start_monitoring(interval=10)

# Monitoring toutes les 5 minutes
metrics.start_monitoring(interval=300)
```

### Personnalisation des Métriques
```python
# Surcharge des méthodes de collecte
class CustomMetrics(PipelineMetrics):
    def _collect_custom_metrics(self):
        # Métriques personnalisées
        pass
    
    def log_current_metrics(self):
        # Format de log personnalisé
        super().log_current_metrics()
        # Ajout de logs spécifiques
```

### Export vers Systèmes Externes
```python
# Export vers InfluxDB
def export_to_influxdb(metrics_data):
    # Implémentation export InfluxDB
    pass

# Export vers Prometheus
def export_to_prometheus(metrics_data):
    # Implémentation export Prometheus
    pass
```

## Performance et Optimisation

### Impact sur les Performances
- **CPU**: < 1% d'utilisation supplémentaire
- **Mémoire**: ~10MB de mémoire supplémentaire
- **Réseau**: Traffic minimal pour les appels API

### Optimisations
- **Buffering**: Stockage limité des métriques (derniers 1000 événements)
- **Async**: Collecte asynchrone pour éviter le blocage
- **Sampling**: Échantillonnage pour les métriques système

## Dépannage

### Problèmes Courants

#### Erreur de Connexion Kafka
```bash
# Vérifier que Kafka est accessible
telnet localhost 9092

# Vérifier les topics
kafka-topics.sh --list --bootstrap-server localhost:9092
```

#### Erreur Spark Web UI
```bash
# Vérifier que Spark est en cours d'exécution
curl http://localhost:4040

# Vérifier les applications Spark
curl http://localhost:4040/api/v1/applications
```

#### Problèmes de Permissions Système
```bash
# Vérifier les permissions psutil
python -c "import psutil; print(psutil.cpu_percent())"
```

### Logs et Debugging
```python
# Augmenter le niveau de log
logging.getLogger('monitoring.metrics').setLevel(logging.DEBUG)

# Logs détaillés
logger.debug("Detailed metrics collection")
```

## Intégration avec d'autres Outils

### Grafana + InfluxDB
```python
# Export vers InfluxDB pour Grafana
from influxdb import InfluxDBClient

class InfluxMetricsExporter:
    def __init__(self, host, port, database):
        self.client = InfluxDBClient(host, port, database=database)
    
    def export_metrics(self, metrics_data):
        # Format InfluxDB line protocol
        pass
```

### Prometheus + AlertManager
```python
# Export Prometheus metrics
from prometheus_client import Gauge, Counter, start_http_server

class PrometheusExporter:
    def __init__(self):
        self.throughput_gauge = Gauge('streaming_throughput', 'Events per second')
        self.latency_gauge = Gauge('streaming_latency', 'Processing latency')
    
    def export_metrics(self, metrics_data):
        self.throughput_gauge.set(metrics_data['throughput']['recent_throughput'])
        self.latency_gauge.set(metrics_data['latency']['avg_latency'])
```

### ELK Stack
```python
# Export vers Elasticsearch
from elasticsearch import Elasticsearch

class ElasticsearchExporter:
    def __init__(self, host):
        self.es = Elasticsearch([host])
    
    def export_metrics(self, metrics_data):
        self.es.index(index='streaming_metrics', body=metrics_data)