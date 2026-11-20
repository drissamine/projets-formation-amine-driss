# Kafka-Spark Streaming Pipeline

## Description
Projet de pipeline de traitement de données en temps réel pour analyser les habitudes de visionnage d'une plateforme de streaming vidéo. Le système utilise Apache Kafka pour la collecte et la distribution des événements, et Apache Spark Structured Streaming pour le traitement et l'analyse en temps réel.

## Architecture

```
Sources de Données → Kafka → Spark Structured Streaming → Stockage/Visualisation
```

### Composants Principaux

1. **Kafka Producer** (`producer/`): Générateur d'événements de streaming
2. **Kafka Cluster** (`kafka/`): Broker de messages avec ZooKeeper
3. **Spark Structured Streaming** (`spark/consumer/`): Moteur de traitement en temps réel
4. **Output Handlers** (`spark/output/`): Systèmes de sortie (Console, Fichiers, SQLite)
5. **Monitoring** (`monitoring/`): Système de collecte de métriques et de monitoring
6. **Tests** (`tests/`): Suite de tests unitaires et d'intégration

## Technologies

- **Kafka 3.5+**: Streaming de messages distribués
- **Spark 3.4+**: Traitement de flux de données
- **Python 3.9+**: Langage de développement
- **SQLite**: Base de données légère pour le stockage
- **JSON**: Format de sérialisation des événements

## Installation

### Prérequis Système
- **Java 8+**: Pour Kafka et Spark
- **Python 3.9+**: Pour les scripts de production et consommation
- **Apache Kafka 3.5+**: Pour le streaming de messages
- **Apache Spark 3.4+**: Pour le traitement en temps réel

### Installation Rapide

1. **Installer les dépendances Python**:
   ```bash
   cd producer && pip install -r requirements.txt
   cd ../spark/consumer && pip install -r requirements.txt
   pip install psutil requests kafka-python
   ```

2. **Démarrer Kafka** (Linux/Mac):
   ```bash
   # Démarrer ZooKeeper
   cd /opt/kafka
   bin/zookeeper-server-start.sh config/zookeeper.properties &
   
   # Démarrer Kafka
   bin/kafka-server-start.sh config/server.properties &
   
   # Créer le topic
   bin/kafka-topics.sh --create --topic streaming-events --bootstrap-server localhost:9092 --partitions 3
   ```

3. **Démarrer Spark**:
   ```bash
   export SPARK_HOME=/opt/spark
   export PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-*.zip:$PYTHONPATH
   cd spark/consumer
   python spark_streaming_app.py
   ```

4. **Démarrer le Producteur**:
   ```bash
   cd producer
   python kafka_producer.py --continuous --delay 0.1
   ```

## Utilisation

### Commandes Disponibles

#### Kafka Producer
```bash
python producer/kafka_producer.py [OPTIONS]

Options:
  --bootstrap-servers SERVERS    Kafka bootstrap servers (default: localhost:9092)
  --topic TOPIC                  Kafka topic name (default: streaming-events)
  --num-events N                 Number of events to generate (default: 1000)
  --delay SECONDS                Delay between events in seconds (default: 0.1)
  --continuous                   Run continuously until interrupted
  --help                         Show help message
```

#### Spark Streaming Consumer
```bash
python spark/consumer/spark_streaming_app.py [OPTIONS]

Options:
  --kafka-bootstrap-servers SERVERS    Kafka bootstrap servers (default: localhost:9092)
  --kafka-topic TOPIC                  Kafka topic name (default: streaming-events)
  --checkpoint-location PATH           Checkpoint location (default: ./checkpoints/spark-streaming)
  --output-mode MODE                   Output mode: append|update|complete (default: append)
  --help                               Show help message
```

### Exemples d'Utilisation

#### Génération de 10000 événements avec délai de 0.05s
```bash
python producer/kafka_producer.py --num-events 10000 --delay 0.05
```

#### Démarrer Spark avec mode de sortie "complete"
```bash
python spark/consumer/spark_streaming_app.py --output-mode complete
```

#### Monitoring continu avec faible latence
```bash
# Terminal 1: Spark Consumer
python spark/consumer/spark_streaming_app.py --output-mode append

# Terminal 2: Kafka Producer (continu)
python producer/kafka_producer.py --continuous --delay 0.01
```

## Analyse des Données

### Query 1: Popularité des Vidéos
- **Objectif**: Identifier les vidéos les plus populaires
- **Métriques**: Nombre de lectures, utilisateurs uniques
- **Fenêtre**: 10 minutes, glissement toutes les 5 minutes

### Query 2: Engagement Utilisateur
- **Objectif**: Analyser l'engagement et détecter l'inactivité
- **Métriques**: Durée de session, temps de visionnage total, inactivité >15min
- **Fenêtre**: 10 minutes, glissement toutes les 5 minutes

### Query 3: Analyse par Genre
- **Objectif**: Répartition des visionnages par genre
- **Métriques**: Nombre de lectures, utilisateurs uniques, durée moyenne
- **Fenêtre**: 10 minutes, glissement toutes les 5 minutes

### Query 4: Détection d'Anomalies
- **Objectif**: Identifier les comportements anormaux
- **Types d'anomalies**:
  - Temps courant invalide (> durée ou < 0)
  - Activité excessive (bots: >100 événements)
  - Vidéos avec durée nulle

## Monitoring

### Métriques Disponibles
- **Performance**: Throughput, latence, temps d'exécution
- **Système**: CPU, mémoire, disque
- **Kafka**: Consumer lag, partitions, offsets
- **Spark**: Jobs, stages, Web UI

### Monitoring en Temps Réel
- **Console Output**: Affichage structuré en temps réel
- **Spark Web UI**: http://localhost:4040
- **Fichiers de Sortie**: Sauvegarde dans `./results/`
- **Base SQLite**: Stockage historique dans `./results/streaming_results.db`

## Tests

### Exécution des Tests
```bash
# Tous les tests
python -m pytest tests/ -v

# Tests spécifiques
python -m pytest tests/test_kafka_producer.py -v
python -m pytest tests/test_spark_streaming.py -v
python -m pytest tests/test_monitoring.py -v

# Tests avec unittest
python tests/test_kafka_producer.py
python tests/test_spark_streaming.py
python tests/test_monitoring.py
```

### Couverture des Tests
- **Kafka Producer**: 15 tests (génération, envoi, erreurs)
- **Spark Streaming**: 12 tests (requêtes, transformations, schémas)
- **Monitoring**: 18 tests (métriques, reporting, background monitoring)
- **Couverture totale**: > 95%

## Scripts de Déploiement

### Script de Déploiement Automatisé
```bash
# Déploiement complet
./scripts/deploy.sh deploy

# Démarrer le pipeline
./scripts/deploy.sh start

# Arrêter le pipeline
./scripts/deploy.sh stop

# Vérifier le statut
./scripts/deploy.sh status

# Exécuter les tests
./scripts/test.sh all
```

## Documentation

### Documentation Technique
- **Rapport Technique**: `docs/technical_report.md`
- **Guide Utilisateur**: `docs/user_guide.md`

### Documentation par Composant
- **Producer**: `producer/README.md`
- **Consumer**: `spark/consumer/README.md`
- **Output**: `spark/output/README.md`
- **Monitoring**: `monitoring/README.md`
- **Tests**: `tests/README.md`

## Performance et Scalabilité

### Benchmarks Attendus
- **Throughput**: > 100 événements/seconde
- **Latence**: < 1 seconde (95% des événements)
- **Ressources Système**: CPU < 50%, Mémoire < 80%

### Optimisations Mises en Œuvre
- **Kafka**: Partitionnement, compression
- **Spark**: Adaptive Query Execution, Kryo Serialization
- **Memory Management**: Configuration optimisée

## Gestion des Erreurs et Fiabilité

### Dead Letter Queue
- **Implementation**: Filtrage des messages invalides
- **Logging**: Journalisation détaillée des erreurs
- **Recovery**: Possibilité de retraiter les messages DLQ

### Checkpointing
- **Location**: ./checkpoints/spark-streaming/
- **Frequency**: Alignée sur les fenêtres (toutes les 5 minutes)
- **Recovery**: Redémarrage à partir du dernier checkpoint

## Dépannage

### Problèmes Courants

#### Kafka ne démarre pas
```bash
# Vérifier les ports
netstat -an | grep 9092
netstat -an | grep 2181

# Vérifier les logs
tail -f /opt/kafka/logs/server.log
tail -f /opt/kafka/logs/zookeeper.log
```

#### Spark ne se connecte pas à Kafka
```bash
# Vérifier la connexion Kafka
telnet localhost 9092

# Vérifier les topics
/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

#### Producteur ne génère pas d'événements
```bash
# Vérifier les logs du producteur
# Vérifier la connexion réseau
# Vérifier les permissions de fichiers
```

### Solutions aux Problèmes Fréquents
Consultez le **Guide Utilisateur** (`docs/user_guide.md`) pour des solutions détaillées aux problèmes courants.

## Maintenance

### Backup et Archivage
- **Checkpoints Spark**: Backup quotidien
- **Base SQLite**: Backup quotidien
- **Fichiers de Sortie**: Backup hebdomadaire
- **Nettoyage**: Suppression automatique des fichiers > 30 jours

### Monitoring en Production
- **Dashboard**: Recommandations Grafana/Prometheus
- **Alertes**: Seuils de performance et ressources
- **Scaling**: Directives d'augmentation de capacité

## Contribuer

### Structure du Projet
```
TP-Projet-Kafka-Spark/
├── producer/              # Kafka Producer
├── kafka/                 # Kafka Configuration
├── spark/                 # Spark Consumer & Output
├── monitoring/            # Metrics Collection
├── tests/                 # Test Suite
├── docs/                  # Documentation
├── scripts/               # Deployment Scripts
└── README.md             # Ce fichier
```

### Processus de Contribution
1. **Fork** le projet
2. Créer une **branche** pour votre feature
3. **Commit** vos changements
4. **Push** vers votre fork
5. Créer une **Pull Request**

### Normes de Code
- **Python**: Respecter PEP 8
- **Documentation**: Documenter toutes les fonctions
- **Tests**: Ajouter des tests pour chaque nouvelle fonctionnalité
- **Commit Messages**: Messages clairs et descriptifs

## License

Ce projet est open source et distribué sous la license MIT. Consultez le fichier `LICENSE` pour plus de détails.

## Contact

Pour toute question ou problème:
1. Consultez la documentation
2. Vérifiez les logs appropriés
3. Exécutez les tests de validation
4. Contactez l'équipe technique

### Support
- **Documentation**: `docs/`
- **Tests**: `tests/`
- **Scripts**: `scripts/`
- **Issues**: GitHub Issues

---

**Projet réalisé dans le cadre du cours de Big Data et Streaming Analytics**