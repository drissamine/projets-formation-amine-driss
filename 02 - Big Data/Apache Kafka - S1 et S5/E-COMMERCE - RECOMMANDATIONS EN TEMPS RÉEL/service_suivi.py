import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer

import modeles
import config

class ServiceSuivi:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=config.KAFKA_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def creer_evenement(self, user_id: str, session_id: str, event_type: str,
                       product_id: str, product_name: str, categorie: str,
                       prix: float, page_duration: int = 0) -> dict:
        """Crée un événement utilisateur au format JSON"""
        return {
            "user_id": user_id,
            "session_id": session_id,
            "event_type": event_type,
            "product_id": product_id,
            "product_name": product_name,
            "categorie": categorie,
            "prix": prix,
            "timestamp": datetime.now().isoformat(),
            "page_duration": page_duration,
            "user_agent": "Chrome/Mobile",
            "location": "Paris, FR"
        }

    def envoyer_evenement(self, evenement: dict):
        """Envoie un événement vers Kafka"""
        try:
            future = self.producer.send(config.TOPIC_EVENEMENTS, value=evenement)
            record_metadata = future.get(timeout=10)
            print(f"Événement envoyé: {evenement['event_type']} pour {evenement['product_name']}")
        except Exception as e:
            print(f"Erreur envoi événement: {e}")

    def simuler_evenements(self):
        """Simule des événements utilisateur pour la démonstration"""
        utilisateurs = ["USER_TECH", "USER_FOODIE", "USER_NEW"]
        produits = modeles.produits

        session_id = f"SESS_{int(time.time())}"

        while True:
            # Sélection aléatoire d'utilisateur et produit
            user_id = random.choice(utilisateurs)
            produit = random.choice(produits)

            # Types d'événements possibles
            event_types = ["VIEW_PRODUCT", "ADD_TO_CART", "PURCHASE"]
            weights = [0.7, 0.2, 0.1]  # Probabilités
            event_type = random.choices(event_types, weights=weights)[0]

            # Durée de page pour VIEW_PRODUCT
            page_duration = random.randint(10, 120) if event_type == "VIEW_PRODUCT" else 0

            # Créer et envoyer l'événement
            evenement = self.creer_evenement(
                user_id=user_id,
                session_id=session_id,
                event_type=event_type,
                product_id=produit["id"],
                product_name=produit["name"],
                categorie=produit["categorie"],
                prix=produit["prix"],
                page_duration=page_duration
            )

            self.envoyer_evenement(evenement)

            # Attendre avant le prochain événement
            time.sleep(config.DELAI_SIMULATION_EVENEMENTS)

if __name__ == "__main__":
    service = ServiceSuivi()
    print("Service de suivi démarré - Simulation d'événements...")
    service.simuler_evenements()
