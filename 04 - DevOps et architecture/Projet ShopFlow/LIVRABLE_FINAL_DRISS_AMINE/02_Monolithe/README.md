# ShopFlow - Monolithe Modulaire (Phase 2)

Ce projet implémente la plateforme ShopFlow comme une application monolithique modulaire en Node.js, en respectant les principes du **Domain-Driven Design (DDD)**.

## 🏗️ Architecture
L'application est structurée par **Bounded Contexts**. Chaque module (`users`, `products`, `orders`, `payments`) possède sa propre architecture en couches :

- **Domain** : Entités métiers, Value Objects et interfaces de repositories.
- **Application** : Use Cases (Services) qui orchestrent la logique métier.
- **Infrastructure** : Implémentations techniques (Prisma ORM, PostgreSQL).
- **Interfaces** : Points d'entrée REST (Express.js).

## 🚀 Installation & Lancement

1. **Installation des dépendances** :
   ```bash
   npm install
   ```

2. **Configuration** :
   Créez un fichier `.env` avec :
   ```env
   DATABASE_URL="postgresql://user:password@localhost:5432/shopflow"
   JWT_SECRET="votre_secret_jwt"
   PORT=3000
   ```

3. **Lancement** :
   ```bash
   npm run dev
   ```

## 🛠️ API Endpoints

### Identity (Users)
- `POST /api/auth/register` : Inscription.
- `POST /api/auth/login` : Connexion (retourne un JWT).

### Catalog (Products)
- `GET /api/products` : Liste des produits.
- `POST /api/products` : Création (Admin requis).

### Ordering (Orders)
- `POST /api/orders` : Passer une commande.
- `GET /api/orders/:id` : Détails de commande.

### Payments
- `POST /api/payments` : Simuler un paiement.

## 📄 Livrables
- Architecture DDD validée.
- Schéma SQL inclus.
- Collection Postman fournie.
