# 📊 mon-app-js - Projet DevOps Complet

Application JavaScript conteneurisée développée dans le cadre du TP DevOps - M2 Ingénierie Logiciel et Data.

## 👨‍💻 Auteur

**DRISS Amine**  
M2 | Spécialité : Ingénierie Logiciel et Data  
📅 Janvier 2026

## 🎯 Objectifs du Projet

Ce projet démontre la maîtrise complète de la chaîne DevOps :

- ✅ Développement d'une application JavaScript avec Express.js
- ✅ Tests unitaires avec Jest
- ✅ Conteneurisation avec Docker
- ✅ Orchestration avec Docker Compose (Dev) et Kubernetes (Prod)
- ✅ Analyse de sécurité avec Trivy
- ✅ Versionnage avec Git/GitHub

## 🚀 Technologies Utilisées

| Technologie    | Version | Rôle                    |
| -------------- | ------- | ----------------------- |
| Node.js        | 24.12.0 | Runtime JavaScript      |
| npm            | 11.6.2  | Gestionnaire de paquets |
| Express.js     | ^4.18.0 | Framework web           |
| Jest           | ^29.0.0 | Tests unitaires         |
| Docker         | 29.1.3  | Conteneurisation        |
| Docker Compose | v2.32.4 | Orchestration (Local)   |
| Kubernetes     | v1.32   | Orchestration (Prod)    |
| Trivy          | 0.68.2  | Analyse de sécurité     |
| Git            | 2.52.0  | Contrôle de version     |

## 📁 Structure du Projet

```
mon-app-js/
├── src/
│   ├── app.js              # Logique métier (calculatrice)
│   ├── index.html          # Interface utilisateur
│   ├── styles.css          # Styles CSS
│   └── utils.js            # Fonctions utilitaires
├── tests/
│   └── app.test.js         # Tests unitaires Jest
├── k8s/                    # Manifests Kubernetes (Partie 6)
│   ├── configmap.yaml
│   ├── deployment.yaml
│   ├── namespace.yaml
│   ├── pod.yaml
│   ├── redis.yaml
│   ├── secret.yaml
│   └── service.yaml
├── Dockerfile              # Configuration Docker
├── docker-compose.yml      # Orchestration
├── package.json            # Dépendances npm
├── server.js               # Serveur Express
├── .dockerignore           # Fichiers exclus du build
├── .gitignore              # Fichiers exclus de Git
└── README.md               # Ce fichier
```

## 🔧 Installation et Démarrage

### Prérequis

- Node.js 18+ et npm
- Docker et Docker Compose
- Git

### Installation locale

```bash
# Cloner le dépôt
git clone https://github.com/drissamine/mon-app-js.git
cd mon-app-js

# Installer les dépendances
npm install

# Lancer les tests
npm test

# Démarrer le serveur
npm start
```

L'application sera accessible sur `http://localhost:3000`

### Démarrage avec Docker

```bash
# Construire l'image Docker
docker build -t mon-app-js:latest .

# Lancer le conteneur
docker run -d -p 3000:3000 --name mon-app mon-app-js:latest

# Vérifier les logs
docker logs mon-app
```

### Démarrage avec Docker Compose

````bash
# Démarrer tous les services
docker-compose up -d

# Vérifier l'état des services
docker-compose ps

# Voir les logs
docker-compose logs -f

# Arrêter les services
docker-compose down
### Démarrage avec Kubernetes (Production)

```bash
# Appliquer la configuration
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/

# Vérifier le déploiement
kubectl get all -n tp-devops-calculatrice

# Accéder à l'application (Port Forwarding si Local)
kubectl port-forward svc/mon-app-service 3000:80 -n tp-devops-calculatrice
````

## 🧪 Tests

```bash
# Lancer tous les tests
npm test

# Tests avec couverture
npm test -- --coverage
```

**Résultats :** ✅ 2/2 tests passés (100%)

## 🔒 Sécurité

### Analyse avec Trivy

```bash
# Scanner l'image Docker
trivy image mon-app-js:latest

# Scanner avec rapport détaillé
trivy image --format table --severity HIGH,CRITICAL mon-app-js:latest
```

**Résultats :** ✅ 0 vulnérabilités critiques ou élevées

### Mesures de sécurité appliquées

- ✅ Image Alpine légère (202MB)
- ✅ Mise à jour des paquets système
- ✅ Dépendances npm sécurisées avec `overrides`
- ✅ Suppression de npm du conteneur final
- ✅ Scan régulier avec Trivy

## 📊 Rapports

Trois rapports HTML détaillés sont disponibles :

1. **rapport.html** - Analyse de sécurité initiale (15 vulnérabilités)
2. **rapport2.html** - Analyse après corrections (0 vulnérabilité)
3. **rapport-devops-complet.html** - Rapport complet du projet

Ouvrez-les dans votre navigateur pour voir les détails.

## 🐳 Docker

### Dockerfile optimisé

- Image de base : `node:18-alpine`
- Mise à jour des paquets système
- Installation des dépendances de production uniquement
- Suppression de npm après installation
- Utilisateur non-root (bonne pratique)

### Taille de l'image

- **Avant optimisation :** ~900MB
- **Après optimisation :** 202MB
- **Réduction :** 78%

## 📝 Commandes Utiles

### Développement

```bash
npm install          # Installer les dépendances
npm test            # Lancer les tests
npm start           # Démarrer le serveur
```

### Docker

```bash
# Images
docker build -t mon-app-js .              # Construire l'image
docker images                              # Lister les images
docker rmi mon-app-js                      # Supprimer l'image

# Conteneurs
docker run -p 3000:3000 mon-app-js        # Lancer un conteneur
docker ps                                  # Lister les conteneurs actifs
docker ps -a                               # Lister tous les conteneurs
docker stop mon-app                        # Arrêter un conteneur
docker rm mon-app                          # Supprimer un conteneur
docker logs mon-app                        # Voir les logs
```

### Docker Compose

```bash
docker-compose up -d          # Démarrer en arrière-plan
docker-compose up --build     # Reconstruire et démarrer
docker-compose ps             # Lister les services
docker-compose logs -f        # Suivre les logs
docker-compose down           # Arrêter et supprimer
docker-compose down -v        # Arrêter et supprimer les volumes
```

### Sécurité

```bash
# Scan de l'image
trivy image mon-app-js:latest

# Scan avec filtre de sévérité
trivy image --severity HIGH,CRITICAL mon-app-js:latest

# Générer un rapport HTML
trivy image --format template --template "@contrib/html.tpl" -o rapport.html mon-app-js:latest
```

### Git

```bash
git status                    # Voir l'état des fichiers
git add .                     # Ajouter tous les fichiers
git commit -m "message"       # Créer un commit
git push origin main          # Pousser vers GitHub
git pull origin main          # Récupérer les modifications
git log --oneline --graph     # Voir l'historique
```

## 🎓 Compétences Démontrées

### Développement

- ✅ JavaScript moderne (ES6+)
- ✅ Framework Express.js
- ✅ Tests unitaires avec Jest
- ✅ Gestion des dépendances npm

### DevOps

- ✅ Conteneurisation Docker
- ✅ Orchestration Docker Compose
- ✅ Orchestration Kubernetes (Pods, Services, Deployments)
- ✅ Optimisation d'images
- ✅ Bonnes pratiques de sécurité

### Sécurité

- ✅ Analyse de vulnérabilités
- ✅ Application de correctifs
- ✅ Réduction de la surface d'attaque
- ✅ Images légères et sécurisées

### Versionnage

- ✅ Git et GitHub
- ✅ Commits descriptifs
- ✅ Gestion de l'historique
- ✅ Collaboration

## 📈 Résultats

| Métrique                 | Valeur     |
| ------------------------ | ---------- |
| Taille de l'image        | 202MB      |
| Tests réussis            | 100% (2/2) |
| Vulnérabilités critiques | 0          |
| Vulnérabilités élevées   | 0          |
| Couverture de code       | 100%       |
| Temps de build           | ~45s       |

## 🔄 Workflow DevOps

```
1. Développement
   ├── Écriture du code
   ├── Tests unitaires
   └── Validation locale

2. Conteneurisation
   ├── Création du Dockerfile
   ├── Build de l'image
   └── Test du conteneur

3. Sécurité
   ├── Scan Trivy
   ├── Correction des vulnérabilités
   └── Re-scan

4. Versionnage
   ├── Commit Git
   ├── Push GitHub
   └── Documentation

5. Déploiement
   ├── Docker Compose (Dev)
   └── Kubernetes (Prod)
```

## 🚧 Améliorations Futures

- [ ] Monitoring avec Prometheus/Grafana
- [ ] Tests d'intégration et E2E
- [ ] Documentation API avec Swagger
- [ ] Optimisation des performances
- [ ] Mise en place de logs structurés
- [ ] Health checks avancés

## 📚 Documentation

- [Rapport DevOps Complet](./rapport-devops-complet.html)
- [Rapport de Sécurité Initial](./rapport.html)
- [Rapport de Sécurité Final](./rapport2.html)

## 🤝 Contribution

Ce projet est développé dans un cadre académique. Pour toute question ou suggestion :

- 📧 Email : [votre.email@example.com]
- 🔗 GitHub : [@drissamine](https://github.com/drissamine)

## 📄 Licence

Ce projet est développé dans un cadre éducatif - M2 Ingénierie Logiciel et Data.

---

**Développé avec ❤️ par DRISS Amine | Janvier 2026**
