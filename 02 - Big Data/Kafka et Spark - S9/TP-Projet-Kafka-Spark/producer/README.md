# Kafka Producer - Streaming Events Generator

## Description
Générateur d'événements de streaming pour simuler les habitudes de visionnage d'une plateforme de streaming vidéo.

## Fonctionnalités
- Génération d'événements aléatoires (PLAY, PAUSE, STOP, SEEK)
- Simulation de différents devices (mobile, desktop, tv)
- Gestion de différents genres de vidéos
- Format JSON conforme au schéma spécifié

## Installation

### Prérequis
- Python 3.9+
- Kafka installé et en cours d'exécution

### Dépendances
```bash
pip install -r requirements.txt
```

## Utilisation

### Génération de 1000 événements
```bash
python kafka_producer.py --num-events 1000 --delay 0.1
```

### Mode continu (jusqu'à interruption)
```bash
python kafka_producer.py --continuous --delay 0.5
```

### Configuration personnalisée
```bash
python kafka_producer.py \
  --bootstrap-servers localhost:9092 \
  --topic streaming-events \
  --num-events 5000 \
  --delay 0.05
```

## Schéma des Événements

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

## Configuration

### Probabilités des Types d'Événements
- PLAY: 60%
- PAUSE: 20%
- STOP: 15%
- SEEK: 5%

### Pool d'utilisateurs
- 100 utilisateurs uniques (user_0001 à user_0100)

### Pool de vidéos
- 50 vidéos uniques (video_0001 à video_0050)
- Durée aléatoire: 1 à 30 minutes
- Genre aléatoire parmi 6 catégories

## Exécution

1. Démarrer Kafka
2. Créer le topic `streaming-events`
3. Exécuter le producteur

```bash
# Démarrer Kafka (dans un terminal)
./kafka-server-start.sh config/server.properties

# Créer le topic
./kafka-topics.sh --create --topic streaming-events --bootstrap-server localhost:9092 --partitions 3

# Exécuter le producteur
python kafka_producer.py
```

## Monitoring

Le producteur affiche des logs avec:
- Progression de la génération
- Confirmation de l'envoi des événements
- Erreurs éventuelles
- Statistiques de performance