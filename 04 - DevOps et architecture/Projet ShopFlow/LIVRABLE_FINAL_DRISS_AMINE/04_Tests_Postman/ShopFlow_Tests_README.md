# ShopFlow Phase 4 - Assurance Qualité & Tests

Ce dossier contient les outils nécessaires pour valider l'intégrité du système de manière automatisée.

## 📁 Contenu
- `ShopFlow_Master_Test_Suite.json` : La collection de tests complète.
- `Monolith.postman_environment.json` : Variables pour le mode monolithe.
- `Microservices.postman_environment.json` : Variables pour le mode microservices.

## 🛠️ Comment exécuter les tests ?

1. Importez la collection et les environnements dans Postman.
2. Sélectionnez l'environnement correspondant à votre déploiement actuel.
3. Ouvrez le **Runner** de Postman.
4. Cliquez sur **Run ShopFlow Master Test Suite**.

## ✅ Scénarios Validés
- **E2E Success** : Création de compte, login, extraction du token et injection automatique dans les en-têtes.
- **Sécurité** : Vérification que les routes privées retournent bien un `401 Unauthorized` sans token.
- **Robustesse** : Gestion des ID inexistants (`404`) et des données invalides (`400/422`).

## 📊 Résumé des tests types
- `Status code is 200/201` : Vérifie la réussite de l'opération.
- `Response time is less than 200ms` : Vérifie la performance du Gateway.
- `JSON Schema Validation` : Garantit que le format de sortie est conforme au contrat d'interface.
