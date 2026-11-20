# 📚 Guide Complet - Exercices PySpark

## 📋 Vue d'ensemble

Ce dossier contient 4 exercices PySpark avec leurs solutions, adaptés pour contourner les problèmes de compatibilité avec Python 3.14.

## ✅ Statut des exercices

| Exercice  | Fichier                      | Statut              | Notes                             |
| --------- | ---------------------------- | ------------------- | --------------------------------- |
| **1-2**   | `exercise1_2.py`             | ✅ Fonctionne       | Word Count avec RDD               |
| **2**     | `exercise2.py`               | ✅ Fonctionne       | Word Count avec RDD               |
| **3**     | `exercise1_3.py`             | ⚠️ Code RDD correct | Incompatibilité Python 3.14       |
| **3 Alt** | `exercise1_3_alternative.py` | ✅ Fonctionne       | Version Python natif              |
| **4**     | `exercise4.py`               | ⚠️ Code SQL correct | Incompatibilité Python 3.14       |
| **4 Alt** | `exercise4_alternative.py`   | ✅ Fonctionne       | Version Python natif (Simul. SQL) |

## 🚀 Exécution rapide

```powershell
# Exercice 1-2 (Word Count)
python exercise1_2.py

# Exercice 2 (Word Count)
python exercise2.py

# Exercice 3 (Analyse Ventes)
python exercise1_3_alternative.py

# Exercice 4 (Analyse Employés SQL)
python exercise4_alternative.py
```

## 📊 Résultats attendus

### Exercice 1-2 et 2 : Word Count

```
🔧 Spark initialisé avec succès!
Top 10 mots:
spark: 3
et: 2
...
```

### Exercice 3 : Analyse de ventes

```
CA TOTAL: 32,100€
Produit le plus vendu: Smartphone (18 unités)
Ville meilleur panier: Lyon (6,400€)
```

### Exercice 4 : Spark SQL

```
1. SALAIRE MOYEN PAR DÉPARTEMENT:
Département  Salaire Moyen   Nb Employés
IT           5,250.00€       2
Sales        4,650.00€       2
...

3. TOP 3 DES SALAIRES:
Nom        Département  Salaire      Ville
Charlie    IT           5,500€       Paris
Alice      IT           5,000€       Paris
...
```

## ⚠️ Problème connu : Python 3.14

**Symptôme** : `Python worker failed to connect back` / `java.io.EOFException`

**Cause** : PySpark 4.1.1 n'est pas encore pleinement compatible avec Python 3.14 (sorti récemment).

**Solution Recommandée** : Utiliser les versions "alternative" (`_alternative.py`) qui utilisent Python natif pour produire les mêmes résultats et valider votre logique.

## 📁 Structure des fichiers

```
M2/S6/
├── exercise1_2.py              # ✅ Word Count
├── exercise2.py                # ✅ Word Count
├── exercise1_3.py              # ⚠️ Analyse ventes (Spark RDD)
├── exercise1_3_alternative.py  # ✅ Analyse ventes (Python Natif)
├── exercise4.py                # ⚠️ Analyse employés (Spark SQL)
├── exercise4_alternative.py    # ✅ Analyse employés (Python Natif)
├── CORRECTIONS_APPLIQUEES.md   # 📝 Détail technique des correctifs
├── EXERCICE3_README.md         # 📝 Guide spécifique Exercice 3
├── EXERCICE4_README.md         # 📝 Guide spécifique Exercice 4
└── README.md                   # 📝 Ce fichier
```

## 💡 Conseils

1. **Logs Windows** : Les warnings `WARN NativeCodeLoader` sont normaux et sans impact.
2. **Production** : Pour exécuter les versions Spark pures (`exercise1_3.py`, `exercise4.py`), utilisez Python 3.11 ou 3.12.
3. **Apprentissage** : Les versions alternatives sont excellentes pour comprendre la logique des algorithmes (MapReduce, GroupBy, Join) sans la complexité de l'infrastructure Spark.

---

✅ **Tous les exercices sont prêts à être testés !**
