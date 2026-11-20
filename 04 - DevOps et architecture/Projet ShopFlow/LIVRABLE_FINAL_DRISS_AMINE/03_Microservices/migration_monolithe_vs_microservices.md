# Rapport Comparatif : Monolithe vs Microservices

Ce document analyse la transformation de l'architecture ShopFlow de la Phase 2 vers la Phase 3.

## 1. Tableau Comparatif

| Critère | Monolithe Modulaire (P2) | Microservices (P3) |
| :--- | :--- | :--- |
| **Complexité Code** | Faible (un seul repo) | Élevée (dépendances inter-services) |
| **Scalabilité** | Verticale (limitation hardware) | Horizontale (service par service) |
| **Isolation des pannes** | Nulle (un bug crash tout) | Élevée (chaque service est isolé) |
| **Déploiement** | Tout ou rien | Indépendant (CI/CD par service) |
| **Cohérence Données** | Transactionnelle (Atomique) | Cohérence Éventuelle (BASE) |

## 2. Pourquoi avons-nous migré ?

### Avantages observés
- **Spécialisation** : L'équipe peut travailler sur le `Payment Service` sans connaître le code du `Product Service`.
- **Infrastructure optimisée** : On peut allouer plus de CPU au `Catalog Service` car c'est le plus sollicité.
- **Résilience** : Une saturation du `Notification Service` n'empêche plus un client de payer sa commande.

### Inconvénients et Compromis
- **Latence réseau** : Les appels entre `Order` et `Product` sont plus lents qu'un appel de fonction local.
- **Observabilité** : Nécessite des logs centralisés car une requête traverse maintenant plusieurs terminaux.

## 3. Conclusion
Le monolithe était idéal pour itérer sur le modèle DDD. Les microservices sont indispensables pour la **mise à l'échelle industrielle** de ShopFlow.
