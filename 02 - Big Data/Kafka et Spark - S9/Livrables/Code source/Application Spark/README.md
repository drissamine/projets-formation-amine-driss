# Application Spark

> **Auteur : DRISS Amine**  —  ESIS 2 (2025-2026)


Consommateur Spark Structured Streaming : lecture Kafka, parsing/validation,
agrégations en fenêtres glissantes, sorties multiples, métriques, DLQ.

## Fichiers

| Fichier | Rôle | Tâche |
|---|---|---|
| `spark_consumer.py` | Construction de la `SparkSession` + lecture du topic Kafka. | 2.1 |
| `spark_schema.py` | Schéma strict + `parse_kafka_stream()` + `split_valid_invalid()` (valides vs invalides). | 2.1 |
| `transformations.py` | Les 4 requêtes d'agrégation en fenêtres glissantes (10 min / slide 5 min). | 2.2 |
| `streaming_app.py` | Application principale : Kafka → parsing → agrégations → console/CSV/JSON/SQLite. | 2.2, 2.3 |
| `sinks.py` | Sorties : fichiers CSV/JSON + SQLite (sans pandas, stdlib uniquement). | 2.3 |
| `metrics.py` | `MetricsListener` (throughput + lag) + latence end-to-end. | 3.1 |
| `metrics_app.py` | Application de monitoring temps réel. | 3.1 |
| `error_handling.py` | `with_error_reason()` : raison d'erreur attachée aux messages invalides. | 3.2 |
| `dlq_app.py` | Routeur Dead-Letter Queue + checkpoint Kafka → Kafka. | 3.2 |
| `settings.py` | Configuration centralisée (brokers, fenêtres, chemins, anomalies). | — |
| `log4j2.properties` | Configuration log4j2 (console propre, niveau ERROR). | — |
| `__init__.py` | Marqueur de package Python. | — |

## Lancement

```bash
# Tâche 2.1 — Validationflux valide / invalide
python -m src.consumer.spark_consumer --once --from-beginning

# Tâche 2.2 / 2.3 — Toutes les requêtes, toutes les sorties (backlog)
python -m src.consumer.streaming_app --once --from-beginning

# En continu, requêtes seules
python -m src.consumer.streaming_app --query anomalies

# Tâche 3.1 — Monitoring temps réel
python -m src.consumer.metrics_app

# Tâche 3.2 — Routeur DLQ
python -m src.consumer.dlq_app --once --from-beginning
```

## Architecture interne

```
Kafka (streaming-events)
   │
   ▼
parse_kafka_stream()  ──►  split_valid_invalid()
   │                              │
   │ valides                      │ invalides
   ▼                              ▼
transformations.* (4 requêtes)   error_handling.with_error_reason()
   │                              │
   ▼                              ▼
sinks.write_batch()              dlq_app → Kafka (streaming-events-dlq)
  ├─ Console                      + checkpointLocation (reprise sur incident)
  ├─ CSV / JSON (results/<req>/<date>/)
  └─ SQLite (streaming_analytics.db)
```

## Choix techniques notables

- **`outputMode("update")`** : incrémental et performant. Le mode `complete`
  a été écarté (recalcul de tout l'état à chaque micro-batch → timeout sur
  le Top-N).
- **`approx_count_distinct`** pour les comptes distincts (les agrégations
  distinctes exactes ne sont pas supportées en streaming).
- **`watch_time_proxy = max(current_time) - min(current_time)`** :
  approximation documentée (les événements simulés sont des instantanés sans
  durée explicite).
- **Top-N par fenêtre** via `foreachBatch` + `row_number()` (le ranking par
  fenêtre n'est pas exprimable directement sur un flux).
- **Sans pandas** : `toPandas()` importe `distutils`, supprimé en Python 3.12+.
  Les sorties utilisent `csv`/`json`/`sqlite3` (stdlib).