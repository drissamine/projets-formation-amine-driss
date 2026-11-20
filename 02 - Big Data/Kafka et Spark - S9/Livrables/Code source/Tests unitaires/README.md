# Tests unitaires

> **Auteur : DRISS Amine**  —  ESIS 2 (2025-2026)


Tests `pytest` du producteur et de la logique Spark (parsing, validation,
raisons d'erreur DLQ, agrégations). **10/10 au vert.**

## Fichiers

| Fichier | Rôle |
|---|---|
| `conftest.py` | Fixtures pytest partagées : session Spark locale (sans Kafka). |
| `test_event_schema.py` | Tests du générateur d'événements (schéma, énumérations, `current_time ≤ duration`, stabilité genre/durée). |
| `test_spark_logic.py` | Tests Spark : parsing/validation, raisons d'erreur DLQ, agrégations en fenêtres. |
| `__init__.py` | Marqueur de package Python. |

## Lancement

```bash
pytest                                  # tous les tests
pytest tests/test_event_schema.py -v     # uniquement le schéma
pytest -W error                          # strict : warnings = erreurs
```

## Détails techniques

- **Session Spark** partagée (`scope="session"`) via `conftest.py` pour éviter
  de relancer une JVM par test.
- **Construction des DataFrames de test via `spark.read.json`** (chemin JVM)
  plutôt que `createDataFrame` : ce dernier déclenche un `RecursionError` de
  la cloudpickle embarquée de pyspark sur Python 3.14.
- **Sans Kafka** : les tests Spark utilisent des fichiers JSON locaux, pas de
  broker nécessaire.