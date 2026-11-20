#!/usr/bin/env python3
"""
Producteur Kafka pour la Simulation d'Événements Streaming

Génère des événements de streaming aléatoires pour une plateforme de streaming vidéo
afin de simuler les habitudes et comportements de visionnage des utilisateurs.
"""

import json
import random
import time
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any
from kafka import KafkaProducer
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StreamingEventGenerator:
    """Génère des événements de streaming aléatoires pour le producteur Kafka"""
    
    def __init__(self):
        # Constantes de configuration
        self.EVENT_TYPES = ['PLAY', 'PAUSE', 'STOP', 'SEEK']
        self.DEVICES = ['mobile', 'desktop', 'tv']
        self.GENRES = ['action', 'comedy', 'drama', 'thriller', 'romance', 'documentary']
        
        # Pools d'utilisateurs et de vidéos
        self.user_ids = [f"user_{i:04d}" for i in range(1, 101)]  # 100 utilisateurs
        self.video_ids = [f"video_{i:04d}" for i in range(1, 51)]   # 50 vidéos
        
        # Cache des métadonnées vidéos
        self.video_metadata = {}
        for video_id in self.video_ids:
            self.video_metadata[video_id] = {
                'duration': random.randint(60, 1800),  # 1 minute à 30 minutes
                'genre': random.choice(self.GENRES)
            }
    
    def generate_event(self) -> Dict[str, Any]:
        """Génère un événement de streaming unique"""
        # Sélectionner un utilisateur et une vidéo aléatoires
        user_id = random.choice(self.user_ids)
        video_id = random.choice(self.video_ids)
        
        # Obtenir les métadonnées vidéo
        video_info = self.video_metadata[video_id]
        duration = video_info['duration']
        genre = video_info['genre']
        
        # Sélectionner le type d'événement avec probabilités
        event_type = random.choices(
            self.EVENT_TYPES,
            weights=[0.6, 0.2, 0.15, 0.05]  # PLAY: 60%, PAUSE: 20%, STOP: 15%, SEEK: 5%
        )[0]
        
        # Générer le temps courant selon le type d'événement
        if event_type == 'PLAY':
            current_time = 0.0
        elif event_type == 'SEEK':
            current_time = random.uniform(0, duration)
        else:
            # Pour PAUSE et STOP, le temps courant doit être dans la durée vidéo
            current_time = random.uniform(0, duration)
        
        # Générer le timestamp
        timestamp = datetime.now(timezone.utc).isoformat() + 'Z'
        
        # Créer l'événement
        event = {
            "event_id": str(uuid.uuid4()),
            "user_id": user_id,
            "video_id": video_id,
            "event_type": event_type,
            "timestamp": timestamp,
            "current_time": round(current_time, 2),
            "duration": duration,
            "genre": genre,
            "device": random.choice(self.DEVICES)
        }
        
        return event

class KafkaStreamingProducer:
    """Producteur Kafka pour les événements de streaming"""
    
    def __init__(self, bootstrap_servers: str = '127.0.0.1:9092', topic: str = 'streaming-events'):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.generator = StreamingEventGenerator()
        
        # Initialiser le producteur Kafka
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',  # Attendre que tous les réplicas reconnaissent
                retries=3,
                batch_size=16384,
                linger_ms=5,  # Petit délai pour regrouper les messages
                buffer_memory=33554432  # Buffer de 32MB
            )
            logger.info(f"Producteur Kafka initialisé avec succès")
            logger.info(f"Topic: {self.topic}")
            logger.info(f"Serveurs bootstrap: {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"Échec de l'initialisation du producteur Kafka: {e}")
            raise
    
    def send_event(self, event: Dict[str, Any]) -> None:
        """Envoyer un événement unique vers Kafka"""
        try:
            future = self.producer.send(self.topic, event)
            # Attendre l'envoi du message (optionnel, pour confirmation)
            # future.get(timeout=10)
            logger.debug(f"Événement envoyé: {event['event_id']} - {event['event_type']}")
        except Exception as e:
            logger.error(f"Échec de l'envoi de l'événement: {e}")
    
    def generate_and_send_events(self, num_events: int = 1000, delay: float = 0.1):
        """Générer et envoyer plusieurs événements"""
        logger.info(f"Démarrage de la génération de {num_events} événements avec délai de {delay}s")
        
        for i in range(num_events):
            try:
                # Générer événement
                event = self.generator.generate_event()
                
                # Envoyer vers Kafka
                self.send_event(event)
                
                # Journaliser la progression
                if (i + 1) % 100 == 0:
                    logger.info(f"Généré et envoyé {i + 1}/{num_events} événements")
                
                # Délai entre les événements
                time.sleep(delay)
                
            except KeyboardInterrupt:
                logger.info("Interrompu par l'utilisateur, arrêt de la génération")
                break
            except Exception as e:
                logger.error(f"Erreur lors de la génération/envoi de l'événement {i + 1}: {e}")
        
        logger.info("Génération d'événements terminée")
    
    def close(self):
        """Fermer le producteur Kafka"""
        if hasattr(self, 'producer'):
            self.producer.flush()  # S'assurer que tous les messages sont envoyés
            self.producer.close()
            logger.info("Producteur Kafka fermé")

def main():
    """Fonction principale pour exécuter le producteur Kafka"""
    parser = argparse.ArgumentParser(description='Producteur d\'Événements Streaming Kafka')
    parser.add_argument('--bootstrap-servers', default='127.0.0.1:9092',
                       help='Serveurs bootstrap Kafka (défaut: 127.0.0.1:9092)')
    parser.add_argument('--topic', default='streaming-events',
                       help='Nom du topic Kafka (défaut: streaming-events)')
    parser.add_argument('--num-events', type=int, default=1000,
                       help='Nombre d\'événements à générer (défaut: 1000)')
    parser.add_argument('--delay', type=float, default=0.1,
                       help='Délai entre les événements en secondes (défaut: 0.1)')
    parser.add_argument('--continuous', action='store_true',
                       help='Exécuter en continu jusqu\'à l\'interruption')
    
    args = parser.parse_args()
    
    # Créer le producteur
    producer = KafkaStreamingProducer(
        bootstrap_servers=args.bootstrap_servers,
        topic=args.topic
    )
    
    try:
        if args.continuous:
            logger.info("Démarrage de la génération d'événements continue (Ctrl+C pour arrêter)")
            while True:
                event = producer.generator.generate_event()
                producer.send_event(event)
                time.sleep(args.delay)
        else:
            # Générer le nombre spécifié d'événements
            producer.generate_and_send_events(args.num_events, args.delay)
    
    except KeyboardInterrupt:
        logger.info("Signal d'interruption reçu, arrêt en cours...")
    finally:
        producer.close()

if __name__ == "__main__":
    main()