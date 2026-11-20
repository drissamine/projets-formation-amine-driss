# Rapport de Développement : GESTIONNAIRE DE PORTEFEUILLE BOURSIER

**Créé par DRISS Amine**

## 1. Introduction

Ce document présente les défis techniques rencontrés lors du développement de l'application **GESTIONNAIRE DE PORTEFEUILLE BOURSIER**, ainsi que les solutions apportées pour garantir une application robuste, fonctionnelle et ergonomique.

## 2. Défis Rencontrés et Solutions

### 2.1. Gestion et Simulation des Prix (Prix Négatifs)

**Le Défi :**
Lors de la simulation des fluctuations du marché, l'algorithme initial générait parfois des variations qui poussaient le prix des actions vers des valeurs négatives ou nulles, ce qui est irréaliste pour le marché boursier.

**La Solution :**
Nous avons affiné la logique de mise à jour des prix dans le `PriceService`.

- Implémentation de bornes de fluctuation (ex: ±2%).
- Ajout d'une vérification stricte empêchant le prix de descendre en dessous d'un seuil minimum (0.01 €).
- Utilisation de modèles de volatilité plus réalistes pour simuler les tendances du marché.

### 2.2. Intégration de Visualisations (ApexCharts)

**Le Défi :**
Le tableau de bord devait offrir une visualisation claire et dynamique de l'évolution du portefeuille. L'intégration de graphiques tiers complexes dans l'écosystème Angular peut parfois poser des problèmes de compatibilité et de cycle de vie (rafraîchissement des données).

**La Solution :**

- Adoption de la librairie **NgApexcharts**, un wrapper Angular officiel pour ApexCharts.
- Configuration d'options graphiques réactives (thème sombre/clair, tooltips, axes dynamiques).
- Mise en place de mécanismes pour mettre à jour les séries de données en temps réel sans recharger le composant entier, assurant une expérience utilisateur fluide.

### 2.3. Sécurisation et Logique de Vente

**Le Défi :**
Il était crucial d'empêcher les erreurs lors des transactions de vente (ex: vendre plus d'actions que possédé) et d'informer l'utilisateur sur l'impact financier de sa décision avant confirmation.

**La Solution :**

- Amélioration du composant `SellStockComponent` avec une validation stricte côté client.
- Affichage en temps réel du **Gain/Perte Potentiel** : l'utilisateur voit immédiatement si sa vente engendrera un profit ou une perte par rapport au prix d'achat moyen (PMP).
- Désactivation dynamique du bouton de confirmation si la quantité saisie invalide le solde disponible.

### 2.4. Tests Unitaires et Asynchronisme

**Le Défi :**
Certains services, notamment le `AlertService`, dépendent d'autres services (`AuthService`, `PortfolioService`) et d'opérations asynchrones (Observables). Tester ces composants de manière isolée générait des erreurs dues à des dépendances non résolues ou des états de session manquants.

**La Solution :**

- Création de **Mocks** (doublures) complets pour les services dépendants dans les fichiers de spec.
- Simulation des retours d'Observables (ex: `of(mockUser)`) pour contrôler le flux de données lors des tests.
- Correction de la configuration de l'injecteur de dépendances (TestBed) pour fournir les mocks appropriés.

### 2.5. Gestion de l'Authentification et Session

**Le Défi :**
Maintenir l'état de l'utilisateur connecté lors du rechargement de la page et protéger les routes sensibles (`/portfolio`).

**La Solution :**

- Implémentation d'un `AuthGuard` qui intercepte la navigation vers les routes protégées.
- Utilisation du `localStorage` pour persister les informations de session (token/user) de manière simple mais efficace pour ce prototype.
- Redirection intelligente vers la page de login avec paramètre `returnUrl` pour rediriger l'utilisateur vers sa destination initiale après connexion.

### 2.6. Localisation et Internationalisation (i18n)

**Le Défi :**
L'application devait être intégralement en français ("100% français"), incluant l'interface utilisateur, les messages d'erreur, les formats de date et de monnaie, ainsi que les commentaires dans le code source pour une meilleure maintenabilité par une équipe francophone.

**La Solution :**

- Révision systématique de tous les templates HTML pour traduire les libellés statiques.
- Utilisation de l'API `Intl` (Intl.NumberFormat, Intl.DateTimeFormat) pour garantir des formats conformes aux standards français (ex: `1 234,56 €`, `dd MMM yyyy`).
- Traduction des commentaires et de la documentation technique.
- Implémentation de méthodes utilitaires centralisées ou locales pour la traduction dynamique des énumérations (ex: niveaux de risque).

## 3. Conclusion

Le projet a permis de livrer une application fonctionnelle répondant aux exigences principales : gestion de portefeuille, achat/vente en temps réel, et visualisation de données. L'architecture modulaire mise en place facilite les évolutions futures (ajout de nouvelles features, vraies API backend, etc.).
