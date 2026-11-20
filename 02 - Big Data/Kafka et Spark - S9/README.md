# Pipeline temps réel Kafka + Spark — Analyse de streaming vidéo

Pipeline de traitement de données en temps réel : ingestion d'événements de
streaming via **Kafka**, traitement avec **Spark Structured Streaming**,
agrégations/alertes en fenêtres glissantes, et stockage (console / CSV / JSON /
SQLite).

```
Sources (producteur) → Kafka → Spark Structured Streaming → Stockage / Visualisation
```

> Rapport technique complet : [`docs/RAPPORT_TECHNIQUE.md`](docs/RAPPORT_TECHNIQUE.md)

---

## Prérequis

- **Docker Desktop** (pour Kafka + Kafka UI)
- **Python 3.9+** (testé sous Python 3.14)
- **JDK 17** (requis par Spark) — variable `JAVA_HOME` définie
- **Windows uniquement** : `winutils.exe` + `hadoop.dll` (Hadoop 3.3.x) dans un
  dossier pointé par `HADOOP_HOME`

> Les chemins `JAVA_HOME` / `HADOOP_HOME` peuvent être surchargés sans toucher au
> système via `JAVA_HOME_OVERRIDE` / `HADOOP_HOME_OVERRIDE` dans le fichier `.env`.

---

## Démarrage rapide

```powershell
# 1. Tout déployer (Docker + topics + dépendances Python)
pwsh scripts/setup.ps1

# 2. Produire des événements (terminal 1)
python -m src.producer.producer --rate 50

# 3. Lancer le pipeline d'agrégations + sorties (terminal 2)
python -m src.consumer.streaming_app --once --from-beginning
```

Kafka UI est disponible sur **http://localhost:8080** (cluster `local`).

---

## Configuration

Tout est centralisé dans **`.env`** (chargé par `config/settings.py`) :

| Variable | Rôle | Défaut |
|---|---|---|
| `KAFKA_BOOTSTRAP_SERVERS` | Brokers (depuis le host) | `localhost:29092` |
| `KAFKA_TOPIC` / `KAFKA_TOPIC_DLQ` | Topics principal / DLQ | `streaming-events` / `-dlq` |
| `EVENTS_PER_SECOND` | Débit du producteur | `50` |
| `WINDOW_DURATION` / `SLIDE_DURATION` | Fenêtres glissantes | `10 minutes` / `5 minutes` |
| `WATERMARK_DELAY` | Tolérance aux retards | `15 minutes` |
| `CHECKPOINT_DIR` | Checkpoints Spark (sans espaces) | `…\.tp-kafka-spark\checkpoints` |
| `RESULTS_DIR` / `SQLITE_DB` | Sorties fichiers / base | `./results` / `streaming_analytics.db` |

---

## Utilisation par partie

### Partie 1 — Simulation (producteur)

```powershell
python -m src.producer.producer                        # débit du .env, en continu
python -m src.producer.producer --total 100000 --rate 5000   # test de charge
python -m src.producer.producer --corrupt-rate 0.02          # injecte des messages invalides (DLQ)
```

### Partie 2 — Traitement Spark

```powershell
# 2.1 Consommateur brut (validation valide/invalide en console)
python -m src.consumer.spark_consumer --once --from-beginning

# 2.2 + 2.3 Agrégations en fenêtres + sorties console/CSV/JSON/SQLite
python -m src.consumer.streaming_app --once --from-beginning
python -m src.consumer.streaming_app --query anomalies          # une seule requête, en continu
#   --query : popularity | engagement | genre | anomalies | all
#   --no-console | --no-files | --no-sqlite | --checkpoint
```

### Partie 3 — Monitoring, erreurs, tests

```powershell
# 3.1 Métriques (throughput, latence, lag) — à lancer en continu pendant la production
python -m src.consumer.metrics_app

# 3.2 Dead-letter queue + checkpoint
python -m src.consumer.dlq_app --once --from-beginning

# 3.3 Tests
python -m pytest tests/ -q                              # tests unitaires
python -m scripts.load_test --volumes 10000,50000,100000   # charge & évolutivité
python -m scripts.crash_recovery_test --volume 30000       # crash & reprise
```

---

## Structure du projet

```
.
├── docker-compose.yml          # Kafka (KRaft) + Kafka UI
├── requirements.txt
├── .env                        # configuration centralisée
├── config/                     # settings.py, log4j2.properties
├── src/
│   ├── producer/               # producteur Kafka (1.1)
│   ├── consumer/               # Spark : consumer, transformations, sinks, metrics, dlq
│   └── common/                 # schéma d'événement, schéma Spark
├── scripts/                    # setup, création topics, tests de charge/crash
├── tests/                      # tests unitaires pytest
├── results/                    # sorties CSV/JSON (générées)
└── docs/                       # rapport technique
```

---

## Dépannage

| Symptôme | Cause / solution |
|---|---|
| `No module named 'kafka.vendor.six'` | `pip install "kafka-python>=2.2"` |
| `ExitCodeException` Spark (Windows) | `winutils.exe`/`hadoop.dll` manquants → définir `HADOOP_HOME` |
| `JAVA_HOME` invalide | installer un JDK 17 et définir `JAVA_HOME_OVERRIDE` dans `.env` |
| Spark ne lit rien | vérifier que les topics existent (`scripts/create_topic.ps1`) et le bootstrap `localhost:29092` |

Voir le détail des difficultés et de leurs solutions dans le
[rapport technique](docs/RAPPORT_TECHNIQUE.md#5-difficultés-rencontrées-et-solutions).
