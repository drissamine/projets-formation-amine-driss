# 📈 GESTIONNAIRE DE PORTEFEUILLE BOURSIER - Application de Gestion de Portefeuille Boursier

Une application Angular moderne pour la gestion de portefeuille d'actions avec calcul de performance, alertes intelligentes et analyse financière avancée.

## 🎯 Fonctionnalités Principales

### 🏦 Gestion de Portefeuille

- **Vue d'ensemble complète** du portefeuille avec métriques en temps réel
- **Calcul automatique** des gains/pertes (réalisés et non-réalisés)
- **Suivi de performance** avec indicateurs avancés (rendement, volatilité, diversification)
- **Analyse de risque** avec classification automatique (LOW, MEDIUM, HIGH, VERY_HIGH)

### 💹 Trading d'Actions

- **Interface d'achat** intuitive avec validation complète
- **Interface de vente** avec vérification des parts possedées
- **Prix en temps réel** via Mock API avec fluctuations réalistes (±2%)
- **Validation des transactions** et gestion du budget

### 🔔 Système d'Alertes

- **4 types d'alertes** : baisse/hausse de prix, objectif de gain, limite de perte
- **Vérification automatique** des seuils définis
- **Notifications navigateur** avec permission utilisateur
- **Interface de gestion** des alertes actives/déclenchées

### 📊 Analytics & Rapports

- **Graphiques d'évolution** interactifs avec ApexCharts
- **Top performers** / Moindres performers
- **Export JSON** de l'historique complet
- **Comparaison SPX500** avec calcul de surperformance et recommandations

### 🔒 Sécurité & Authentification

- **AuthGuard** pour protection des routes
- **Persistance localStorage** par utilisateur
- **Session utilisateur** avec gestion automatique
- **Validation côté client** complète

## 🏗️ Architecture Technique

### 📁 Structure des Modules

```
src/app/
├── shared/                    # Module partagé
│   ├── models/               # Modèles TypeScript
│   │   ├── user.model.ts
│   │   ├── stock.model.ts
│   │   ├── transaction.model.ts
│   │   └── portfolio.model.ts
│   ├── services/             # Services métier
│   │   ├── auth.service.ts
│   │   ├── portfolio.service.ts
│   │   ├── price.service.ts
│   │   ├── alert.service.ts
│   │   └── spx500.service.ts
│   ├── guards/               # Guards de sécurité
│   │   └── auth.guard.ts
│   └── components/           # Composants partagés
│       ├── login/
│       └── navbar/
├── portfolio/                # Module portefeuille
│   ├── components/
│   │   ├── dashboard/        # Dashboard principal
│   │   ├── portfolio-list/   # Liste des actions
│   │   ├── buy-stock/        # Formulaire d'achat
│   │   ├── sell-stock/       # Formulaire de vente
│   │   ├── transaction-history/ # Historique
│   │   └── alert-management/ # Gestion alertes
│   ├── portfolio-module.ts
│   └── portfolio-routing-module.ts
└── app/
    ├── app.component.ts
    ├── app.routes.ts
    └── app.config.ts
```

### 🔧 Services Clés

#### AuthService

- **Gestion d'authentification** avec localStorage
- **Observable reactive** avec currentUser$
- **Méthodes** : login(), register(), logout(), updateBudget()
- **Gestion des sessions** persistantes

#### PortfolioService

- **Gestion d'état centralisée** avec BehaviorSubjects
- **Calculs de performance** automatiques
- **Méthodes principales** : buyStock(), sellStock(), getTransactionSummary()
- **Export de données** en JSON

#### PriceService

- **Mock API** avec 5 actions : AAPL, GOOG, MSFT, AMZN, TESLA
- **Fluctuations réalistes** (±2% par mise à jour)
- **Observable des prix** en temps réel
- **Méthodes** : getStockPrice(), refreshPrices(), getAvailableSymbols()

#### AlertService

- **Système d'alertes complet** avec 4 types
- **Vérification automatique** des seuils
- **Notifications navigateur** natives
- **Persistance localStorage** par utilisateur

#### SPX500Service

- **Simulation de marché** (SPX500) avec historique sur 30 jours
- **Calcul de rendement** sur différentes périodes (1D, 1W, 1M, 1Y)
- **Comparaison de performance** avec le portefeuille utilisateur
- **Recommandations automatiques** basées sur l'écart de performance

### 🎨 Composants UI

#### DashboardComponent

- **Métriques temps réel** : capital investi, valeur actuelle, gains/pertes
- **Graphiques d'évolution** interactifs avec NgApexCharts
- **Comparaison de marché** (vs SPX500) avec indicateurs de surperformance
- **Top/Flop performers** avec gains/pertes
- **Actions rapides** vers buy/sell/history

#### BuyStockComponent

- **Formulaire réactif** avec validation complète
- **Mise à jour prix** automatique par symbole
- **Calcul coût total** dynamique
- **Vérification budget** avant achat

#### SellStockComponent

- **Sélection actions possedées** depuis portefeuille
- **Validation parts disponibles** en temps réel
- **Calcul produit vente** automatique
- **Interface intuitive** avec conseils

#### PortfolioListComponent

- **Tableau complet** des actions possedées
- **Tri/filtrage** par symbole ou métriques
- **Métriques détaillées** : parts, prix moyen, valeur, gains/pertes
- **Interface responsive** avec actions rapides

## 🧪 Tests Unitaires

### 📋 Couverture de Tests

- **AuthService** : 15+ tests couvrant login, register, logout, persistence
- **Tests asynchrones** avec subscribe() et done() callbacks
- **Mock localStorage** avec nettoyage automatique
- **Tests d'intégration** entre services

### 🚀 Exécution des Tests

```bash
# Tests unitaires
npm test

# Tests avec couverture
npm run test:coverage

# Tests en mode watch
npm run test:watch
```

## 📱 Interface Utilisateur

### 🎨 Design System

- **Bootstrap 5** pour la grille et composants
- **Font Awesome** pour les icônes
- **SCSS** pour le styling personnalisé
- **Responsive design** mobile-first

### 🔄 États d'Interface

- **Loading states** avec spinners
- **Error handling** avec messages utilisateur
- **Success notifications** pour actions
- **Form validation** en temps réel

## 📊 Données & Mock API

### 💰 Actions Supportées

| Symbole | Nom             | Prix Initial |
| ------- | --------------- | ------------ |
| AAPL    | Apple Inc.      | €185.50      |
| GOOG    | Alphabet Inc.   | €2,750.00    |
| MSFT    | Microsoft Corp. | €420.00      |
| AMZN    | Amazon.com Inc. | €3,200.00    |
| TESLA   | Tesla Inc.      | €245.80      |

### 📈 Fluctuations de Prix

- **Variation aléatoire** ±2% par mise à jour
- **Mise à jour automatique** toutes les 30 secondes
- **Persistance des prix** pendant la session
- **Simulation réaliste** du marché

## 🔧 Configuration & Installation

### 📋 Prérequis

- Node.js 18+
- Angular CLI 17+
- npm ou yarn

### 🚀 Installation

```bash
# Cloner le projet
git clone [repository-url]
cd stock-portfolio-manager

# Installer les dépendances
npm install

# Démarrer en développement
npm start

# Build pour production
npm run build

# Lancer les tests
npm test
```

### ⚙️ Configuration Environment

```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:3000/api',
  mockApiEnabled: true,
  priceUpdateInterval: 30000, // 30 secondes
  defaultInitialBudget: 10000,
};
```

## 📚 Documentation API

### 🔗 Services & Méthodes

#### PortfolioService

```typescript
// Acheter des actions
buyStock(symbol: string, shares: number, pricePerShare: number): Observable<boolean>

// Vendre des actions
sellStock(symbol: string, shares: number, pricePerShare: number): Observable<boolean>

// Résumé des transactions
getTransactionSummary(): Observable<TransactionSummary>

// Export JSON
exportHistory(): string
```

#### PriceService

```typescript
// Obtenir prix d'une action
getStockPrice(symbol: string): Observable<StockPrice | null>

// Obtenir tous les prix
getAllStockPrices(): Observable<{ [symbol: string]: StockPrice }>

// Actualiser tous les prix
refreshPrices(): Observable<void>

// Symboles disponibles
getAvailableSymbols(): string[]
```

#### AlertService

```typescript
// Créer une alerte
createAlert(symbol: string, type: AlertType, threshold: number): Observable<boolean>

// Supprimer une alerte
deleteAlert(alertId: string): void

// Alertes actives
getActiveAlerts(): Observable<PortfolioAlert[]>

// Alertes déclenchées
getTriggeredAlerts(): Observable<PortfolioAlert[]>
```

## 🚀 Roadmap & Améliorations

### 📈 Phase Suivante (v2.0)

- [ ] **Personnalisation avancée** des graphiques ApexCharts
- [ ] **Tests E2E** avec Cypress
- [ ] **PWA** avec service workers
- [ ] **API réelle** en backend Node.js
- [ ] **Authentification OAuth** (Google, GitHub)

### 🔧 Améliorations Techniques

- [ ] **State management** avec NgRx
- [ ] **Internationalisation** (i18n)
- [ ] **Lazy loading** des modules
- [ ] **Code splitting** automatique
- [ ] **Bundle optimization** avec webpack

### 📊 Fonctionnalités Avancées

- [ ] **Analyse technique** (RSI, MACD, Bollinger)
- [ ] **Backtesting** des stratégies
- [ ] **Simulation de trading** paper
- [ ] **API de données réelles** (Alpha Vantage, IEX)
- [ ] **Alertes email/SMS**

## 🤝 Contribution

### 📝 Guidelines

1. **Fork** le repository
2. **Créer** une branche feature (`git checkout -b feature/amazing-feature`)
3. **Commit** les changements (`git commit -m 'Add amazing feature'`)
4. **Push** vers la branche (`git push origin feature/amazing-feature`)
5. **Ouvrir** une Pull Request

### 🧪 Standards de Code

- **ESLint** + **Prettier** pour le formatting
- **Conventional Commits** pour les messages
- **Tests requis** pour nouvelles fonctionnalités
- **Documentation** mise à jour obligatoire

## 👥 Équipe

Développé dans le cadre du TP de développement Angular.

**Créé par DRISS Amine**

---
