# Créé par DRISS Amine
import json
import time
from collections import defaultdict
from datetime import datetime, timedelta
from kafka import KafkaConsumer, KafkaProducer

# Configuration
consumer = KafkaConsumer(
    'transactions',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='earliest',
    group_id='fraud_detector'
)

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Pays à risque
pays_risques = ['RU', 'CN', 'IR', 'BR', 'NG', 'TR']

# État des clients
client_timestamps = defaultdict(list)
client_merchants = defaultdict(set)

def process_transaction(tx):
    client = tx['client_id']
    ts_str = tx['timestamp']
    ts = datetime.fromisoformat(ts_str[:-1])  # remove Z
    montant = tx['montant']
    pays = tx['pays_marchand']
    marchand = tx['marchand']
    heure = ts.hour

    alerts = []

    # Règles directes
    if montant > 5000:
        alerts.append({"rule": "MONTANT_ELEVE", "severity": "HIGH"})

    if pays in pays_risques:
        alerts.append({"rule": "PAYS_RISQUE", "severity": "MEDIUM"})

    if 0 <= heure <= 5:
        alerts.append({"rule": "HEURE_INHABITUELLE", "severity": "LOW"})

    # Nouveau marchand
    if marchand not in client_merchants[client]:
        alerts.append({"rule": "NOUVEAU_MARCHAND", "severity": "LOW"})

    # Ajouter à l'état
    client_timestamps[client].append(ts)
    client_merchants[client].add(marchand)

    # Vérifier transactions rapides (dernières 5 minutes)
    recent = [t for t in client_timestamps[client] if ts - t <= timedelta(minutes=5)]
    if len(recent) > 3:
        alerts.append({"rule": "TRANSACTIONS_RAPIDES", "severity": "MEDIUM"})

    # Si alertes, envoyer
    if alerts:
        # Transaction suspecte
        producer.send('suspectes', value=tx)
        print(f"Transaction suspecte: {tx['transaction_id']}")

        # Calculer la durée depuis la dernière transaction
        last_transaction_time = None
        if len(client_timestamps[client]) > 1:
            # Trier les timestamps et prendre l'avant-dernier
            sorted_times = sorted(client_timestamps[client])
            if len(sorted_times) >= 2:
                last_transaction_time = sorted_times[-2]

        time_since_last = None
        if last_transaction_time:
            time_diff = ts - last_transaction_time
            time_since_last = f"{int(time_diff.total_seconds() // 60)}min {int(time_diff.total_seconds() % 60)}s"

        # Alertes enrichies avec détails
        for alert in alerts:
            alert_msg = {
                "transaction_id": tx["transaction_id"],
                "client_id": client,
                "rule": alert["rule"],
                "severity": alert["severity"],
                "timestamp": datetime.now().isoformat(),
                # Détails enrichis
                "amount": tx["montant"],
                "currency": tx["devise"],
                "merchant": tx["marchand"],
                "merchant_country": tx["pays_marchand"],
                "channel": tx["canal"],
                "type": tx["type"],
                "ip_address": tx["ip_address"],
                "time_since_last_transaction": time_since_last,
                "risk_score": calculate_risk_score(tx, alert["rule"]),
                "reason": get_alert_reason(alert["rule"], tx)
            }
            producer.send('alertes', value=alert_msg)
            print(f"Alerte générée: {alert_msg}")

            # Simulation d'un délai de traitement (2 secondes)
            time.sleep(2)

def calculate_risk_score(tx, rule):
    """Calcule un score de risque simple basé sur la règle et les données"""
    base_score = 0

    if rule == "MONTANT_ELEVE":
        amount = tx["montant"]
        if amount > 10000:
            base_score = 95
        elif amount > 5000:
            base_score = 85
    elif rule == "PAYS_RISQUE":
        base_score = 70
    elif rule == "TRANSACTIONS_RAPIDES":
        base_score = 80
    elif rule == "HEURE_INHABITUELLE":
        base_score = 40
    elif rule == "NOUVEAU_MARCHAND":
        base_score = 30

    return min(100, base_score)

def get_alert_reason(rule, tx):
    """Génère une raison détaillée pour l'alerte"""
    if rule == "MONTANT_ELEVE":
        return f"Montant élevé: {tx['montant']} {tx['devise']} (> 5000€)"
    elif rule == "PAYS_RISQUE":
        return f"Pays à risque: {tx['pays_marchand']}"
    elif rule == "TRANSACTIONS_RAPIDES":
        return "Plus de 3 transactions en 5 minutes"
    elif rule == "HEURE_INHABITUELLE":
        return f"Heure inhabituelle: {datetime.fromisoformat(tx['timestamp'][:-1]).hour}h"
    elif rule == "NOUVEAU_MARCHAND":
        return f"Nouveau marchand: {tx['marchand']}"
    return "Raison inconnue"

# Consommation
print("Démarrage du détecteur de fraude...")
message_count = 0
for message in consumer:
    tx = message.value
    process_transaction(tx)
    message_count += 1
    if message_count >= 50:  # Stop après 50 pour le test
        break

producer.flush()
producer.close()
consumer.close()

print("Détection terminée.")
