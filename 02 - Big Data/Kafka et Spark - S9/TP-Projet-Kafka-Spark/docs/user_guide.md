# Guide Utilisateur : Pipeline Kafka-Spark Streaming

## Description
Guide d'utilisation pour le pipeline de traitement de données en temps réel Kafka-Spark Streaming.

## Table des Matières
1. [Prérequis Système](#prerequis-systeme)
2. [Installation](#installation)
3. [Démarrage du Pipeline](#demarrage-du-pipeline)
4. [Utilisation](#utilisation)
5. [Monitoring](#monitoring)
6. [Tests](#tests)
7. [Dépannage](#depasse)
8. [Maintenance](#maintenance)

## Prérequis Système

### Logiciels Requis
- **Java 8+**: Pour Kafka et Spark
- **Python 3.9+**: Pour les scripts de production et consommation
- **Apache Kafka 3.5+**: Pour le streaming de messages
- **Apache Spark 3.4+**: Pour le traitement en temps réel

### Vérification des Prérequis
```bash
# Vérifier Java
java -version
# Doit afficher: java version "1.8.x" ou version supérieure

# Vérifier Python
python --version
# Doit afficher: Python 3.9.x ou version supérieure

# Vérifier pip
pip --version
```

### Espace Disque
- **Minimum requis**: 5GB d'espace disque
- **Recommandé**: 10GB d'espace disque

## Installation

### 1. Installation de Kafka

#### Téléchargement
```bash
# Télécharger Kafka
wget https://downloads.apache.org/kafka/3.5.0/kafka_2.13-3.5.0.tgz

# Extraire
tar -xzf kafka_2.13-3.5.0.tgz

# Déplacer vers un emplacement permanent
sudo mv kafka_2.13-3.5.0 /opt/kafka
```

#### Configuration
Les fichiers de configuration sont déjà fournis dans `kafka/config/`:
- `server.properties`: Configuration du broker Kafka
- `zookeeper.properties`: Configuration de ZooKeeper

### 2. Installation de Spark

#### Téléchargement
```bash
# Télécharger Spark
wget https://downloads.apache.org/spark/spark-3.4.0/spark-3.4.0-bin-hadoop3.tgz

# Extraire
tar -xzf spark-3.4.0-bin-hadoop3.tgz

# Déplacer vers un emplacement permanent
sudo mv spark-3.4.0-bin-hadoop3 /opt/spark
```

#### Configuration des Variables d'Environnement
```bash
# Ajouter au ~/.bashrc ou ~/.zshrc
export SPARK_HOME=/opt/spark
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
export PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-*.zip:$PYTHONPATH
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64  # Adapter selon votre installation

# Recharger le shell
source ~/.bashrc
```

### 3. Installation des Dépendances Python

#### Kafka Producer Dependencies
```bash
cd TP-Projet-Kafka-Spark/producer
pip install -r requirements.txt
```

#### Spark Consumer Dependencies
```bash
cd TP-Projet-Kafka-Spark/spark/consumer
pip install -r requirements.txt
```

#### Monitoring Dependencies
```bash
pip install psutil requests kafka-python
```

## Démarrage du Pipeline

### 1. Démarrer Kafka et ZooKeeper

#### Option 1: Scripts Windows (fournis)
```bash
# Démarrer Kafka (dans un terminal)
cd TP-Projet-Kafka-Spark/kafka
kafka/start_kafka.bat

# Attendre 10-15 secondes pour que tout démarre
```

#### Option 2: Manuel (Linux/Mac)
```bash
# Démarrer ZooKeeper (dans un terminal)
cd /opt/kafka
bin/zookeeper-server-start.sh config/zookeeper.properties &

# Attendre 5 secondes
sleep 5

# Démarrer Kafka (dans un terminal)
bin/kafka-server-start.sh config/server.properties &

# Créer le topic
bin/kafka-topics.sh --create --topic streaming-events --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

### 2. Vérifier le Bon Fonctionnement de Kafka

```bash
# Vérifier ZooKeeper
echo stat | nc localhost 2181

# Vérifier Kafka
bin/kafka-topics.sh --list --bootstrap-server localhost:9092
# Doit afficher: streaming-events
```

### 3. Démarrer le Consommateur Spark

```bash
# Configurer l'environnement
export SPARK_HOME=/opt/spark
export PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-*.zip:$PYTHONPATH

# Démarrer le consommateur Spark
cd TP-Projet-Kafka-Spark/spark/consumer
python spark_streaming_app.py
```

**Attendre le message**: "All streaming queries started successfully"

### 4. Démarrer le Producteur Kafka

#### Option 1: Mode Continu (Recommandé pour le monitoring)
```bash
cd TP-Projet-Kafka-Spark/producer
python kafka_producer.py --continuous --delay 0.1
```

#### Option 2: Mode Batch (Pour les tests)
```bash
cd TP-Projet-Kafka-Spark/producer
python kafka_producer.py --num-events 1000 --delay 0.1
```

## Utilisation

### Commandes Disponibles

#### Kafka Producer
```bash
python kafka_producer.py [OPTIONS]

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
python spark_streaming_app.py [OPTIONS]

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
python kafka_producer.py --num-events 10000 --delay 0.05
```

#### Démarrer Spark avec mode de sortie "complete"
```bash
python spark_streaming_app.py --output-mode complete
```

#### Monitoring continu avec faible latence
```bash
# Terminal 1: Spark Consumer
python spark_streaming_app.py --output-mode append

# Terminal 2: Kafka Producer (continu)
python kafka_producer.py --continuous --delay 0.01
```

## Monitoring

### Monitoring en Temps Réel

#### Console Output
Les résultats sont affichés en temps réel dans la console du consommateur Spark:
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

#### Spark Web UI
Accéder à l'interface Web Spark pour le monitoring détaillé:
- **URL**: http://localhost:4040
- **Informations disponibles**:
  - Jobs en cours et terminés
  - Stages et tâches
  - Statistiques de performance
  - RDDs et DataFrames

#### Fichiers de Sortie
Les résultats sont sauvegardés dans `./results/`:
```
results/
├── json/
│   ├── video_popularity_20240101_100000.json
│   ├── user_engagement_20240101_100000.json
│   ├── genre_analysis_20240101_100000.json
│   └── anomalies_20240101_100000.json
└── csv/
    ├── video_popularity_20240101_100000.csv
    ├── user_engagement_20240101_100000.csv
    ├── genre_analysis_20240101_100000.csv
    └── anomalies_20240101_100000.csv
```

#### Base de Données SQLite
Accéder aux résultats historiques via SQLite:
```bash
sqlite3 ./results/streaming_results.db

# Exemples de requêtes
SELECT * FROM video_popularity ORDER BY created_at DESC LIMIT 10;
SELECT * FROM anomalies WHERE alert_type = 'INVALID_CURRENT_TIME';
```

### Monitoring des Performances

#### Métriques Clés à Surveiller
- **Throughput**: Doit être > 100 événements/seconde
- **Latence**: Doit être < 1 seconde pour 95% des événements
- **CPU Usage**: Doit être < 80%
- **Memory Usage**: Doit être < 90%
- **Kafka Lag**: Doit être < 1000 messages

#### Alertes
Le système de monitoring enverra des alertes dans les logs si:
- Le throughput chute en dessous de 50 événements/seconde
- La latence dépasse 2 secondes
- L'utilisation CPU dépasse 90%
- L'utilisation mémoire dépasse 95%

## Tests

### Exécution des Tests

#### Tests Unitaires
```bash
# Tous les tests
python -m pytest tests/ -v

# Tests spécifiques
python -m pytest tests/test_kafka_producer.py -v
python -m pytest tests/test_spark_streaming.py -v
python -m pytest tests/test_monitoring.py -v
```

#### Tests d'Intégration
```bash
# Tests avec 100K événements
python tests/test_integration.py --num-events 100000

# Tests de performance
python tests/test_performance.py --duration 300  # 5 minutes
```

#### Tests avec unittest
```bash
# Kafka Producer tests
python tests/test_kafka_producer.py

# Spark Streaming tests
python tests/test_spark_streaming.py

# Monitoring tests
python tests/test_monitoring.py
```

### Couverture des Tests
- **Kafka Producer**: 15 tests (génération, envoi, erreurs)
- **Spark Streaming**: 12 tests (requêtes, transformations, schémas)
- **Monitoring**: 18 tests (métriques, reporting, background monitoring)
- **Couverture totale**: > 95%

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

# Vérifier la mémoire
free -h
```

#### Spark ne se connecte pas à Kafka
```bash
# Vérifier la connexion Kafka
telnet localhost 9092

# Vérifier les topics
/opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Vérifier la configuration réseau
ping localhost
```

#### Producteur ne génère pas d'événements
```bash
# Vérifier les logs du producteur
# Vérifier la connexion réseau
# Vérifier les permissions de fichiers
ls -la TP-Projet-Kafka-Spark/producer/
```

#### Consommateur Spark plante
```bash
# Vérifier la mémoire disponible
free -h

# Vérifier la configuration Spark
echo $SPARK_HOME
echo $PYTHONPATH

# Vérifier les logs Spark
tail -f /tmp/spark-*.out
```

### Solutions aux Problèmes Fréquents

#### Problème: "Connection refused" Kafka
```bash
# Solution: Vérifier que Kafka est démarré
ps aux | grep kafka

# Redémarrer Kafka
/opt/kafka/bin/kafka-server-stop.sh
/opt/kafka/bin/kafka-server-start.sh config/server.properties &
```

#### Problème: "No module named 'pyspark'"
```bash
# Solution: Vérifier PYTHONPATH
echo $PYTHONPATH

# Réinstaller PySpark
pip uninstall pyspark
pip install pyspark==3.4.0
```

#### Problème: "Out of memory" Spark
```bash
# Solution: Augmenter la mémoire
export SPARK_DRIVER_MEMORY=4g
export SPARK_EXECUTOR_MEMORY=8g

# Redémarrer Spark
```

#### Problème: "Topic does not exist"
```bash
# Solution: Créer le topic
/opt/kafka/bin/kafka-topics.sh --create --topic streaming-events --bootstrap-server localhost:9092 --partitions 3
```

### Logs et Debugging

#### Fichiers de Logs Importants
- **Kafka**: `/opt/kafka/logs/server.log`
- **ZooKeeper**: `/opt/kafka/logs/zookeeper.log`
- **Spark**: `/tmp/spark-*.out`
- **Producer**: Logs affichés dans la console
- **Consumer**: Logs affichés dans la console

#### Activation du Debug Mode
```bash
# Producer debug
python kafka_producer.py --continuous --delay 0.1

# Consumer debug (modifier le niveau de log dans spark_streaming_app.py)
logging.getLogger().setLevel(logging.DEBUG)
```

## Maintenance

### Backup et Archivage

#### Backup des Checkpoints Spark
```bash
# Backup quotidien
tar -czf checkpoints_backup_$(date +%Y%m%d).tar.gz ./checkpoints/

# Archivage mensuel
mv checkpoints_backup_*.tar.gz archives/
```

#### Backup de la Base SQLite
```bash
# Backup quotidien
cp ./results/streaming_results.db ./backups/streaming_results_$(date +%Y%m%d).db

# Archivage mensuel
tar -czf sqlite_backup_$(date +%Y%m).tar.gz ./backups/*.db
```

#### Backup des Fichiers de Sortie
```bash
# Backup hebdomadaire
tar -czf results_backup_$(date +%Y%m%d).tar.gz ./results/

# Nettoyage des anciens fichiers (> 30 jours)
find ./results/ -type f -mtime +30 -delete
```

### Nettoyage et Maintenance

#### Nettoyage des Fichiers Temporaires
```bash
# Nettoyer les fichiers temporaires Spark
rm -rf /tmp/spark-*
rm -rf /tmp/hive-*

# Nettoyer les logs anciens
find /opt/kafka/logs/ -name "*.log" -mtime +7 -delete
```

#### Vérification de l'Espace Disque
```bash
# Vérifier l'espace disque
df -h

# Nettoyer si nécessaire
sudo apt-get clean
sudo journalctl --vacuum-time=7d
```

### Mises à Jour et Migrations

#### Mise à Jour de Kafka
```bash
# Arrêter Kafka
/opt/kafka/bin/kafka-server-stop.sh

# Télécharger nouvelle version
wget https://downloads.apache.org/kafka/3.6.0/kafka_2.13-3.6.0.tgz

# Extraire et remplacer
tar -xzf kafka_2.13-3.6.0.tgz
sudo mv kafka_2.13-3.6.0 /opt/kafka-new
sudo mv /opt/kafka /opt/kafka-old
sudo mv /opt/kafka-new /opt/kafka

# Copier la configuration
cp /opt/kafka-old/config/* /opt/kafka/config/

# Redémarrer
/opt/kafka/bin/kafka-server-start.sh config/server.properties &
```

#### Mise à Jour de Spark
```bash
# Arrêter Spark
/opt/spark/sbin/stop-all.sh

# Télécharger nouvelle version
wget https://downloads.apache.org/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz

# Extraire et remplacer
tar -xzf spark-3.5.0-bin-hadoop3.tgz
sudo mv spark-3.5.0-bin-hadoop3 /opt/spark-new
sudo mv /opt/spark /opt/spark-old
sudo mv /opt/spark-new /opt/spark

# Mettre à jour les variables d'environnement
export SPARK_HOME=/opt/spark
export PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-*.zip:$PYTHONPATH

# Redémarrer
/opt/spark/sbin/start-all.sh
```

### Scaling et Performance

#### Augmentation du Throughput
```bash
# Augmenter le nombre de partitions Kafka
/opt/kafka/bin/kafka-topics.sh --alter --topic streaming-events --partitions 6 --bootstrap-server localhost:9092

# Augmenter le nombre de Spark executors
export SPARK_EXECUTOR_INSTANCES=4
export SPARK_EXECUTOR_CORES=2
export SPARK_EXECUTOR_MEMORY=4g
```

#### Optimisation de la Mémoire
```bash
# Ajuster la mémoire Spark
export SPARK_DRIVER_MEMORY=4g
export SPARK_EXECUTOR_MEMORY=8g

# Ajuster les partitions de shuffle
export SPARK_SQL_SHUFFLE_PARTITIONS=16
```

#### Monitoring Avancé
```bash
# Installer Prometheus pour le monitoring système
# Installer Grafana pour la visualisation
# Configurer des alertes Slack/Email
```

## Support et Assistance

### Documentation
- **Technical Report**: `docs/technical_report.md`
- **Producer Documentation**: `producer/README.md`
- **Consumer Documentation**: `spark/consumer/README.md`
- **Monitoring Documentation**: `monitoring/README.md`

### Contact
Pour toute question ou problème:
1. Vérifier ce guide utilisateur
2. Consulter les logs appropriés
3. Exécuter les tests de validation
4. Contacter l'équipe technique avec:
   - Description du problème
   - Logs pertinents
   - Étapes pour reproduire
   - Configuration système

### Rapport de Bugs
Pour signaler un bug:
1. Créer un ticket avec:
   - Description détaillée
   - Étapes de reproduction
   - Logs d'erreur
   - Configuration système
2. Joindre les fichiers de logs pertinents
3. Indiquer la version utilisée de Kafka, Spark, Python