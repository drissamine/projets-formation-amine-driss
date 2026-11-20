# Guide Pas-à-Pas : Création du Workflow KNIME Iris

## Introduction
Ce guide vous accompagne étape par étape dans la création d'un workflow KNIME complet pour analyser le dataset Iris. Suivez chaque étape pour tester votre installation et apprendre les bases de KNIME.

## Étape 1 : Configuration Initiale

### 1.1 Lancer KNIME
1. Ouvrez KNIME Analytics Platform
2. Attendez le chargement complet de l'interface

### 1.2 Créer un Nouveau Workflow
1. Allez dans `File > New > KNIME Workflow`
2. Nommez votre workflow : **"Iris Test Workflow"**
3. Cliquez sur **Finish**

### 1.3 Organiser l'Espace de Travail
1. **Explorer** (à gauche) : Contient vos fichiers et nœuds disponibles
2. **Workflow** (centre) : Zone de création de votre workflow
3. **Views** (droite) : Résultats et visualisations

## Étape 2 : Import des Données

### 2.1 Ajouter le Nœud File Reader
1. Dans l'onglet **Node Repository** (Explorer)
2. Recherchez "File Reader" dans la barre de recherche
3. Faites glisser le nœud **File Reader** vers la zone de workflow
4. Double-cliquez sur le nœud pour le configurer

### 2.2 Configurer File Reader
Dans l'onglet **Configuration** :
- **File/URL**: Cliquez sur "Browse" et sélectionnez `iris-dataset.csv`
- **Format**: Sélectionnez "CSV"
- **Header**: Cochez "First line contains column names"
- **Column Separator**: Virgule (,)
- Cliquez sur **OK**

### 2.3 Tester l'Import
1. Cliquez droit sur le nœud File Reader
2. Sélectionnez **Execute** (ou touche F9)
3. Le nœud doit passer au vert ✅
4. Double-cliquez sur le nœud et allez dans l'onglet **Views** pour voir les données

## Étape 3 : Exploration des Données

### 3.1 Ajouter Table View
1. Recherchez "Table View" dans Node Repository
2. Faites glisser le nœud vers le workflow
3. Connectez la sortie de File Reader à l'entrée de Table View
4. Exécutez le nœud Table View
5. Double-cliquez pour voir les données en tableau

### 3.2 Ajouter Statistics
1. Recherchez "Statistics" dans Node Repository
2. Connectez File Reader → Statistics
3. Exécutez le nœud
4. Visualisez les statistiques : moyenne, écart-type, min, max

### 3.3 Vérifier les Valeurs Manquantes
1. Recherchez "Missing Value" dans Node Repository
2. Connectez File Reader → Missing Value
3. Exécutez et vérifiez qu'aucune valeur manquante n'est détectée

## Étape 4 : Visualisation des Données

### 4.1 Créer un Scatter Plot
1. Recherchez "Scatter Plot" dans Node Repository
2. Connectez File Reader → Scatter Plot
3. Configurez le Scatter Plot :
   - **X-Axis**: Sélectionnez "sepal_length"
   - **Y-Axis**: Sélectionnez "petal_length"
   - **Color**: Sélectionnez "species"
   - **Size**: Optionnel, vous pouvez choisir "petal_width"
4. Exécutez et observez les clusters par espèce

### 4.2 Créer un Histogramme
1. Recherchez "Histogram" dans Node Repository
2. Connectez File Reader → Histogram
3. Configurez l'Histogramme :
   - **Column**: Sélectionnez "petal_width"
   - **Number of bins**: 15
4. Exécutez et observez la distribution

### 4.3 Créer un Box Plot
1. Recherchez "Box Plot" dans Node Repository
2. Connectez File Reader → Box Plot
3. Configurez le Box Plot :
   - **Column**: Sélectionnez "sepal_width"
   - **Group by**: Sélectionnez "species"
4. Exécutez et comparez les distributions par espèce

## Étape 5 : Analyse Statistique

### 5.1 Calculer les Corrélations
1. Recherchez "Correlation Filter" dans Node Repository
2. Connectez File Reader → Correlation Filter
3. Configurez :
   - **Columns**: Sélectionnez toutes les colonnes numériques
   - **Threshold**: 0.5
4. Exécutez et observez la matrice de corrélation

### 5.2 Statistiques par Espèce
1. Recherchez "GroupBy" dans Node Repository
2. Connectez File Reader → GroupBy
3. Configurez :
   - **Group by**: Sélectionnez "species"
   - **Aggregation**: Cliquez sur "Add"
     - Sélectionnez "Mean"
     - Ajoutez toutes les colonnes numériques
4. Exécutez et observez les moyennes par espèce

## Étape 6 : Machine Learning

### 6.1 Diviser les Données
1. Recherchez "Partitioning" dans Node Repository
2. Connectez File Reader → Partitioning
3. Configurez :
   - **Sampling type**: Random
   - **Training set**: 70%
   - **Test set**: 30%
4. Exécutez

### 6.2 Entraîner un Arbre de Décision
1. Recherchez "Decision Tree Learner" dans Node Repository
2. Connectez Partitioning (Train) → Decision Tree Learner
3. Configurez :
   - **Target column**: Sélectionnez "species"
   - **Feature columns**: Sélectionnez toutes les colonnes numériques
4. Exécutez

### 6.3 Faire des Prédictions
1. Recherchez "Decision Tree Predictor" dans Node Repository
2. Connectez :
   - Decision Tree Learner → Decision Tree Predictor (model)
   - Partitioning (Test) → Decision Tree Predictor (data)
3. Exécutez

### 6.4 Évaluer les Performances
1. Recherchez "Scorer" dans Node Repository
2. Connectez Decision Tree Predictor → Scorer
3. Configurez :
   - **True column**: Sélectionnez "species"
   - **Predicted column**: Sélectionnez "species (prediction)"
4. Exécutez et observez l'accuracy

### 6.5 Visualiser la Matrice de Confusion
1. Recherchez "Confusion Matrix" dans Node Repository
2. Connectez Decision Tree Predictor → Confusion Matrix
3. Configurez les mêmes colonnes que pour Scorer
4. Exécutez et observez les erreurs de classification

## Étape 7 : Exécution Complète

### 7.1 Exécuter Tout le Workflow
1. Sélectionnez tous les nœuds : Ctrl+A (ou Cmd+A)
2. Cliquez droit et sélectionnez **Execute**
3. Attendez que tous les nœuds passent au vert ✅

### 7.2 Vérifier les Résultats
1. **Accuracy**: Doit être > 90%
2. **Visualisations**: Toutes les vues doivent s'afficher
3. **Aucune erreur**: Vérifiez la console pour les messages d'erreur

## Étape 8 : Analyse des Résultats

### 8.1 Interpréter les Visualisations
- **Scatter Plot**: Les espèces forment-elles des clusters distincts ?
- **Histogramme**: Distribution normale ou biaisée ?
- **Box Plot**: Différences significatives entre espèces ?

### 8.2 Interpréter les Statistiques
- **Corrélations**: Quelles variables sont fortement corrélées ?
- **Moyennes par espèce**: Quelles différences observez-vous ?

### 8.3 Interpréter le Machine Learning
- **Accuracy**: > 90% indique un bon modèle
- **Confusion Matrix**: Quelles espèces sont les plus difficiles à classifier ?

## Astuces et Bonnes Pratiques

### Organisation
- **Commentez vos nœuds** : Clic droit > Add Annotation
- **Groupez les nœuds** : Sélectionnez plusieurs nœuds > Clic droit > Create Metanode
- **Nommez clairement** : Renommez les nœuds pour plus de clarté

### Dépannage
- **Nœud rouge** : Erreur de configuration ou de données
- **Nœud jaune** : Avertissement mais exécution possible
- **Console** : Vérifiez les messages d'erreur détaillés

### Amélioration
- **Ajoutez des filtres** : Pour explorer des sous-ensembles de données
- **Testez d'autres algorithmes** : Random Forest, SVM, etc.
- **Créez des dashboards** : Pour présenter vos résultats

## Prochaines Étapes

Une fois ce workflow maîtrisé :
1. **Explorez d'autres datasets** dans KNIME Hub
2. **Apprenez les métanodes** pour organiser vos workflows
3. **Découvrez les extensions** (KNIME Community Extensions)
4. **Créez des workflows plus complexes** avec plusieurs algorithmes

## Support
- **Aide dans KNIME** : Help > KNIME Documentation
- **Forums** : https://forum.knime.com/
- **Tutoriels** : https://www.knime.com/videos

Félicitations ! Vous avez créé votre premier workflow KNIME complet. 🎉