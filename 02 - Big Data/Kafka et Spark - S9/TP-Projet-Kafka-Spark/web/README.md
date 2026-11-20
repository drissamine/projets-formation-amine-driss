# Web Dashboard

## Description
Dashboard web interactif pour le monitoring et la visualisation en temps réel des résultats d'analyse du pipeline Kafka-Spark Streaming.

## Fonctionnalités

### Visualisation en Temps Réel
- **Métriques Pipeline**: Throughput, latence, événements totaux
- **Graphiques Dynamiques**: Évolution de la popularité, engagement utilisateur, analyse par genre
- **Timeline d'Anomalies**: Suivi des événements anormaux détectés
- **Tableau d'Anomalies**: Détails des anomalies récentes

### Technologies Utilisées
- **Flask**: Framework web léger
- **Plotly**: Visualisation interactive de données
- **SQLite**: Accès aux données historiques
- **JavaScript**: Interface utilisateur dynamique
- **CORS**: Communication API sécurisée

## Installation

### Dépendances Python
```bash
cd TP-Projet-Kafka-Spark/web
pip install -r requirements.txt
```

### Dépendances Système
- **Flask**: Framework web
- **Plotly**: Bibliothèque de visualisation
- **SQLite3**: Accès base de données (inclus dans Python)

## Démarrage

### 1. Démarrer le Pipeline
Assurez-vous que le pipeline Kafka-Spark est en cours d'exécution:
```bash
# Démarrer Kafka et Spark
./scripts/deploy.sh start

# Démarrer le producteur
python producer/kafka_producer.py --continuous --delay 0.1
```

### 2. Démarrer le Dashboard
```bash
cd TP-Projet-Kafka-Spark/web
python dashboard.py
```

### 3. Accéder au Dashboard
Ouvrir un navigateur et accéder à: http://localhost:5000

## Interface Utilisateur

### Page d'Accueil
- **Status System**: Indicateur de santé du système
- **Métriques Clés**: Total événements, throughput, latence moyenne, anomalies
- **Bouton Refresh**: Mise à jour manuelle des données

### Grille de Statistiques
- **Total Events**: Nombre total d'événements traités
- **Throughput**: Taux de traitement en événements/seconde
- **Avg Latency**: Latence moyenne de traitement
- **Recent Anomalies**: Compteur d'anomalies détectées

### Graphiques Interactifs

#### 1. Popularité des Vidéos
- **Type**: Line Chart avec points
- **Axes**: Temps (X) vs Nombre de lectures (Y)
- **Fonctionnalités**: Zoom, pan, hover détaillé
- **Données**: Évolution temporelle par vidéo

#### 2. Analyse par Genre
- **Type**: Bar Chart
- **Axes**: Genre (X) vs Nombre moyen de lectures (Y)
- **Fonctionnalités**: Comparaison entre genres
- **Données**: Statistiques agrégées par catégorie

#### 3. Engagement Utilisateur
- **Type**: Scatter Plot
- **Axes**: Durée de session (X) vs Temps de visionnage total (Y)
- **Fonctionnalités**: Nuage de points colorés
- **Données**: Relation entre différents indicateurs d'engagement

#### 4. Timeline d'Anomalies
- **Type**: Line Chart temporel
- **Axes**: Temps (X) vs Nombre d'anomalies (Y)
- **Fonctionnalités**: Suivi temporel des incidents
- **Données**: Fréquence des anomalies détectées

### Tableau d'Anomalies
- **Colonnes**: Temps, Type, User ID, Video ID, Détails
- **Tri**: Derniers événements en premier
- **Badge Colorés**: Types d'anomalies (danger, warning, info)
- **Pagination**: Affichage des 10 dernières anomalies

## API Endpoints

### Statistiques Pipeline
```http
GET /api/stats
```
Retourne: Métriques de performance (throughput, latence, système)

### Données Brutes
```http
GET /api/video-popularity
GET /api/user-engagement
GET /api/genre-analysis
GET /api/anomalies
```
Retourne: Données brutes au format JSON

### Graphiques
```http
GET /api/charts/video-popularity
GET /api/charts/genre-analysis
GET /api/charts/user-engagement
GET /api/charts/anomalies-timeline
```
Retourne: Données formatées pour Plotly

### Système
```http
GET /api/system-metrics
GET /api/health
```
Retourne: Statut système et disponibilité

## Configuration

### Variables d'Environnement
```bash
export FLASK_ENV=production
export DATABASE_PATH=./results/streaming_results.db
export REFRESH_INTERVAL=30
```

### Configuration Flask
```python
app.config['DEBUG'] = False
app.config['CORS_HEADERS'] = 'Content-Type'
```

### Configuration Plotly
```python
# Responsive charts
{responsive: true}

# Chart themes
layout = go.Layout(
    template='plotly_white',
    font=dict(family='Arial')
)
```

## Personnalisation

### Thèmes Visuels
Modifier les variables CSS dans `templates/dashboard.html`:
```css
:root {
    --primary-color: #2c3e50;
    --secondary-color: #3498db;
    --success-color: #27ae60;
    --warning-color: #f39c12;
    --danger-color: #e74c3c;
}
```

### Intervalles de Rafraîchissement
Modifier dans `dashboard.py`:
```python
REFRESH_INTERVAL = 30  # seconds
```

### Types de Graphiques
Ajouter de nouveaux graphiques dans les endpoints API:
```python
@app.route('/api/charts/nouveau-graphique')
def api_nouveau_graphique():
    # Logique de création du graphique
    pass
```

## Déploiement

### En Production
```bash
# Utiliser un serveur WSGI
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 dashboard:app
```

### Avec Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "dashboard.py"]
```

### Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name dashboard.example.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoring et Logs

### Logs d'Application
```bash
# Logs Flask
tail -f /var/log/flask.log

# Logs d'accès
tail -f /var/log/nginx/access.log
```

### Monitoring Performance
- **Temps de réponse**: < 100ms pour les endpoints API
- **Utilisation mémoire**: < 200MB pour l'application
- **Connexions simultanées**: Supporte 100+ utilisateurs

### Alertes
- **Système Hors Ligne**: Notification si pipeline indisponible
- **Base de Données**: Alertes si SQLite inaccessible
- **Performance**: Alertes si temps de réponse > 1s

## Sécurité

### CORS
```python
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

### Validation des Données
- **Input Sanitization**: Nettoyage des entrées utilisateur
- **SQL Injection**: Utilisation de requêtes paramétrées
- **XSS Protection**: Échappement HTML dans les templates

### Authentification (Optionnel)
```python
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    # Logique d'authentification
    pass
```

## Dépannage

### Problèmes Courants

#### Dashboard ne se charge pas
```bash
# Vérifier que le serveur Flask est démarré
ps aux | grep dashboard.py

# Vérifier les logs
tail -f /var/log/flask.log
```

#### Graphiques ne s'affichent pas
```bash
# Vérifier la connexion à la base de données
sqlite3 ./results/streaming_results.db ".tables"

# Vérifier les endpoints API
curl http://localhost:5000/api/stats
```

#### Données non mises à jour
```bash
# Vérifier le collecteur de données
ps aux | grep data_collector

# Vérifier l'intervalle de refresh
grep REFRESH_INTERVAL dashboard.py
```

### Logs et Debugging
```python
# Activer le debug mode
app.run(debug=True)

# Logs détaillés
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Intégration avec d'autres Outils

### Grafana
Exporter les métriques vers Grafana via Prometheus:
```python
from prometheus_client import Counter, Histogram
```

### ELK Stack
Envoyer les logs vers Elasticsearch:
```python
import logging
from logstash_formatter import LogstashFormatter
```

### Alerting
Intégration avec Slack/Email:
```python
import requests
def send_alert(message):
    requests.post(SLACK_WEBHOOK_URL, json={'text': message})
```

## Performance

### Optimisation des Requêtes
- **Index SQLite**: Création d'indexes sur les colonnes fréquemment consultées
- **Pagination**: Limitation des résultats pour les grandes tables
- **Cache**: Mise en cache des données fréquemment accédées

### Optimisation Frontend
- **Lazy Loading**: Chargement des graphiques à la demande
- **Debouncing**: Limitation des appels API lors du refresh
- **Compression**: Compression GZIP des réponses

### Scaling
- **Load Balancing**: Plusieurs instances Flask derrière un load balancer
- **Database Pooling**: Pool de connexions SQLite
- **CDN**: Hébergement des assets statiques sur CDN