# Configuration du système de recommandations

# Kafka
KAFKA_SERVERS = ['localhost:9092']
TOPIC_EVENEMENTS = 'evenements_utilisateur'
TOPIC_RECOMMANDATIONS = 'recommandations'
TOPIC_METRIQUES = 'metriques'

# Seuils pour recommandations
SEUIL_SIMILARITE_CATEGORIE = 0.5
NOMBRE_RECOMMANDATIONS_MAX = 5

# A/B Testing
GROUPES_AB = ['categorie', 'recommandation']  # Algorithmes disponibles

# Dashboard
PORT_DASHBOARD = 5000

# Simulation
DELAI_SIMULATION_EVENEMENTS = 2  # secondes entre événements
