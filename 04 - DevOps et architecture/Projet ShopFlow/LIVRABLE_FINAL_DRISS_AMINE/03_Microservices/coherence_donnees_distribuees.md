# Cohérence des Données dans l'Architecture ShopFlow

Le passage aux microservices introduit le défi de la gestion des données réparties sur plusieurs bases de données isolées.

## 1. Stratégie de Cohérence Choisie

### A. Cohérence Forte (Synchrone)
**Scénario :** Validation de stock lors de la commande.
- **Choix** : Appel HTTP REST direct du `Order Service` vers le `Product Service`.
- **Raison** : On ne peut pas se permettre une cohérence éventuelle ici (risque de vendre deux fois le dernier article).
- **Compromis** : Si le `Product Service` est en panne, le `Order Service` est bloqué.

### B. Cohérence Éventuelle (Asynchrone via Redis)
**Scénario :** Envoi de notifications (Email/SMS).
- **Choix** : Publication d'événements dans Redis.
- **Raison** : Une latence de quelques millisecondes n'impacte pas l'expérience utilisateur. L'envoi du mail ne doit jamais ralentir la transaction financière.
- **Compromis** : Possibilité de décalage mineur entre l'action et la notification.

## 2. Patterns de Transaction (Évolutions)

### Saga Pattern (Choreography)
Pour des flux plus complexes (ex: Annulation de commande si le paiement échoue), nous utilisons une **Saga chorégraphiée** :
1. `OrderCreated` émis par Order Service.
2. `PaymentService` écoute, tente de débiter, émet `PaymentFailed`.
3. `OrderService` écoute `PaymentFailed` et passe la commande en statut `CANCELLED`.

## 3. Compromis CAP
ShopFlow privilégie la **Partition Tolerance** et la **Consistency** pour le stock (CP), et la **Availability** pour les notifications (AP).
