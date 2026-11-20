#!/usr/bin/env python3
"""
Script de diagnostic pour le système de recommandations e-commerce
"""

import sys
import time

def test_kafka():
    """Test la connexion Kafka"""
    print("=== Test Kafka ===")
    try:
        from kafka.admin import KafkaAdminClient
        admin = KafkaAdminClient(bootstrap_servers=['localhost:9092'])
        topics = admin.list_topics()
        admin.close()

        user_topics = [t for t in topics if not t.startswith('__')]
        print(f"Kafka accessible - {len(user_topics)} topics utilisateur")
        for topic in sorted(user_topics):
            print(f"   - {topic}")
        return True
    except Exception as e:
        print(f"ERREUR: Kafka non accessible: {e}")
        print("   Solutions:")
        print("   1. Demarrer ZooKeeper: start kafka\\start_zookeeper.cmd")
        print("   2. Demarrer Kafka: start kafka\\start_kafka.cmd")
        print("   3. Attendre 10-15 secondes")
        return False

def test_topics():
    """Vérifie que les topics nécessaires existent"""
    print("\n=== Test Topics ===")
    try:
        from kafka.admin import KafkaAdminClient, NewTopic
        admin = KafkaAdminClient(bootstrap_servers=['localhost:9092'])
        topics_existants = admin.list_topics()

        topics_requis = ['evenements_utilisateur', 'recommandations', 'metriques']
        topics_manquants = []
        topics_trouves = []

        for topic in topics_requis:
            if topic in topics_existants:
                topics_trouves.append(topic)
            else:
                topics_manquants.append(topic)

        if topics_trouves:
            print(f"Topics trouves: {', '.join(topics_trouves)}")

        if topics_manquants:
            print(f"Topics manquants: {', '.join(topics_manquants)}")
            print("   Creation automatique...")
            nouveaux_topics = [NewTopic(name=t, num_partitions=1, replication_factor=1) for t in topics_manquants]
            admin.create_topics(nouveaux_topics)
            print(f"   {len(nouveaux_topics)} topics crees")

        admin.close()
        return True
    except Exception as e:
        print(f"ERREUR: Erreur topics: {e}")
        return False

def test_composants():
    """Test les imports des composants"""
    print("\n=== Test Composants ===")

    composants = [
        ('modeles', 'Modeles de donnees'),
        ('config', 'Configuration'),
        ('service_suivi', 'Service de suivi'),
        ('moteur_recommandations', 'Moteur de recommandations'),
        ('test_ab', 'Test A/B'),
        ('tableau_bord', 'Tableau de bord')
    ]

    ok = 0
    erreur = 0

    for module, description in composants:
        try:
            __import__(module)
            print(f"OK - {description}")
            ok += 1
        except Exception as e:
            print(f"ERREUR - {description}: {e}")
            erreur += 1

    print(f"\nResultat: {ok} OK, {erreur} erreurs")
    return erreur == 0

def test_dashboard():
    """Test l'accès au dashboard"""
    print("\n=== Test Dashboard ===")
    try:
        import requests
        response = requests.get('http://localhost:5000/api/metrics', timeout=3)
        if response.status_code == 200:
            data = response.json()
            print("Dashboard accessible")
            print(f"   Utilisateurs: {data.get('total_users', 0)}")
            print(f"   Evenements: {data.get('total_events', 0)}")
            print(f"   Recommandations: {data.get('recommendations_generated', 0)}")
            return True
        else:
            print(f"Dashboard repond erreur {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("Dashboard non accessible (port 5000)")
        print("   Solution: python tableau_bord.py")
        return False
    except Exception as e:
        print(f"Erreur dashboard: {e}")
        return False

def recommandations_simulation():
    """Simule quelques recommandations pour tester"""
    print("\n=== Simulation de données ===")
    try:
        from kafka import KafkaProducer
        import json

        producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        # Simuler quelques recommandations
        recommandations = [
            {
                'user_id': 'USER_ALICE',
                'product_ids': ['PROD_005', 'PROD_004'],
                'algorithm': 'categorie',
                'timestamp': '2024-01-01T10:00:00Z'
            },
            {
                'user_id': 'USER_BOB',
                'product_ids': ['PROD_002'],
                'algorithm': 'recommandation',
                'timestamp': '2024-01-01T10:01:00Z'
            }
        ]

        for rec in recommandations:
            producer.send('recommandations', value=rec)
            print(f"Recommandation envoyee pour {rec['user_id']}")

        producer.flush()
        producer.close()
        print("Donnees de test envoyees")
        return True

    except Exception as e:
        print(f"ERREUR: Erreur simulation: {e}")
        return False

def main():
    """Fonction principale de diagnostic"""
    print("Diagnostic du systeme de recommandations e-commerce")
    print("=" * 60)

    tests = [
        ("Connexion Kafka", test_kafka),
        ("Topics requis", test_topics),
        ("Composants Python", test_composants),
        ("Dashboard", test_dashboard),
    ]

    resultats = []
    for nom, fonction in tests:
        print(f"\nTest: {nom}")
        resultat = fonction()
        resultats.append((nom, resultat))

    print("\n" + "=" * 60)
    print("RESULTATS FINAUX:")

    for nom, succes in resultats:
        status = "OK" if succes else "ERREUR"
        print(f"   {status} - {nom}")

    succes_total = sum(1 for _, s in resultats if s)
    print(f"\nScore: {succes_total}/{len(resultats)} tests reussis")

    if succes_total >= 3:  # Au moins Kafka, topics et composants
        print("\nSysteme pret ! Vous pouvez lancer:")
        print("   python tableau_bord.py")
        print("   python service_suivi.py")
        print("   python moteur_recommandations.py")

        # Simuler des données automatiquement
        print("\nSimulation de donnees de test...")
        recommandations_simulation()
    else:
        print("\nProblemes a resoudre avant de continuer")

if __name__ == "__main__":
    main()
