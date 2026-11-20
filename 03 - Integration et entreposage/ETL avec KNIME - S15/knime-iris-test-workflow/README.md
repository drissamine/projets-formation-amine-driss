# Projet de Test KNIME - Dataset Iris

## Description
Ce projet est conçu pour tester votre installation KNIME et vous familiariser avec les bases de l'analyse de données visuelle. Il utilise le célèbre dataset Iris, souvent appelé le "Hello World" de l'apprentissage machine.

## Dataset Iris
Le dataset contient 150 échantillons de fleurs d'iris avec 4 caractéristiques mesurables :
- **sepal_length** : Longueur du sépale (en cm)
- **sepal_width** : Largeur du sépale (en cm)  
- **petal_length** : Longueur de la pétale (en cm)
- **petal_width** : Largeur de la pétale (en cm)
- **species** : Espèce d'iris (setosa, versicolor, virginica)

## Structure du Projet
```
knime-iris-test-workflow/
├── iris-dataset.csv          # Données d'entraînement
├── README.md                 # Ce fichier
└── workflow-guide.md         # Guide pas-à-pas pour créer le workflow
```

## Objectifs du Workflow
1. **Import des données** - Charger le dataset Iris
2. **Exploration des données** - Comprendre la structure et la qualité des données
3. **Visualisation** - Créer des graphiques pour explorer les relations
4. **Analyse statistique** - Calculer des statistiques descriptives
5. **Machine Learning** - Créer un modèle de classification simple

## Étapes pour Créer le Workflow KNIME

### 1. Création du Workflow
1. Ouvrez KNIME Analytics Platform
2. Créez un nouveau workflow : `File > New > KNIME Workflow`
3. Nommez-le "Iris Test Workflow"

### 2. Import des Données
Ajoutez ces nœuds dans votre workflow :

#### Nœud File Reader
- **Type** : File Reader
- **Configuration** :
  - File/URL: Sélectionnez `iris-dataset.csv`
  - Format: CSV
  - Header: Cochez "First line contains column names"

#### Nœud Column Filter (Optionnel)
- **Type** : Column Filter
- **Configuration** :
  - Include: Toutes les colonnes
  - Purpose: Garder seulement les colonnes nécessaires

### 3. Exploration des Données

#### Nœud Table View
- **Type** : Table View
- **Objectif** : Visualiser les données brutes
- **Connexion** : Sortie de File Reader → Entrée de Table View

#### Nœud Statistics
- **Type** : Statistics
- **Objectif** : Obtenir des statistiques descriptives
- **Connexion** : Sortie de File Reader → Entrée de Statistics

#### Nœud Missing Value
- **Type** : Missing Value
- **Objectif** : Vérifier les valeurs manquantes
- **Connexion** : Sortie de File Reader → Entrée de Missing Value

### 4. Visualisation des Données

#### Nœud Scatter Plot
- **Type** : Scatter Plot
- **Configuration** :
  - X-Axis: sepal_length
  - Y-Axis: petal_length
  - Color: species
- **Objectif** : Visualiser les relations entre caractéristiques

#### Nœud Histogram
- **Type** : Histogram
- **Configuration** :
  - Column: petal_width
  - Number of bins: 10
- **Objectif** : Distribution de la largeur des pétales

#### Nœud Box Plot
- **Type** : Box Plot
- **Configuration** :
  - Column: sepal_width
  - Group by: species
- **Objectif** : Comparer les distributions par espèce

### 5. Analyse Statistique

#### Nœud Correlation Filter
- **Type** : Correlation Filter
- **Configuration** :
  - Columns: Toutes les colonnes numériques
  - Threshold: 0.5
- **Objectif** : Identifier les corrélations fortes

#### Nœud GroupBy
- **Type** : GroupBy
- **Configuration** :
  - Group by: species
  - Aggregation: Mean pour chaque colonne numérique
- **Objectif** : Statistiques par espèce

### 6. Machine Learning

#### Nœud Partitioning
- **Type** : Partitioning
- **Configuration** :
  - Sampling type: Random
  - Training set: 70%
  - Test set: 30%
- **Objectif** : Diviser les données en entraînement/test

#### Nœud Decision Tree Learner
- **Type** : Decision Tree Learner
- **Configuration** :
  - Target column: species
  - Feature columns: Toutes les colonnes numériques
- **Objectif** : Entraîner un arbre de décision

#### Nœud Decision Tree Predictor
- **Type** : Decision Tree Predictor
- **Configuration** :
  - Model: Sortie de Decision Tree Learner
  - Data: Données de test
- **Objectif** : Prédire les espèces sur les données de test

#### Nœud Scorer
- **Type** : Scorer
- **Configuration** :
  - True column: species
  - Predicted column: species (prediction)
- **Objectif** : Évaluer les performances du modèle

#### Nœud Confusion Matrix
- **Type** : Confusion Matrix
- **Configuration** :
  - True column: species
  - Predicted column: species (prediction)
- **Objectif** : Visualiser les erreurs de classification

## Exécution du Workflow
1. **Sélectionnez tous les nœuds** : Ctrl+A (ou Cmd+A sur Mac)
2. **Exécutez le workflow** : Clic droit > Execute or touche F9
3. **Vérifiez les résultats** :
   - Les nœuds doivent passer au vert (succès)
   - Aucun message d'erreur ne doit apparaître
   - Les visualisations doivent s'afficher correctement

## Résultats Attendus
- **Accuracy** : > 90% (le dataset Iris est relativement facile à classifier)
- **Visualisations** : Graphiques clairs montrant les clusters d'espèces
- **Statistiques** : Moyennes et écarts-types par espèce
- **Workflow complet** : Tous les nœuds exécutés avec succès

## Dépannage
Si vous rencontrez des erreurs :
1. **Vérifiez le chemin du fichier** : Le fichier CSV doit être accessible
2. **Vérifiez les types de données** : Toutes les colonnes sauf "species" doivent être numériques
3. **Redémarrez KNIME** : Parfois une simple relance résout les problèmes
4. **Consultez la console** : Les messages d'erreur détaillés apparaissent dans la console

## Prochaines Étapes
Une fois ce workflow fonctionnel :
1. Essayez d'autres algorithmes (Random Forest, SVM)
2. Ajoutez des visualisations plus complexes
3. Explorez d'autres datasets
4. Créez des workflows plus avancés

## Support
Pour toute question sur KNIME :
- Documentation officielle : https://www.knime.com/documentation
- Forums communautaires : https://forum.knime.com/
- Tutoriels vidéo : https://www.knime.com/videos