# Créé par DRISS Amine
import json
import random
import uuid
from datetime import datetime, timedelta
from kafka import KafkaProducer

# Configuration du producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Données de base
devises = ['EUR', 'USD', 'GBP']
types_tx = ['CARTE', 'VIREMENT', 'PRELEVEMENT']
canaux = ['WEB', 'MOBILE', 'TERMINAL']
pays_risques = ['RU', 'CN', 'IR', 'BR', 'NG', 'TR']
pays_normaux = ['FR', 'DE', 'IT', 'ES', 'GB', 'US']

marchands = [
    'AMAZON_FR', 'EBAY_DE', 'CARREFOUR_FR', 'DECATHLON_FR', 'IKEA_SE',
    'ZARA_ES', 'H&M_DE', 'FNAC_FR', 'MEDIA_MARKT_DE', 'ALDI_DE'
]

# Génération de transactions
transactions = []

for i in range(50):
    tx_id = f"TX{i+1:06d}"
    # Pour tester rapid, faire 4 tx du même client
    if 45 <= i <= 48:
        client_id = "CUST123456"  # même client pour rapid
    else:
        client_id = f"CUST{random.randint(100000, 999999)}"

    # Déterminer si suspect (5 sur 50)
    is_suspect = i >= 45  # derniers 5 sont suspects

    if is_suspect:
        # Types de suspects
        suspect_type = random.choice(['montant', 'pays', 'heure'])
        if suspect_type == 'montant':
            montant = round(random.uniform(5001, 15000), 2)
            pays = random.choice(pays_normaux)
            heure = random.randint(8, 22)
        elif suspect_type == 'pays':
            montant = round(random.uniform(100, 2000), 2)
            pays = random.choice(pays_risques)
            heure = random.randint(8, 22)
        else:  # heure
            montant = round(random.uniform(100, 2000), 2)
            pays = random.choice(pays_normaux)
            heure = random.randint(0, 5)
    else:
        montant = round(random.uniform(10, 3000), 2)
        pays = random.choice(pays_normaux)
        heure = random.randint(8, 22)

    # Timestamp
    if 45 <= i <= 48:
        # Pour rapid, timestamps proches
        base_time = datetime.now()
        variation = timedelta(minutes=random.randint(0, 4))  # 0-4 min
        timestamp = (base_time + variation).strftime('%Y-%m-%dT%H:%M:%SZ')
    else:
        base_time = datetime.now()
        variation = timedelta(minutes=random.randint(-30, 30))
        timestamp = (base_time + variation).strftime('%Y-%m-%dT%H:%M:%SZ')

    # IP aléatoire
    ip = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"

    transaction = {
        "transaction_id": tx_id,
        "client_id": client_id,
        "montant": montant,
        "devise": random.choice(devises),
        "marchand": random.choice(marchands),
        "pays_marchand": pays,
        "timestamp": timestamp,
        "type": random.choice(types_tx),
        "canal": random.choice(canaux),
        "ip_address": ip
    }

    transactions.append(transaction)

# Envoi au topic transactions
for tx in transactions:
    producer.send('transactions', value=tx)
    print(f"Envoyé: {tx['transaction_id']} - {tx['montant']}€ - {tx['pays_marchand']}")

producer.flush()
producer.close()

print("50 transactions envoyées au topic 'transactions'")
