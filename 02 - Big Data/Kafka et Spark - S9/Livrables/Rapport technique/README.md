# Rapport technique

> **Auteur : DRISS Amine**  —  ESIS 2 (2025-2026)


Document principal : `RAPPORT_TECHNIQUE.md` (format Markdown).

## Contenu

Le rapport couvre les 6 sections demandées dans le sujet du TP :

1. **Introduction et contexte** — objectif, stack, architecture globale.
2. **Architecture détaillée** — schéma du pipeline, tableau des composants,
   configuration Kafka (3 partitions / 7 jours / KRaft), schéma des événements.
3. **Choix techniques justifiés** — format des données (JSON + clé `user_id`),
   taille des fenêtres (10 min / slide 5 min + watermark 15 min), stratégie de
   checkpoint, mode de sortie (`update` vs `complete`).
4. **Résultats et performances** — validation fonctionnelle, métriques
   (latence ~2,5 s, lag 0), évolutivité 10K/50K/100K, reprise sur crash
   (30000/30000), DLQ (74), tests (10/10). **Screenshots intégrés.**
5. **Difficultés rencontrées et solutions** — tableau des 9 incompatibilités
   Windows/Python 3.14 résolues (Java, winutils, kafka-python, distutils,
   cloudpickle, log4j, checkpoints…).
6. **Améliorations potentielles** — Avro + Schema Registry, PostgreSQL/Delta,
   exactly-once, Grafana, scalabilité horizontale, etc.

## Screenshots

Les 13 captures sont dans `screenshots/` :

| # | Fichier | Contenu |
|---|---|---|
| 01 | `01_producer.png` | Sortie du producteur (~567 evt/s) |
| 02 | `02_validation.png` | Consommateur 2.1 : flux valide + DLQ |
| 03 | `03_popularite.png` | Requête 1 : Top 10 vidéos par fenêtre |
| 04 | `04_anomalies.png` | Requête 4 : DEVICE_FLOOD + TOO_MANY_VIDEOS |
| 05 | `05_genre.png` | Requête 3 : analyse par genre |
| 06 | `06_sqlite.png` | Tables SQLite peuplées (5 requêtes) |
| 07 | `07_dlq.png` | Topic `streaming-events-dlq` (74 messages) |
| 08 | `08_charge.png` | Test 100K événements (19k prod / 33k traités) |
| 09 | `09_crash.png` | Crash + reprise (30000/30000, 0 perte) |
| 10 | `10_tests.png` | `pytest` 10/10 |
| 11 | `11_kafkaui_topics.png` | Kafka UI — cluster + topics |
| 12 | `12_kafkaui_messages.png` | Kafka UI — messages de `streaming-events` |
| 13 | `13_kafkaui_dlq.png` | Kafka UI — messages de la DLQ |

## Export

Le rapport est en Markdown. Pour l'exporter en PDF/Word :

```bash
# PDF (nécessite pandoc + LaTeX)
pandoc RAPPORT_TECHNIQUE.md -o RAPPORT_TECHNIQUE.pdf

# Word
pandoc RAPPORT_TECHNIQUE.md -o RAPPORT_TECHNIQUE.docx
```