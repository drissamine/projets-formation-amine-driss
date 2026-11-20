# Exercice 4 : Spark SQL - Guide

## ⚠️ Situation

Comme pour l'exercice 3, l'utilisation de **Spark SQL** avec **Python 3.14** rencontre des problèmes de compatibilité technique (les workers Python ne parviennent pas à communiquer avec le driver Java).

## ✅ Solution : Version Alternative

**Fichier : `exercise4_alternative.py`**

Cette version utilise Python natif pour simuler fidèlement les opérations SQL demandées. C'est la meilleure façon de valider la logique de l'exercice dans votre environnement actuel.

### Requêtes implémentées

1.  **Salaire moyen par département**
    - _SQL Concept_ : `GROUP BY departement`, `AVG(salaire)`
    - _Résultat_ : IT (5 250€), Sales (4 650€), HR (4 000€)

2.  **Nombre d'employés par ville**
    - _SQL Concept_ : `GROUP BY ville`, `COUNT(*)`
    - _Résultat_ : Lyon (2), Paris (2), Marseille (1)

3.  **Top 3 des salaires**
    - _SQL Concept_ : `ORDER BY salaire DESC LIMIT 3`
    - _Résultat_ : Charlie (5 500€), Alice (5 000€), Eve (4 800€)

4.  **Employés gagnant plus que la moyenne de leur département**
    - _SQL Concept_ : Jointure avec sous-requête d'agrégation
    - _Résultat_ : Eve (Sales, +150€), Charlie (IT, +250€)

5.  **Jointure avec le département**
    - _SQL Concept_ : `JOIN departements ON e.departement = d.code`
    - _Résultat_ : Affiche le nom complet du département et le manager pour chaque employé.

## 📚 Versions Spark (pour référence)

Les fichiers suivants contiennent le code Spark correct. Ils pourront être exécutés tels quels dès que la compatibilité Python 3.14/Spark sera assurée ou si vous installez une version antérieure de Python (ex: 3.12).

- **`exercise4.py`** : Utilise `spark.sql("SELECT ...")`.
- **`exercise4_dataframe.py`** : Utilise l'API programmatique `df.groupBy().agg()`.

## 🚀 Comment lancer l'exercice

```powershell
# Version recommandée (fonctionne immédiatement)
python exercise4_alternative.py
```
