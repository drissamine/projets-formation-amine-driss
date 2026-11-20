# Spark Structured Streaming Consumer

## Description
Application Spark Structured Streaming pour le traitement en temps réel des événements de streaming vidéo.

## Fonctionnalités
- Consommation d'événements depuis Kafka topic `streaming-events`
- Parsing JSON et validation de schéma
- 4 requêtes d'analyse en temps réel avec fenêtres glissantes
- Sorties vers console, fichiers JSON et base de données SQLite
- Checkpointing pour reprise sur incident

## Architecture des Requêtes

### Query 1: Popularité des Vidéos
- **Objectif**: Top 10 des vidéos les plus populaires
- **Fenêtre**: 10 minutes, glissement toutes les 5 minutes
- **Métriques**: Nombre de lectures, utilisateurs uniques
- **Sorties**: Console + fichiers JSON

### Query 2: Engagement Utilisateur
- **Objectif**: Analyse de l'engagement et détection d'inactivité
- **Fenêtre**: 10 minutes, glissement toutes les 5 minutes
- **Métriques**: Durée de session, temps de visionnage, inactivité >15min
- **Sorties**: Console

### Query 3: Analyse par Genre
- **Objectif**: Répartition des visionnages par genre
- **Fenêtre**: 10 minutes, glissement toutes les 5 minutes
- **Métriques**: Nombre de lectures, utilisateurs uniques, durée moyenne
- **Sorties**: Console

### Query 4: Détection d'Anomalies
- **Objectif**: Détection d'anomalies et alertes
- **Types d'anomalies**:
  - Temps courant invalide (> durée ou < 0)
  - Activité excessive (bots)
  - Vidéos avec durée nulle
- **Sorties**: Console

## Installation

### Prérequis
- Java 8+
- Apache Spark 3.4+
- Python 3.9+
- Kafka installé et en cours d'exécution

### Dépendances Python
```bash
pip install -r requirements.txt
```

## Configuration Spark

### Variables d'environnement
```bash
export SPARK_HOME=/path/to/spark
export PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-*.zip:$PYTHONPATH
export JAVA_HOME=/path/to/java
```

### Configuration recommandée
```python
spark.sql.adaptive.enabled = true
spark.sql.adaptive.coalescePartitions.enabled = true
spark.sql.adaptive.skewJoin.enabled = true
spark.serializer = org.apache.spark.serializer.KryoSerializer
spark.sql.shuffle.partitions = 8
```

## Utilisation

### Démarrage de base
```bash
python spark_streaming_app.py
```

### Options de configuration
```bash
python spark_streaming_app.py \
  --kafka-bootstrap-servers localhost:9092 \
  --kafka-topic streaming-events \
  --checkpoint-location ./checkpoints/spark-streaming \
  --output-mode append
```

### Options disponibles
- `--kafka-bootstrap-servers`: Serveurs Kafka (défaut: localhost:9092)
- `--kafka-topic`: Topic Kafka (défaut: streaming-events)
- `--checkpoint-location`: Emplacement des checkpoints (défaut: ./checkpoints/spark-streaming)
- `--output-mode`: Mode de sortie (append, update, complete)

## Sorties

### Console Output
Les résultats sont affichés en temps réel dans la console avec:
- Formatage lisible
- Troncature désactivée pour une meilleure visibilité
- Mise à jour toutes les 30 secondes

### Fichiers JSON
Les résultats sont sauvegardés dans `./results/`:
- `video_popularity/`: Popularité des vidéos
- Structure: `/results/video_popularity/YYYY-MM-DD-HH-mm-ss/`

### Checkpoints
Les checkpoints sont stockés dans `./checkpoints/spark-streaming/`:
- Permettent la reprise sur incident
- Séparés par requête pour une meilleure gestion

## Monitoring

### Métriques Spark
- **Throughput**: Événements traités par seconde
- **Latence**: Temps de traitement des événements
- **Utilisation mémoire**: Consommation mémoire des workers
- **Partitions**: Distribution des données

### Monitoring via Web UI
Accéder à l'interface Spark Web UI:
- URL: http://localhost:4040
- Permet de surveiller les jobs, stages, et RDDs
- Visualisation des statistiques de performance

## Performance

### Optimisations Spark
- **Adaptive Query Execution**: Optimisation dynamique des requêtes
- **Kryo Serialization**: Sérialisation plus rapide
- **Partition Coalescing**: Regroupement intelligent des partitions
- **Skew Join Handling**: Gestion des partitions déséquilibrées

### Tuning recommandé
```bash
# Augmenter le nombre de partitions pour le shuffle
spark.sql.shuffle.partitions=16

# Activer l'adaptive execution
spark.sql.adaptive.enabled=true

# Configurer la mémoire
spark.executor.memory=2g
spark.driver.memory=1g
```

## Gestion des Erreurs

### Dead Letter Queue
Les messages invalides sont gérés via:
- Validation de schéma JSON
- Filtrage des événements corrompus
- Logging des erreurs pour analyse

### Reprise sur Incident
- **Checkpoints**: Sauvegarde régulière de l'état
- **Exactly-once semantics**: Garantie de traitement unique
- **Recovery**: Redémarrage à partir du dernier checkpoint

## Dépannage

### Problèmes courants

#### Erreur de connexion Kafka
```bash
# Vérifier que Kafka est en cours d'exécution
netstat -an | grep 9092

# Tester la connexion
telnet localhost 9092
```

#### Erreur de mémoire Spark
```bash
# Augmenter la mémoire allouée
export SPARK_DRIVER_MEMORY=2g
export SPARK_EXECUTOR_MEMORY=4g
```

#### Erreur de schéma JSON
Vérifier que les événements Kafka respectent le schéma:
```json
{
  "event_id": "uuid",
  "user_id": "string",
  "video_id": "string",
  "event_type": "PLAY|PAUSE|STOP|SEEK",
  "timestamp": "ISO8601",
  "current_time": 123.45,
  "duration": 600.00,
  "genre": "action|comedy|drama",
  "device": "mobile|desktop|tv"
}
```

## Exécution

### Workflow typique
1. Démarrer Kafka et ZooKeeper
2. Créer le topic `streaming-events`
3. Démarrer le producteur Kafka
4. Démarrer le consommateur Spark
5. Surveiller les sorties et métriques

### Commandes de base
```bash
# Démarrer Kafka (dans un terminal)
./kafka-server-start.sh config/server.properties

# Créer le topic
./kafka-topics.sh --create --topic streaming-events --bootstrap-server localhost:9092 --partitions 3

# Démarrer le producteur
python ../producer/kafka_producer.py --continuous

# Démarrer le consommateur Spark
python spark_streaming_app.py