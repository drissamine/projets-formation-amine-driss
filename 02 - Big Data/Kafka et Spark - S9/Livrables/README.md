# Livrables — Pipeline temps réel Kafka + Spark

> **Auteur : DRISS Amine**  —  ESIS 2 (2025-2026)


**TP Projet — Traitement de données en temps réel avec Kafka et Spark**
ESIS 2 (2025-2026) — Apache Kafka et Spark

Pipeline d'analyse en temps réel des habitudes de visionnage vidéo :
ingestion Kafka → traitement Spark Structured Streaming → agrégations,
alertes et stockage (console / CSV / JSON / SQLite).

```
Sources (producteur) → Kafka → Spark Structured Streaming → Stockage / Visualisation
```

## Arborescence

```
Livrables/
├── Code source/
│   ├── Producer Kafka/            # Producteur Kafka (Python)
│   │   ├── producer.py
│   │   ├── event_schema.py
│   │   └── README.md
│   ├── Application Spark/         # Consommateur Spark Structured Streaming
│   │   ├── spark_consumer.py      # Tâche 2.1
│   │   ├── transformations.py     # Tâche 2.2 (4 requêtes fenêtrées)
│   │   ├── streaming_app.py       # Tâche 2.2 + 2.3 (application)
│   │   ├── sinks.py               # Tâche 2.3 (sorties CSV/JSON/SQLite)
│   │   ├── metrics.py             # Tâche 3.1
│   │   ├── metrics_app.py         # Tâche 3.1
│   │   ├── error_handling.py      # Tâche 3.2
│   │   ├── dlq_app.py             # Tâche 3.2
│   │   ├── spark_schema.py
│   │   ├── settings.py
│   │   ├── log4j2.properties
│   │   └── README.md
│   ├── Scripts de deploiement/    # Infrastructure + tests de charge
│   │   ├── docker-compose.yml
│   │   ├── requirements.txt
│   │   ├── .env.example
│   │   ├── setup.ps1
│   │   ├── create_topic.ps1 / .sh
│   │   ├── load_test.py           # Tâche 3.3 (charge/évolutivité)
│   │   ├── crash_recovery_test.py # Tâche 3.3 (crash/reprise)
│   │   └── README.md
│   └── Tests unitaires/           # pytest 10/10
│       ├── conftest.py
│       ├── test_event_schema.py
│       ├── test_spark_logic.py
│       └── README.md
├── Rapport technique/
│   ├── RAPPORT_TECHNIQUE.md       # 6 sections (voir ci-dessous)
│   ├── screenshots/               # 13 PNG
│   └── README.md
└── README.md                      # (ce fichier)
```

## Rapport technique — plan

1. Introduction et contexte
2. Architecture détaillée
3. Choix techniques justifiés (format des données, taille des fenêtres,
   stratégie de checkpoint)
4. Résultats et performances (screenshots des sorties + métriques)
5. Difficultés rencontrées et solutions
6. Améliorations potentielles

## Mise en route

Voir `Code source/Scripts de deploiement/README.md` pour le déploiement
complet. En résumé :

```powershell
# 1. Démarrer Kafka + Kafka UI
docker compose up -d
# 2. Créer les topics
pwsh scripts/create_topic.ps1      # ou: bash scripts/create_topic.sh
# 3. Installer les dépendances Python
pip install -r requirements.txt
# 4. Copier .env.example en .env et adapter les chemins (JAVA_HOME, etc.)
# 5. Lancer le pipeline
python -m src.consumer.streaming_app --once --from-beginning
```

## Stack

- **Kafka 3.7** (mode KRaft, sans Zookeeper) + Kafka UI — via Docker
- **Spark 3.5.1** (Structured Streaming) — local
- **Python 3** (kafka-python 3.x, pyspark 3.5.1)
- **JDK 17** requis pour Spark (Temurin)
- **SQLite** (stdlib) pour le stockage des résultats

## État

Toutes les tâches 1.1 → 3.3 sont implémentées, testées sur données réelles et
**sans warning** (code vérifié avec `python -W error`, logs Spark filtrés).