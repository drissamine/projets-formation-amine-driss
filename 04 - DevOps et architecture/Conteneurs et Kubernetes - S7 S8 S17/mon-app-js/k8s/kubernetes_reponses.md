# Réponses aux Questions de Synthèse (Partie 6 - K8s)

## Différence fondamentale entre un Pod et un Deployment

Un **Pod** est l'unité d'exécution la plus élémentaire dans Kubernetes. Il représente une instance unique d'un processus en cours d'exécution dans le cluster (contenant un ou plusieurs conteneurs). Les Pods sont éphémères : s'ils meurent, ils ne sont pas ressuscités automatiquement.

Un **Deployment** est une abstraction de plus haut niveau qui gère les Pods. Il permet de décrire l'état désiré pour une application (ex: "je veux 3 répliques de mon-app"). Le Deployment s'assure que le nombre défini de Pods est toujours en cours d'exécution. Il gère également le cycle de vie des applications, y compris les mises à jour progressives (Rolling Updates) et les retours en arrière (Rollbacks).

**En résumé** : Le Pod exécute le conteneur, le Deployment gère et orchestre les Pods.

## Progression logique : Pod → Service → Deployment

Cette progression illustre la construction typique d'une application résiliente :

1.  **Pod** : On commence par définir le conteneur à exécuter. C'est la "brique" de base.
2.  **Deployment** : On ne crée généralement pas de Pods directement. On utilise un Deployment pour dire "Gère-moi X copies de ce Pod". Cela apporte la résilience et la scalabilité.
3.  **Service** : Une fois les Pods gérés par le Deployment, ils sont dynamiques (leurs IPs changent). Le Service fournit une interface réseau stable (IP fixe, nom DNS) pour accéder à cet ensemble de Pods, quel que soit leur cycle de vie.

## Quels problèmes Kubernetes résout-il par rapport à Docker seul ?

Docker seul (avec Docker Compose) est excellent pour exécuter des conteneurs sur une seule machine, mais montre ses limites en production à grande échelle. Kubernetes résout :

1.  **Orchestration multi-nœuds** : K8s gère un cluster de plusieurs serveurs comme une seule entité.
2.  **Haute Disponibilité (Self-healing)** : Si un conteneur ou un nœud plante, K8s le redémarre ou le déplace ailleurs automatiquement.
3.  **Scalabilité automatique (Auto-scaling)** : Ajustement dynamique du nombre de répliques selon la charge (CPU/RAM).
4.  **Mises à jour sans interruption (Zero Downtime Deployment)** : Mise à jour de l'application pod par pod.
5.  **Découverte de Service et Équilibrage de charge** : Gestion native du trafic réseau entre les microservices.

## Bonnes pratiques Kubernetes appliquées dans ce projet

Dans les manifestes créés, nous avons appliqué les pratiques suivantes :

1.  **Utilisation de Liveness et Readiness Probes** : Pour que K8s sache si l'application est vivante et prête à recevoir du trafic (fichiers `deployment.yaml`).
2.  **Définition des Ressources (Requests/Limits)** : Pour éviter qu'un pod ne consomme toutes les ressources du nœud et aider le scheduler à bien placer les pods.
3.  **Réplication** : Utilisation de `replicas: 2` pour assurer la disponibilité même si un pod échoue.
4.  **Configuration par Variables d'Env** : Injection de la configuration (`APP_MESSAGE`) via le manifest, respectant les principes "12-factor app".
