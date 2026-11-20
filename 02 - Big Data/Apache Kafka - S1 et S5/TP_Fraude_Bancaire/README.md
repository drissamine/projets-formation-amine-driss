Créé par DRISS Amine

# Système de Détection de Fraude Bancaire avec Apache Kafka

## Description

Ce projet implémente un système de traitement de flux de données en temps réel pour la détection de fraudes bancaires utilisant Apache Kafka. Le système analyse 10 000 transactions par jour avec une latence de détection inférieure à 2 secondes.

### Fonctionnalités

- **Simulation de transactions** : Génération de flux de transactions bancaires réalistes
- **Détection en temps réel** : Application de règles métier pour identifier les fraudes
- **Classification des alertes** : Alertes classées par sévérité (HIGH, MEDIUM, LOW)
- **Archivage automatique** : Stockage des transactions suspectes pour investigation
- **Monitoring** : Comptage et surveillance des alertes en temps réel

## Architecture

```
Transactions (JSON) → Kafka Topic 'transactions' → Fraud Detector → Alertes (Topic 'alertes') + Suspectes (Topic 'suspectes')
```

### Composants

- **Producer** : `fraud_producer.py` - Génère et envoie des transactions simulées
- **Detector** : `fraud_detector.py` - Consomme, analyse et génère des alertes
- **Topics Kafka** :
  - `transactions` : Flux entrant des transactions
  - `alertes` : Alertes de fraude générées
  - `suspectes` : Transactions suspectes archivées

## Prérequis

- **Apache Kafka 3.7.0** (inclus dans le projet)
- **Python 3.8+**
- **Bibliothèques Python** :
  - `kafka-python` (installé automatiquement)
- **Système d'exploitation** : Windows/Linux/Mac

## Installation

### 1. Clonage du projet

```bash
# Le projet est déjà dans le dossier TP_Fraude_Bancaire
cd TP_Fraude_Bancaire
```

### 2. Installation des dépendances Python

```bash
pip install kafka-python
```

### 3. Démarrage de Kafka

#### Sur Windows :
```cmd
# Démarrer ZooKeeper
start kafka\start_zookeeper.cmd

# Démarrer Kafka
start kafka\start_kafka.cmd
```

#### Sur Linux/Mac :
```bash
# Démarrer ZooKeeper
bin/zookeeper-server-start.sh config/zookeeper.properties &

# Démarrer Kafka
bin/kafka-server-start.sh config/server.properties &
```

### 4. Création des topics

```bash
# Créer les topics nécessaires
kafka\bin\windows\kafka-topics.bat --create --topic transactions --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
kafka\bin\windows\kafka-topics.bat --create --topic alertes --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
kafka\bin\windows\kafka-topics.bat --create --topic suspectes --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

# Vérifier la création
kafka\bin\windows\kafka-topics.bat --list --bootstrap-server localhost:9092
```

## Utilisation

### 1. Génération des transactions

Lancez le producteur pour générer 50 transactions :

```bash
python scripts/fraud_producer.py
```

**Sortie attendue :**
```
Envoyé: TX000001 - 753.37€ - IT
Envoyé: TX000002 - 1660.88€ - US
...
Envoyé: TX000050 - 1132.76€ - US
50 transactions envoyées au topic 'transactions'
```

### 2. Lancement du détecteur de fraude

Lancez le détecteur en temps réel :

```bash
python scripts/fraud_detector.py
```

**Sortie attendue :**
```
Démarrage du détecteur de fraude...
Transaction suspecte: TX000046
Alerte générée: {'transaction_id': 'TX000046', 'client_id': 'CUST123456', 'rule': 'MONTANT_ELEVE', 'severity': 'HIGH', ...}
...
Détection terminée.
```

### 3. Vérification des résultats

Lancez le script de vérification :

```bash
python scripts/verify.py
```

**Sortie attendue :**
```
Vérification des topics :
Transactions: 50
Suspectes: 50
Alertes: 54
```

### 4. Utilisation rapide (Windows)

Pour lancer automatiquement le producteur puis le détecteur en séquence :

```cmd
scripts\Run.cmd
```

Ce script exécute `python fraud_producer.py` suivi de `python fraud_detector.py`.

## Règles de Détection de Fraude

Le système applique 5 règles métier classées par sévérité :

### HIGH (Critique)
- **Montant élevé** : Transaction > 5000€

### MEDIUM (Important)
- **Pays à risque** : Transaction depuis RU, CN, IR, BR, NG, TR
- **Transactions rapides** : Plus de 3 transactions du même client en 5 minutes

### LOW (Information)
- **Heure inhabituelle** : Transaction entre 00h et 06h
- **Nouveau marchand** : Premier achat chez ce marchand pour ce client

## Structure des Données

### Transaction (Topic 'transactions')

```json
{
  "transaction_id": "TX000001",
  "client_id": "CUST001234",
  "montant": 1500.50,
  "devise": "EUR",
  "marchand": "AMAZON_FR",
  "pays_marchand": "FR",
  "timestamp": "2024-01-15T14:30:25Z",
  "type": "CARTE",
  "canal": "MOBILE",
  "ip_address": "192.168.1.100"
}
```

### Alerte (Topic 'alertes')

```json
{
  "transaction_id": "TX000046",
  "client_id": "CUST123456",
  "rule": "MONTANT_ELEVE",
  "severity": "HIGH",
  "timestamp": "2026-01-12T11:42:45Z"
}
```

## Monitoring et Debugging

### Consulter les messages dans les topics

```bash
# Transactions
kafka-console-consumer --topic transactions --bootstrap-server localhost:9092 --from-beginning

# Alertes
kafka-console-consumer --topic alertes --bootstrap-server localhost:9092 --from-beginning

# Transactions suspectes
kafka-console-consumer --topic suspectes --bootstrap-server localhost:9092 --from-beginning
```

### Statistiques des topics

```bash
# Décrire les topics
kafka-topics --describe --topic transactions --bootstrap-server localhost:9092
kafka-topics --describe --topic alertes --bootstrap-server localhost:9092
kafka-topics --describe --topic suspectes --bootstrap-server localhost:9092
```

## Personnalisation

### Modifier les règles de fraude

Éditez `scripts/fraud_detector.py` :

```python
# Pays à risque
pays_risques = ['RU', 'CN', 'IR', 'BR', 'NG', 'TR']

# Seuil montant élevé
if montant > 5000:  # Modifier ce seuil
```

### Changer le nombre de transactions

Modifiez la boucle dans `scripts/fraud_producer.py` :

```python
for i in range(50):  # Changer 50 par le nombre souhaité
```

## Dépannage

### Erreur de connexion Kafka

- Vérifiez que ZooKeeper et Kafka sont démarrés
- Vérifiez les ports (2181 pour ZooKeeper, 9092 pour Kafka)
- Vérifiez les logs dans les fenêtres de commande

### Pas d'alertes générées

- Vérifiez que le producteur a bien envoyé des transactions
- Vérifiez les timestamps (règle des transactions rapides)
- Consultez les logs du détecteur

### Problèmes de performance

- Augmentez les partitions des topics si nécessaire
- Ajustez les paramètres de consumer (batch size, etc.)

## Extension (Bonus)

### Dashboard Web

Pour implémenter un dashboard temps réel :

1. Installer Node.js
2. Créer une application Express avec Socket.io
3. Consommer le topic 'alertes' et diffuser via WebSocket

### Intégration avec base de données

- Utiliser Kafka Connect pour sinker vers PostgreSQL/MySQL
- Stocker historiquement les alertes et transactions suspectes

## Auteurs

Développé dans le cadre du cours Big Data et Systèmes Distribués 2025-2026.

## Licence

Ce projet est fourni à des fins éducatives.
