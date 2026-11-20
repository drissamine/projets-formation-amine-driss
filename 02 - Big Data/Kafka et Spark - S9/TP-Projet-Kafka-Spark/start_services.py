#!/usr/bin/env python3
"""
Script pour demarrer ZooKeeper et Kafka de maniere fiable
"""
import subprocess
import time
import os
import shutil

def main():
    print("=" * 60)
    print("Demarrage du Pipeline Kafka-Spark")
    print("=" * 60)
    
    # Chemins
    KAFKA_BIN = r"d:\M2\S9\kafka-install\kafka_2.13-3.8.1\bin\windows"
    CONFIG_DIR = r"d:\M2\S9\TP-Projet-Kafka-Spark\kafka\config"
    ROOT_DIR = r"D:\M2\S9\TP-Projet-Kafka-Spark"
    
    # 1. Nettoyer les donnees
    print("\n[1/4] Nettoyage des donnees...")
    folders_to_clean = [
        os.path.join(ROOT_DIR, 'zookeeper-data'),
        os.path.join(ROOT_DIR, 'zookeeper-logs'),
        os.path.join(ROOT_DIR, 'kafka-logs'),
        os.path.join(ROOT_DIR, 'checkpoints'),
        r"C:\tmp\kafka-logs",
        r"C:\tmp\zookeeper"
    ]
    
    for folder in folders_to_clean:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f"  - Nettoyé: {folder}")
            except Exception as e:
                print(f"  - Erreur nettoyage {folder}: {e}")
        
        if not folder.startswith("C:\\tmp"): # Only recreate local folders
             os.makedirs(folder, exist_ok=True)
    
    # Clean old database
    db_path = os.path.join(ROOT_DIR, "results", "streaming_results.db")
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"  - Supprimé: {db_path}")
        except Exception as e:
            print(f"  - Erreur suppression DB: {e}")

    print("[OK] Donnees nettoyees")
    
    # 2. Demarrer ZooKeeper
    print("\n[2/4] Demarrage de ZooKeeper...")
    zk_cmd = f'start "ZooKeeper" cmd /k "{KAFKA_BIN}\\zookeeper-server-start.bat" "{CONFIG_DIR}\\zookeeper.properties"'
    subprocess.Popen(zk_cmd, shell=True)
    print("[OK] ZooKeeper lance")
    
    # Attendre que ZooKeeper soit pret
    print("Attente du demarrage de ZooKeeper (15s)...")
    time.sleep(15)
    
    # 3. Demarrer Kafka
    print("\n[3/4] Demarrage de Kafka...")
    kafka_cmd = f'start "Kafka" cmd /k "{KAFKA_BIN}\\kafka-server-start.bat" "{CONFIG_DIR}\\server.properties"'
    subprocess.Popen(kafka_cmd, shell=True)
    print("[OK] Kafka lance")
    
    # Attendre que Kafka soit pret
    print("Attente du demarrage de Kafka (25s)...")
    time.sleep(25)
    
    # 4. Creer le topic
    print("\n[4/4] Creation du topic streaming-events...")
    topic_cmd = [
        os.path.join(KAFKA_BIN, "kafka-topics.bat"),
        "--bootstrap-server", "127.0.0.1:9092",
        "--create",
        "--topic", "streaming-events",
        "--partitions", "3",
        "--replication-factor", "1"
    ]
    try:
        result = subprocess.run(topic_cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("[OK] Topic streaming-events cree")
        else:
            print(f"Note: {result.stdout} {result.stderr}")
    except Exception as e:
        print(f"Note: Impossible de creer le topic: {e}")
    
    print("\n" + "=" * 60)
    print("Services demarres:")
    print("  - ZooKeeper: 127.0.0.1:2181")
    print("  - Kafka:     127.0.0.1:9092")
    print("============================================================")
    print("ETAPE SUIVANTE: Lancer le producteur et Spark")
    print("============================================================")

if __name__ == "__main__":
    main()
