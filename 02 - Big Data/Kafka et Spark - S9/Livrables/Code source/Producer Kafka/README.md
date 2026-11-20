# Producer Kafka

> **Auteur : DRISS Amine**  —  ESIS 2 (2025-2026)


Producteur d'événements de streaming vidéo publié dans Kafka.

## Fichiers

| Fichier | Rôle |
|---|---|
| `producer.py` | Producteur Kafka : génération d'événements + envoi sur le topic `streaming-events` avec clé de partitionnement `user_id`. |
| `event_schema.py` | Générateur d'événements aléatoires cohérents (catalogue vidéo stable : genre/durée fixes par `video_id`, `current_time ≤ duration`). |
| `__init__.py` | Marqueur de package Python. |

## Lancement

```bash
# Démarrage rapide (500 événements)
python -m src.producer.producer --total 500

# Flux continu à 50 evt/s
python -m src.producer.producer --rate 50

# Gros volume (test de charge)
python -m src.producer.producer --total 100000 --rate 1000
```

## Détails techniques

- **Clé de partitionnement** : `user_id` → tous les événements d'un même
  utilisateur tombent dans la même partition (ordre préservé par utilisateur).
- **Sérialisation** : classes `KeySerializer` / `JsonValueSerializer`
  (héritées de `kafka.serializer.Serializer`, signature kafka-python 3.x) →
  **0 warning**.
- **Compression gzip** côté producteur pour réduire l'empreinte réseau.
- **Acks `all`** + `retries=5` pour la fiabilité.
- **Micro-batching** (`linger_ms=20`) pour améliorer le throughput.