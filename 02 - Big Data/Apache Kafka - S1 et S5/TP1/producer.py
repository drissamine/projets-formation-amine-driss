from kafka import KafkaProducer # type: ignore
import json
import random
import time
from datetime import datetime, timezone

# 1. Configuration du producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',  # Serveur Kafka local
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Sérialisation JSON
)

print("Producer IoT demarre")
print("Envoi de donnees toutes les 2 secondes...")

# 2. Liste des batiments et capteurs
buildings = ['A', 'B', 'C']
sensors_per_building = 5

try:
    while True:
        for building in buildings:
            for sensor_num in range(sensors_per_building):
                # 3. Creer les donnees du capteur
                sensor_data = {
                    "sensor_id": f"sensor_{building}_{sensor_num}",
                    "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                    "temperature": round(random.uniform(18, 28), 1),
                    "humidity": random.randint(30, 70),
                    "building": building,
                    "floor": (sensor_num % 3) + 1,
                    "room": str((sensor_num % 10) + 1),
                    "battery_level": random.randint(80, 100)
                }
                
                # 4. Envoyer a Kafka
                producer.send('iot-sensors', value=sensor_data)
                
                # Afficher un message toutes les 5 envois
                if random.random() < 0.2:
                    print(f"[SEND] {sensor_data['sensor_id']}: {sensor_data['temperature']}C")
        
        time.sleep(2)  # Attendre 2 secondes
        
except KeyboardInterrupt:
    print("\nArret du producer")
    producer.flush()
