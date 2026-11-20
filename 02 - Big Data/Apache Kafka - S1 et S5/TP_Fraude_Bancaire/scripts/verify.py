# Créé par DRISS Amine
from kafka import KafkaConsumer
import json

def count_messages(topic):
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers='localhost:9092',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        consumer_timeout_ms=5000  # 5 seconds timeout
    )
    count = 0
    try:
        for message in consumer:
            count += 1
    except:
        pass
    consumer.close()
    return count

print("Vérification des topics :")
print(f"Transactions: {count_messages('transactions')}")
print(f"Suspectes: {count_messages('suspectes')}")
print(f"Alertes: {count_messages('alertes')}")
