#!/usr/bin/env python3
"""
Démonstration du système de recommandations e-commerce
Génère quelques événements de test et montre les recommandations calculées
"""

import time
import json
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient
from datetime import datetime

import modeles
import config

def verifier_kafka():
    """Vérifie que Kafka est accessible"""
    try:
        admin = KafkaAdminClient(bootstrap_servers=config.KAFKA_SERVERS)
        topics = admin.list_topics()
        admin.close()
        return True
    except:
        print("ERREUR: Kafka non accessible. Demarrer ZooKeeper et Kafka d'abord.")
        return False

def creer_topics_si_besoin():
    """Crée les topics nécessaires s'ils n'existent pas"""
    from kafka.admin import NewTopic
    admin = KafkaAdminClient(bootstrap_servers=config.KAFKA_SERVERS)
    topics_existants = admin.list_topics()
    topics_a_creer = []

    for topic_name in [config.TOPIC_EVENEMENTS, config.TOPIC_RECOMMANDATIONS, config.TOPIC_METRIQUES]:
        if topic_name not in topics_existants:
            topics_a_creer.append(NewTopic(name=topic_name, num_partitions=1, replication_factor=1))

    if topics_a_creer:
        admin.create_topics(topics_a_creer)
        print(f"SUCCESS: Topics crees: {[t.name for t in topics_a_creer]}")

    admin.close()

def generer_evenements_test():
    """Génère quelques événements de test"""
    producer = KafkaProducer(
        bootstrap_servers=config.KAFKA_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    print("\nGeneration d'evenements de test...")

    # Scénario de test: Alice navigue sur le site
    evenements = [
        {
            "user_id": "USER_ALICE",
            "session_id": "SESS_ALICE_001",
            "event_type": "VIEW_PRODUCT",
            "product_id": "PROD_004",  # Livre Kafka
            "product_name": "Livre Kafka",
            "categorie": "Livres/Informatique",
            "prix": 49.99,
            "timestamp": datetime.now().isoformat(),
            "page_duration": 45
        },
        {
            "user_id": "USER_ALICE",
            "session_id": "SESS_ALICE_001",
            "event_type": "ADD_TO_CART",
            "product_id": "PROD_004",
            "product_name": "Livre Kafka",
            "categorie": "Livres/Informatique",
            "prix": 49.99,
            "timestamp": datetime.now().isoformat(),
            "page_duration": 0
        },
        {
            "user_id": "USER_ALICE",
            "session_id": "SESS_ALICE_001",
            "event_type": "VIEW_PRODUCT",
            "product_id": "PROD_005",  # Formation Spark
            "product_name": "Formation Spark",
            "categorie": "Formation/Online",
            "prix": 199.99,
            "timestamp": datetime.now().isoformat(),
            "page_duration": 30
        },
        {
            "user_id": "USER_BOB",
            "session_id": "SESS_BOB_001",
            "event_type": "VIEW_PRODUCT",
            "product_id": "PROD_001",  # iPhone
            "product_name": "iPhone 15",
            "categorie": "Électronique/Smartphones",
            "prix": 1199.99,
            "timestamp": datetime.now().isoformat(),
            "page_duration": 60
        },
        {
            "user_id": "USER_BOB",
            "session_id": "SESS_BOB_001",
            "event_type": "PURCHASE",
            "product_id": "PROD_001",
            "product_name": "iPhone 15",
            "categorie": "Électronique/Smartphones",
            "prix": 1199.99,
            "timestamp": datetime.now().isoformat(),
            "page_duration": 0
        }
    ]

    for i, event in enumerate(evenements, 1):
        producer.send(config.TOPIC_EVENEMENTS, value=event)
        print(f"  {i}. {event['event_type']} - {event['product_name']} ({event['user_id']})")
        time.sleep(0.5)  # Petit délai pour simuler le temps réel

    producer.flush()
    producer.close()
    print("Evenements de test generes")

def attendre_recommandations():
    """Attend et affiche les recommandations générées"""
    print("\nAttente des recommandations...")

    consumer = KafkaConsumer(
        config.TOPIC_RECOMMANDATIONS,
        bootstrap_servers=config.KAFKA_SERVERS,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='earliest',
        consumer_timeout_ms=10000  # Timeout après 10 secondes
    )

    recommandations_recues = []

    try:
        for message in consumer:
            rec = message.value
            recommandations_recues.append(rec)
            print(f"\nRecommandation pour {rec['user_id']}:")
            print(f"   Produit consulte: {rec['current_product']}")
            print(f"   Algorithme: {rec['algorithm']}")
            print(f"   Recommandations: {rec['product_ids']}")

            # Afficher les noms des produits recommandés
            for prod_id in rec['product_ids'][:3]:  # Max 3 pour lisibilité
                prod_nom = next((p['name'] for p in modeles.produits if p['id'] == prod_id), prod_id)
                print(f"     -> {prod_nom}")

    except Exception as e:
        if recommandations_recues:
            print(f"\n{len(recommandations_recues)} recommandations recues")
        else:
            print(f"\nAucune recommandation recue (timeout): {e}")

    consumer.close()
    return recommandations_recues

def calculer_metriques_ab(recommandations):
    """Calcule les métriques A/B des recommandations"""
    if not recommandations:
        return

    print("\nMetriques A/B:")

    algo_count = {}
    for rec in recommandations:
        algo = rec['algorithm']
        algo_count[algo] = algo_count.get(algo, 0) + 1

    total = len(recommandations)
    for algo, count in algo_count.items():
        pourcentage = (count / total) * 100
        print(".1f")

def demo_complete():
    """Démonstration complète du système"""
    print("Demonstration du systeme de recommandations e-commerce")
    print("=" * 60)

    # 1. Vérifier les prérequis
    if not verifier_kafka():
        return

    # 2. Créer les topics si nécessaire
    creer_topics_si_besoin()

    # 3. Générer des événements de test
    generer_evenements_test()

    # 4. Attendre et afficher les recommandations
    recommandations = attendre_recommandations()

    # 5. Calculer les métriques
    calculer_metriques_ab(recommandations)

    print("\n" + "=" * 60)
    print("Demonstration terminee !")
    print("\nLe systeme a montre :")
    print("- Collecte d'evenements en temps reel")
    print("- Calcul de recommandations personnalisees")
    print("- Test A/B automatique entre algorithmes")
    print("- Metriques de performance")

    if recommandations:
        print(f"\nSUCCES: {len(recommandations)} recommandations generees avec succes !")
    else:
        print("\nWARNING: Verifier que le moteur de recommandations fonctionne")

if __name__ == "__main__":
    demo_complete()
