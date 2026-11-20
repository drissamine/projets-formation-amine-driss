# TP2 APACHE KAFKA - IoT Dashboard

Ce projet implémente un système IoT complet avec Apache Kafka pour la collecte, le traitement et l'affichage de données de capteurs en temps réel.

## 📁 Structure du projet

```
TP2/
├── producer_iot.py          # Producer IoT avec génération de données
├── consumer_iot_stats.py    # Consumer avec calcul de statistiques
├── dashboard_iot.py         # Dashboard temps réel avec interface riche
├── requirements.txt         # Dépendances Python
├── setup.py                 # Script d'installation et de configuration
├── test_imports.py          # Script de test des imports
└── README.md               # Ce fichier
```

## 🚀 Installation et Configuration

### 1. Prérequis
- Docker avec Apache Kafka
- Python 3.7+ (testé avec Python 3.13)

### 2. Installation rapide (recommandée)
```bash
python setup.py
```
Ce script :
- Installe automatiquement les dépendances
- Lance les tests de validation
- Vérifie la connexion au serveur Kafka

### 3. Installation manuelle des dépendances
```bash
pip install -r requirements.txt
```

### 4. Test des imports
```bash
python test_imports.py
```

### 5. Configuration Kafka
```bash
# Créer le topic IoT
docker exec kafka kafka-topics.sh \
  --create \
  --topic iot-sensors \
  --partitions 3 \
  --replication-factor 1 \
  --bootstrap-server localhost:9092

# Vérifier le topic
docker exec kafka kafka-topics.sh \
  --describe \
  --topic iot-sensors \
  --bootstrap-server localhost:9092
```

## 🛠️ Résolution des Problèmes

### Problème d'import "kafka" résolu ✅
**Problème :** `[Pylance] Import "kafka" could not be resolved`

**Solution appliquée :**
- Mise à jour de `kafka-python` de la version 2.0.2 vers 2.3.0
- Compatibilité avec Python 3.13 assurée
- Validation des imports avec `test_imports.py`

**Vérification :**
```bash
python -c "from kafka import KafkaProducer, KafkaConsumer; print('✅ Import kafka réussi')"
```

## 🎯 Utilisation

### Producer IoT (producer_iot.py)
Génère et envoie des données de capteurs IoT vers Kafka.

```bash
python producer_iot.py
```

**Fonctionnalités :**
- 3 bâtiments (A, B, C) avec 5 capteurs chacun
- Données : température, humidité, niveau de batterie
- Envoi toutes les 2 secondes
- Affichage des envois avec emoji

### Consumer avec Statistiques (consumer_iot_stats.py)
Consomme les messages et calcule des statistiques par bâtiment.

```bash
python consumer_iot_stats.py
```

**Fonctionnalités :**
- Détection d'anomalies (température > 28°C)
- Statistiques par bâtiment : moyenne, min, max
- Fenêtre temporelle de 30 secondes
- Affichage des alertes en temps réel

### Dashboard IoT (dashboard_iot.py)
Interface graphique temps réel avec la bibliothèque Rich.

```bash
python dashboard_iot.py
```

**Fonctionnalités :**
- Interface utilisateur colorée et interactive
- Tableaux de statistiques en temps réel
- Alertes visuelles pour les anomalies
- Mise à jour automatique toutes les secondes

## 📊 Exemple de Sortie

### Consumer IoT Stats
```
📊 Consumer IoT démarré
Calcul des statistiques par bâtiment...
🚨 ALERTE: sensor_B_3: 32.5°C (supérieur à 28°C)

==================================================
📈 STATISTIQUES 14:30:00
==================================================
🏢 Bâtiment A: Moyenne=22.3°C, Min=18.5°C, Max=26.1°C (15 échantillons)
🏢 Bâtiment B: Moyenne=23.8°C, Min=19.2°C, Max=32.5°C (15 échantillons)
🏢 Bâtiment C: Moyenne=21.9°C, Min=18.1°C, Max=25.3°C (15 échantillons)
```

### Dashboard IoT
Interface Rich avec :
- Tableau de statistiques coloré
- Panneau d'alertes avec notifications
- Informations système en temps réel
- Codes couleur : Vert (normal), Jaune (attention), Rouge (alerte)

## 🔧 Configuration Avancée

### Personnalisation des Paramètres
Vous pouvez modifier les paramètres dans chaque fichier :

**Producer :**
- `buildings` : Liste des bâtiments
- `sensors_per_building` : Nombre de capteurs par bâtiment
- `time.sleep(2)` : Intervalle d'envoi

**Consumer :**
- `window_duration` : Durée de la fenêtre statistique
- Seuil d'anomalie dans `check_anomaly()`

**Dashboard :**
- `refresh_per_second` : Fréquence de rafraîchissement
- Seuils d'alerte dans `create_dashboard()`

## 🛠 Dépannage

### Erreurs de connexion Kafka
1. Vérifier que Kafka est démarré : `docker ps`
2. Tester la connexion : `docker exec kafka kafka-topics.sh --list --bootstrap-server localhost:9092`

### Erreurs d'import
1. Vérifier l'installation : `pip install -r requirements.txt`
2. Version Python compatible (3.7+)

### Performance
- Réduire le nombre de capteurs si trop de messages
- Augmenter l'intervalle d'envoi dans le producer
- Optimiser la fenêtre temporelle dans le consumer

## 📈 Fonctionnalités Bonus

1. **Dashboard avancé** : Interface Rich avec animations
2. **Système d'alertes** : Détection d'anomalies automatique
3. **Statistiques temps réel** : Calculs sur fenêtre glissante
4. **Interface utilisateur** : Emojis et codes couleur

## 🎓 Concepts Appris

- Apache Kafka : Topics, Producers, Consumers
- Streaming de données temps réel
- Traitement et agrégation de données IoT
- Interface utilisateur en terminal avec Rich
- Architecture pub/sub pour systèmes distribués
