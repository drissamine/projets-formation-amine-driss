# consumer_iot_stats.py - À COMPLÉTER
from kafka import KafkaConsumer # pyright: ignore[reportMissingImports]
import json
from datetime import datetime, timedelta, timezone
from collections import defaultdict

# 1. Configuration du consumer
try:
    consumer = KafkaConsumer(
        'iot-sensors',
        bootstrap_servers='localhost:9092',
        value_deserializer=lambda x: x.decode('utf-8'),
        auto_offset_reset='earliest'
    )
    print("Consumer IoT demarre")
except Exception as e:
    print(f"Erreur de connexion a Kafka: {e}")
    print("Assurez-vous que Zookeeper et Kafka sont demarres.")
    exit(1)
print("Calcul des statistiques par batiment...")

# 2. Structures pour les statistiques
building_stats = defaultdict(list)  # Dictionnaire pour stocker les stats par batiment

# 3. Variables pour la fenetre temporelle
window_start = datetime.now(timezone.utc)
window_duration = timedelta(seconds=30)  # Fenetre de 30 secondes
try:
    for message in consumer:
        try:
            data = json.loads(message.value)  # Decode le JSON après deserialisation UTF-8
            building = data['building']
            temperature = data['temperature']
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Erreur lors du traitement du message: {e}")
            continue
        
        # 4. Detection d'anomalies
        if temperature > 28:
            print(f"ALERTE: Temperature elevee dans {building}: {temperature}C")
        
        # 5. Mettre a jour les statistiques
        building_stats[building].append(temperature)
        # 6. Verifier si la fenetre est terminee
        current_time = datetime.now(timezone.utc)
        if current_time - window_start > window_duration:
            print(f"\n{'='*50}")
            print(f"STATISTIQUES {window_start.strftime('%H:%M:%S')}")
            print('='*50)
            
            # 7. Afficher les stats par batiment
            for building, temps in building_stats.items():
                if temps:  # Verifier qu'il y a des donnees
                    avg_temp = sum(temps) / len(temps)
                    min_temp = min(temps)
                    max_temp = max(temps)
                    print(f"{building:15} | Moyenne: {avg_temp:5.1f}C | Min: {min_temp:5.1f}C | Max: {max_temp:5.1f}C | Nb: {len(temps)}")
            
            # Reinitialiser
            window_start = current_time
            building_stats.clear()  # Reinitialiser les statistiques
except KeyboardInterrupt:
    print("\nArret du consumer")
