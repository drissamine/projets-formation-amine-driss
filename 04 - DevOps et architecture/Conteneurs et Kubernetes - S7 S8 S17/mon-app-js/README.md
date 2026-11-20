# Projet DevOps - Mon App JS

**Créé par DRISS Amine**

Ce projet est une application JavaScript permettant d'effectuer des calculs simples (addition, soustraction), développée dans le cadre du cours "Conteneurisation des applications avec Docker".

## Structure du projet

- `src/` : Frontend (HTML, CSS, JS).
- `tests/` : Tests unitaires avec Jest.
- `k8s/` : Fichiers de configuration Kubernetes.
- `kube-prometheus/` : Stack de supervision Prometheus & Grafana.
- `Rapport_DevOps.html` : Rapport complet du projet (étapes, commandes, réponses).
- `app-backend.js` : Logique serveur web / API via Express.
- `server.js` : Démarrage du serveur backend (point d'entrée principal).
- `Dockerfile` & `docker-compose.yml` : Conteneurisation.

## Lancement en local

1. Installez les dépendances :
   ```bash
   npm install
   ```
2. Lancez les tests unitaires :
   ```bash
   npm test
   ```
3. Démarrez l'application :
   ```bash
   npm start
   ```
   Le serveur écoute par défaut sur le port 3000 (`http://localhost:3000`).

### Endpoints Utiles

- Backend principal: `/`
- Healthcheck (Live): `/health/live`
- Healthcheck (Ready): `/health/ready`
- Métriques basiques: `/metrics`
- Métriques Prometheus: `/metric`
- Simulation charge CPU: `/heavy?ms=500`

## Déploiement Docker (Docker Compose)

Pour conteneuriser l'application :

```bash
docker compose up -d
```

L'application sera accessible sur `http://localhost:3000`.

## Déploiement Kubernetes

Le dossier `k8s/` contient tous les manifestes pour déployer l'architecture de manière robuste sur un cluster Kubernetes.
L'ordre de déploiement recommandé est le suivant :

**1. Installer la stack de supervision (Prérequis pour ServiceMonitor)** :

```bash
cd kube-prometheus
kubectl apply --server-side -f manifests/setup
kubectl apply -f manifests/
cd ..
```

**2. Déployer l'application et ses composants** :

```bash
kubectl apply -f k8s/01-namespace.yaml
kubectl apply -f k8s/02-configmap-secret.yaml
kubectl apply -f k8s/03-redis-service.yaml
kubectl apply -f k8s/06-redis-statefulset.yaml
kubectl apply -f k8s/04-deployment.yaml
kubectl apply -f k8s/05-hpa.yaml
kubectl apply -f k8s/07-servicemonitor.yaml
```

## Rapport du projet et Réponses

Un fichier **`Rapport_DevOps.html`** complet a été généré. Il inclut :

- Le détail étape par étape de la création du projet.
- Toutes les commandes terminales exécutées lors de la conception.
- Les réponses rigoureuses aux questions théoriques de chaque étape (Trivy, Kubernetes, Prometheus).

_(Une version brute Markdown des réponses existe également sous le nom `Réponses.md`)._
