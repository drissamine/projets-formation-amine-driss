import subprocess
import time
import os
import sys

def run_test():
    print("Démarrage du test complet...")
    ROOT_DIR = r"D:\M2\S9\TP-Projet-Kafka-Spark"
    os.chdir(ROOT_DIR)
    
    # 1. Start Producer
    print("\n[1/3] Lancement du producteur...")
    producer_cmd = [sys.executable, "producer/kafka_producer.py", "--num-events", "200", "--delay", "0.1"]
    producer_proc = subprocess.Popen(producer_cmd)
    
    # 2. Start Spark
    print("\n[2/3] Lancement de Spark...")
    env = os.environ.copy()
    env["HADOOP_HOME"] = ROOT_DIR
    env["PYTHONPATH"] = ROOT_DIR
    
    with open("spark_test_output.log", "w") as log_file:
        spark_cmd = [sys.executable, "spark/consumer/spark_streaming_app.py", "--checkpoint-location", "./checkpoints/spark-test-final"]
        spark_proc = subprocess.Popen(spark_cmd, env=env, stdout=log_file, stderr=subprocess.STDOUT)
        
        print("\nAttente de 90 secondes pour le traitement...")
        # Give Spark more time to start up and process first batch
        for i in range(9):
            time.sleep(10)
            print(f"  { (i+1)*10 }s écoulés...")
        
        # 3. Check SQLite
        print("\n[3/3] Vérification SQLite...")
        db_path = os.path.join(ROOT_DIR, "results", "streaming_results.db")
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            print(f"[OK] Fichier DB: {db_path} ({size} octets)")
            if size > 0:
                import sqlite3
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                c.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [t[0] for t in c.fetchall()]
                print(f"Tables: {tables}")
                for table in tables:
                    c.execute(f"SELECT COUNT(*) FROM {table}")
                    print(f"  - {table}: {c.fetchone()[0]} lignes")
                conn.close()
            else:
                print("[WARNING] Fichier DB vide.")
        else:
            print("[ERROR] Fichier DB absent.")

    producer_proc.terminate()
    spark_proc.terminate()
    print("\nTest terminé.")

if __name__ == "__main__":
    run_test()
