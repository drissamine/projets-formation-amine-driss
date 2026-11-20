# 🛍️ Système de Recommandations E-commerce en Temps Réel

Un système complet de recommandations personnalisées pour e-commerce, inspiré d'Amazon, utilisant Apache Kafka pour le traitement en temps réel.

## 🎯 Problème Résolu

Les e-commerçants perdent 35% de ventes potentielles car :
- Les clients ne trouvent pas les produits recherchés
- Les recommandations sont génériques et non personnalisées
- Le système ne s'adapte pas au comportement en temps réel

## 🏗️ Architecture

Le système utilise une architecture en temps réel avec Kafka :

- **service_suivi.py** : Collecte les événements utilisateur (vues, achats, paniers)
- **moteur_recommandations.py** : Traite les événements et génère des recommandations personnalisées
- **test_ab.py** : Compare les performances de différents algorithmes
- **tableau_bord.py** : Dashboard web pour monitorer les métriques

### Algorithmes de Recommandation

1. **Par Catégorie** : Recommande des produits populaires dans la même catégorie
2. **Par Co-occurrence** : Recommande des produits fréquemment achetés ensemble

## 🚀 Démarrage Rapide

### Prérequis

- Python 3.8+
- Java 8+ (pour Kafka)
- Git

### Installation et Lancement

1. **Cloner le projet** (ou utiliser les fichiers créés)

2. **Démarrer le système complet** :
   ```bash
   python demarrer_systeme.py
   ```

   Cette commande :
   - Installe les dépendances Python
   - Démarre ZooKeeper
   - Démarre Kafka
   - Crée les topics nécessaires
   - Lance tous les services en parallèle

3. **Accéder au dashboard** :
   Ouvrez http://localhost:5000 dans votre navigateur

## 📊 Fonctionnalités

### Suivi d'Événements
- **VIEW_PRODUCT** : Consultation d'un produit
- **ADD_TO_CART** : Ajout au panier
- **PURCHASE** : Achat final

### Recommandations Personnalisées
- Adaptées au comportement en temps réel
- Test A/B automatique entre algorithmes
- Mise à jour continue des profils utilisateur

### Métriques en Temps Réel
- Nombre d'utilisateurs actifs
- Taux de conversion par algorithme
- Performance des recommandations

## 🧪 Test A/B

Le système teste automatiquement deux algorithmes :
- **categorie** : Basé sur la popularité par catégorie
- **cooccurrence** : Basé sur les achats associés

Les utilisateurs sont assignés aléatoirement aux groupes pour mesurer l'efficacité.

## 📈 Exemple de Scénario

```
14:30:00 - Alice arrive sur le site
14:30:05 - Regarde un livre Kafka (45 secondes)
14:30:50 - Système recommande livres Big Data
14:31:00 - Alice ajoute un livre au panier
14:31:10 - Système recommande formations en ligne Kafka
14:31:30 - Alice achète
14:31:35 - Système recommande livres Spark pour compléter
```

## 🔧 Configuration

Voir `config.py` pour :
- Paramètres Kafka
- Seuils de recommandation
- Configuration A/B testing

## 📁 Structure du Projet

```
.
├── exigences.txt              # Dépendances Python
├── modeles.py                 # Modèles de données
├── config.py                  # Configuration
├── service_suivi.py          # Collecte d'événements
├── moteur_recommandations.py  # Moteur de calcul
├── test_ab.py                # Framework A/B testing
├── tableau_bord.py           # Dashboard web
├── demarrer_systeme.py       # Script de lancement
└── kafka/                    # Apache Kafka
```

## 🛠️ Technologies Utilisées

- **Python 3.8+**
- **Apache Kafka** : Traitement en temps réel
- **Flask** : Dashboard web
- **kafka-python** : Client Kafka
- **Collections** : Structures de données optimisées

## 🎯 Métriques Clés

- **CTR (Click-Through Rate)** : Taux de clic sur recommandations
- **Conversion Rate** : Taux de transformation visite → achat
- **Personalization Score** : Pertinence des recommandations

## 🔄 Flux de Données

1. **Événements** → Kafka topic `evenements_utilisateur`
2. **Traitement** → Mise à jour profils utilisateur
3. **Recommandations** → Calcul et envoi vers `recommandations`
4. **Métriques** → Collecte pour A/B testing

## 🚀 Déploiement

Pour un environnement de production :
- Utiliser Kubernetes pour l'orchestration
- Base de données persistante (Redis/PostgreSQL)
- Monitoring avec Prometheus/Grafana
- Load balancing pour le dashboard

---

**Ce système démontre comment l'analyse en temps réel du comportement utilisateur peut considérablement améliorer l'expérience d'achat et augmenter les conversions.**
