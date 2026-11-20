#!/usr/bin/env python3
"""
Script pour créer automatiquement les topics Kafka nécessaires
pour le système de détection de fraude bancaire.

Topics créés :
- transactions : Flux des transactions bancaires
- alertes : Alertes de fraude générées
- suspectes : Transactions suspectes archivées

Utilisation :
python creer_topics.py
"""

from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError, NoBrokersAvailable
import sys
import time

def creer_topics_kafka():
    """Crée les topics Kafka nécessaires pour le système de fraude"""

    # Configuration Kafka
    bootstrap_servers = ['localhost:9092']
    topics_a_creer = [
        {
            'name': 'transactions',
            'num_partitions': 1,
            'replication_factor': 1,
            'topic_configs': {'retention.ms': '604800000'}  # 7 jours
        },
        {
            'name': 'alertes',
            'num_partitions': 1,
            'replication_factor': 1,
            'topic_configs': {'retention.ms': '2592000000'}  # 30 jours
        },
        {
            'name': 'suspectes',
            'num_partitions': 1,
            'replication_factor': 1,
            'topic_configs': {'retention.ms': '2592000000'}  # 30 jours
        }
    ]

    try:
        print("Connexion a Kafka...")
        admin_client = KafkaAdminClient(
            bootstrap_servers=bootstrap_servers,
            client_id='topic-creator'
        )

        print("Connecte a Kafka")

        # Lister les topics existants
        topics_existants = admin_client.list_topics()
        print(f"Topics existants : {len(topics_existants)}")

        topics_crees = []
        topics_existants_liste = []

        for topic_config in topics_a_creer:
            topic_name = topic_config['name']

            if topic_name in topics_existants:
                print(f"WARNING: Topic '{topic_name}' existe deja")
                topics_existants_liste.append(topic_name)
                continue

            # Créer le nouveau topic
            new_topic = NewTopic(
                name=topic_config['name'],
                num_partitions=topic_config['num_partitions'],
                replication_factor=topic_config['replication_factor'],
                topic_configs=topic_config['topic_configs']
            )

            try:
                admin_client.create_topics([new_topic])
                print(f"SUCCESS: Topic '{topic_name}' cree avec succes")
                print(f"   - Partitions: {topic_config['num_partitions']}")
                print(f"   - Replication: {topic_config['replication_factor']}")
                print(f"   - Configuration: {topic_config['topic_configs']}")
                topics_crees.append(topic_name)

            except TopicAlreadyExistsError:
                print(f"WARNING: Topic '{topic_name}' existe deja (erreur concurrente)")
                topics_existants_liste.append(topic_name)
            except Exception as e:
                print(f"ERREUR: Erreur lors de la creation du topic '{topic_name}': {e}")

        # Attendre que les topics soient disponibles
        if topics_crees:
            print("\nAttente de la disponibilite des topics...")
            time.sleep(2)

        # Vérifier la création
        topics_verifies = admin_client.list_topics()

        print("\nResume de l'operation :")
        print(f"   - Topics demandes : {len(topics_a_creer)}")
        print(f"   - Topics crees : {len(topics_crees)}")
        print(f"   - Topics existants : {len(topics_existants_liste)}")
        print(f"   - Total topics Kafka : {len(topics_verifies)}")

        if topics_crees:
            print(f"\nTopics crees : {', '.join(topics_crees)}")

        if topics_existants_liste:
            print(f"Topics deja existants : {', '.join(topics_existants_liste)}")

        # Lister tous les topics avec détails
        print("\nTous les topics du systeme :")
        for topic in ['transactions', 'alertes', 'suspectes']:
            if topic in topics_verifies:
                try:
                    desc = admin_client.describe_topics([topic])
                    partitions = len(desc[0]['partitions'])
                    print(f"   - {topic} : {partitions} partition(s) OK")
                except:
                    print(f"   - {topic} : cree OK")
            else:
                print(f"   - {topic} : manquant ERROR")

        admin_client.close()
        print("\nOperation terminee avec succes !")
        return True

    except NoBrokersAvailable:
        print("ERREUR: Impossible de se connecter a Kafka")
        print("   Verifiez que Kafka est demarre sur localhost:9092")
        print("   Demarrez ZooKeeper puis Kafka avec les scripts start_zookeeper.cmd et start_kafka.cmd")
        return False

    except Exception as e:
        print(f"ERREUR: Erreur inattendue : {e}")
        return False

def afficher_aide():
    """Affiche l'aide du script"""
    print("Créateur automatique de topics Kafka pour le système de détection de fraude")
    print("\nUtilisation :")
    print("  python creer_topics.py")
    print("\nPrérequis :")
    print("  - Kafka doit être démarré")
    print("  - ZooKeeper doit être démarré")
    print("\nTopics créés :")
    print("  - transactions : Flux des transactions bancaires")
    print("  - alertes : Alertes de fraude générées")
    print("  - suspectes : Transactions suspectes archivées")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        afficher_aide()
    else:
        print("Creation automatique des topics Kafka")
        print("=" * 50)

        success = creer_topics_kafka()

        if not success:
            print("\nConseils de depannage :")
            print("   1. Verifiez que ZooKeeper est demarre")
            print("   2. Verifiez que Kafka est demarre")
            print("   3. Attendez quelques secondes apres le demarrage de Kafka")
            print("   4. Verifiez les logs de Kafka pour les erreurs")

            sys.exit(1)
        else:
            sys.exit(0)
