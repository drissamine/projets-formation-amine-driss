# CineReview - Site de Critique Cinematographique

Une application React moderne pour gérer etcritiquer des films avec un système de notation et de recherche.

## Fonctionnalités

- ✅ **Ajouter des films** : Formulaire avec validation pour ajouter de nouveaux films
- ✅ **Système de notation** : Notation interactive avec étoiles (1-5)
- ✅ **Ajouter des critiques** : Possibilité d'ajouter des commentaires sur chaque film
- ✅ **Recherche et filtrage** : Rechercher des films par titre ou réalisateur
- ✅ **Suppression de films** : Supprimer des films avec confirmation
- ✅ **Persistance des données** : Sauvegarde automatique dans localStorage
- ✅ **Interface responsive** : Design moderne et adaptatif

## Structure du projet

```
movie-review-app/
├── src/
│   ├── components/
│   │   ├── MovieList.jsx      # Liste et grille des films
│   │   ├── MovieCard.jsx      # Carte individuelle de film
│   │   ├── MovieForm.jsx      # Formulaire d'ajout avec validation
│   │   ├── SearchBar.jsx      # Barre de recherche
│   │   └── RatingStars.jsx    # Composant de notation
│   ├── App.jsx                # Composant principal avec logique métier
│   ├── App.css                # Styles CSS complets
│   └── index.js
├── package.json
└── README.md
```

## Installation et démarrage

```bash
# Créer le projet
npm create vite@latest movie-review-app -- --template react

# Naviguer vers le projet
cd movie-review-app

# Installer les dépendances
npm install

# Lancer le serveur de développement
npm run dev
```

## Concepts React utilisés

- **Composants fonctionnels** : Tous les composants sont des fonctions
- **Hooks** : useState pour la gestion d'état, useEffect pour les effets
- **Props** : Communication entre composants parents et enfants
- **Gestion d'état** : État global dans App.jsx avec distribution via props
- **Formulaires contrôlés** : Validation et gestion des erreurs
- **Rendu conditionnel** : Affichage conditionnel selon l'état
- **Listes et keys** : Utilisation de map() et keys React
- **Persistance** : localStorage pour sauvegarder les données

## Fonctionnalités détaillées

### 1. Ajout de films
- Formulaire avec champs : titre, réalisateur, année, description
- Validation en temps réel avec messages d'erreur
- Reset automatique du formulaire après ajout

### 2. Notation des films
- Système d'étoiles interactif (1-5)
- Affichage de la note numérique
- Mise à jour en temps réel

### 3. Critiques
- Ajout de critiques via prompt simple
- Affichage du nombre de critiques
- Liste des critiques avec style distinctif

### 4. Recherche
- Filtrage par titre et réalisateur
- Mise à jour en temps réel
- Compteur de résultats

### 5. Suppression
- Bouton de suppression avec icône
- Confirmation utilisateur avant suppression
- Mise à jour immédiate de l'interface

## Technologies utilisées

- **React 18** : Framework JavaScript pour l'interface utilisateur
- **Vite** : Outil de build rapide et serveur de développement
- **CSS3** : Styles modernes avec gradients, transitions et animations
- **localStorage** : Persistance des données côté client

## Améliorations possibles (Défis)

- **Édition de films** : Modifier les informations après création
- **Tri des films** : Par titre, note, année
- **Genres** : Ajout d'un système de classification
- **Statistiques** : Nombre total, note moyenne, film le mieux noté
- **Export/Import** : Sauvegarde en JSON
- **Images de couverture** : Ajout d'URLs d'affiches
- **Dates de visionnage** : Tracking des dates de visionnage

## Développement

Pour contribuer ou modifier l'application :

1. Modifier les composants dans `src/components/`
2. Ajuster les styles dans `src/App.css`
3. Modifier la logique métier dans `src/App.jsx`
4. Tester les modifications avec `npm run dev`

## Performance

L'application utilise des bonnes pratiques React :
- State management optimisé
- Ré-rendus minimisés
- Effets de bord contrôlés avec useEffect
- Validation côté client pour une meilleure UX

## Compatibilité

- Navigateurs modernes supportant ES6+
- Mobile et desktop (responsive design)
- Compatible avec les outils de développement React
