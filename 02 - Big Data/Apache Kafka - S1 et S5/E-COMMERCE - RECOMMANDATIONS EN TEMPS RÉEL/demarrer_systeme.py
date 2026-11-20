import subprocess
import threading
import time
import os
import sys

def demarrer_zookeeper():
    """Démarre ZooKeeper"""
    print("Démarrage de ZooKeeper...")
    try:
        # Utiliser le script Windows
        result = subprocess.run([os.path.join("kafka", "bin", "windows", "zookeeper-server-start.bat"),
                                os.path.join("kafka", "config", "zookeeper.properties")],
                               capture_output=True, text=True, cwd=".")
        print("ZooKeeper démarré")
        return True
    except Exception as e:
        print(f"Erreur démarrage ZooKeeper: {e}")
        return False

def demarrer_kafka():
    """Démarre Kafka"""
    print("Démarrage de Kafka...")
    try:
        # Attendre que ZooKeeper soit prêt
        time.sleep(5)
        result = subprocess.run([os.path.join("kafka", "bin", "windows", "kafka-server-start.bat"),
                                os.path.join("kafka", "config", "server.properties")],
                               capture_output=True, text=True, cwd=".")
        print("Kafka démarré")
        return True
    except Exception as e:
        print(f"Erreur démarrage Kafka: {e}")
        return False

def installer_dependances():
    """Installe les dépendances Python"""
    print("Installation des dépendances...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "exigences.txt"], check=True)
        print("Dépendances installées")
        return True
    except Exception as e:
        print(f"Erreur installation dépendances: {e}")
        return False

def creer_topics():
    """Crée les topics Kafka nécessaires"""
    print("Création des topics Kafka...")
    topics = ["evenements_utilisateur", "recommandations", "metriques"]

    for topic in topics:
        try:
            subprocess.run([os.path.join("kafka", "bin", "windows", "kafka-topics.bat"),
                           "--create", "--topic", topic, "--bootstrap-server", "localhost:9092",
                           "--partitions", "1", "--replication-factor", "1"],
                          capture_output=True, text=True, cwd=".")
            print(f"Topic {topic} créé")
        except Exception as e:
            print(f"Erreur création topic {topic}: {e}")

    time.sleep(2)  # Attendre que les topics soient prêts

def demarrer_services():
    """Démarre tous les services en parallèle"""
    print("Démarrage des services...")

    # Importer ici pour éviter les erreurs d'import si dépendances non installées
    import service_suivi
    import moteur_recommandations
    import tableau_bord

    # Créer instances
    service_suivi_instance = service_suivi.ServiceSuivi()
    moteur_instance = moteur_recommandations.MoteurRecommandations()

    # Thread pour le service de suivi
    def thread_service_suivi():
        service_suivi_instance.simuler_evenements()

    # Thread pour le moteur de recommandations
    def thread_moteur():
        moteur_instance.demarrer()

    # Thread pour le dashboard
    def thread_dashboard():
        tableau_bord.demarrer_dashboard(moteur_instance)

    # Démarrer les threads
    t1 = threading.Thread(target=thread_service_suivi, daemon=True)
    t2 = threading.Thread(target=thread_moteur, daemon=True)
    t3 = threading.Thread(target=thread_dashboard, daemon=True)

    t1.start()
    print("Service de suivi démarré")

    t2.start()
    print("Moteur de recommandations démarré")

    t3.start()
    print("Dashboard démarré")

    # Garder le programme principal actif
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Arrêt du système...")

def main():
    """Fonction principale pour démarrer tout le système"""
    print("Demarrage du systeme de recommandations e-commerce...")

    # Étape 1: Installer dépendances
    if not installer_dependances():
        return

    # Étape 2: Démarrer ZooKeeper
    if not demarrer_zookeeper():
        return

    # Étape 3: Démarrer Kafka
    if not demarrer_kafka():
        return

    # Étape 4: Créer topics
    creer_topics()

    # Étape 5: Démarrer les services
    demarrer_services()

if __name__ == "__main__":
    main()
