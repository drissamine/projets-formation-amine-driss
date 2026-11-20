# Quick Start KNIME - Dataset Iris

## Pour les Pressés ⚡

### 1. Lancer KNIME
```bash
# Ouvrez KNIME Analytics Platform
# Créez un nouveau workflow : File > New > KNIME Workflow
# Nommez-le "Iris Test"
```

### 2. Import des Données (30 secondes)
1. **File Reader** → Sélectionnez `iris-dataset.csv`
2. **Configuration rapide** :
   - Format: CSV
   - Header: ✅ First line contains column names
   - Separator: ,

### 3. Visualisation Express (2 minutes)
Ajoutez ces 3 nœuds en parallèle :
- **Scatter Plot** : sepal_length vs petal_length (color: species)
- **Histogram** : petal_width (bins: 10)
- **Box Plot** : sepal_width groupé par species

### 4. Machine Learning Rapide (1 minute)
1. **Partitioning** : 70% train / 30% test
2. **Decision Tree Learner** : target=species
3. **Decision Tree Predictor** + **Scorer**

### 5. Exécuter Tout (10 secondes)
- Ctrl+A → Execute (F9)
- Vérifiez que tous les nœuds sont verts ✅

## Résultats Attendus
- **Accuracy**: > 90%
- **Clusters visibles** dans le scatter plot
- **Workflow fonctionnel** en 5 minutes

## Erreurs Fréquentes et Solutions

| Erreur | Solution |
|--------|----------|
| Nœud rouge | Vérifiez le chemin du fichier CSV |
| Colonnes non numériques | Vérifiez le séparateur (virgule) |
| Erreur de mémoire | Redémarrez KNIME |
| Nœud jaune | Ignorez les warnings, continuez |

## Prochaines Étapes Express
1. **Random Forest** : Meilleures performances
2. **Data Table** : Explorer les données
3. **KNIME Hub** : Télécharger d'autres workflows

## Raccourcis Clés
- **F9** : Exécuter le nœud sélectionné
- **Ctrl+A** : Sélectionner tous les nœuds
- **F6** : Exécuter le workflow
- **Suppr** : Supprimer un nœud

## Support Express
- Documentation : Help > KNIME Documentation
- Forums : forum.knime.com
- Tutoriels : knime.com/videos

---

**Temps total estimé** : 10 minutes
**Niveau requis** : Aucun
**Objectif** : Tester votre installation KNIME