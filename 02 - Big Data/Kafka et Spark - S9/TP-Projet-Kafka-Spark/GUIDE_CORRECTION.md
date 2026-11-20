# 🔧 Guide de Correction des Tests Échoués

# Kafka-Spark Streaming Pipeline

## 📋 Résumé des Problèmes

**7 tests échoués sur 44** (84.1% de réussite)

- 1 test Spark Streaming (Query 2 - Engagement)
- 6 tests Monitoring (Calculs de percentiles)

**Cause principale**: Erreurs Py4J (communication Python ↔ Java/Spark)

---

## 🔴 ÉTAPE 1: Vérifier la Configuration Spark/Java

### 1.1 Vérifier les variables d'environnement

```powershell
# Vérifier JAVA_HOME
$env:JAVA_HOME
java -version

# Vérifier SPARK_HOME
$env:SPARK_HOME
Get-ChildItem $env:SPARK_HOME

# Vérifier PYTHONPATH
$env:PYTHONPATH
```

### 1.2 Configurer correctement Spark

```powershell
# Définir SPARK_HOME (adapter le chemin)
$env:SPARK_HOME = "C:\spark"  # ou votre chemin d'installation

# Définir JAVA_HOME (adapter le chemin)
$env:JAVA_HOME = "C:\Program Files\Java\jdk-11"  # ou votre version

# Ajouter au PYTHONPATH
$env:PYTHONPATH = "$env:SPARK_HOME\python;$env:SPARK_HOME\python\lib\py4j-0.10.9.7-src.zip"
```

### 1.3 Augmenter la mémoire JVM

```powershell
# Augmenter la mémoire pour le driver Spark
$env:SPARK_DRIVER_MEMORY = "2g"

# Augmenter la mémoire pour les executors
$env:SPARK_EXECUTOR_MEMORY = "4g"

# Options JVM supplémentaires
$env:SPARK_DRIVER_OPTS = "-Xms1g -Xmx2g"
```

---

## 🔴 ÉTAPE 2: Corriger le Code

### 2.1 Corriger les warnings datetime

**Fichier**: `producer/kafka_producer.py` (ligne 74)

```python
# ❌ AVANT (déprécié)
timestamp = datetime.datetime.utcnow()

# ✅ APRÈS (recommandé)
from datetime import datetime, timezone
timestamp = datetime.now(timezone.utc)
```

### 2.2 Corriger Query 2 (Engagement)

**Fichier**: `spark/consumer/spark_streaming_app.py`

Vérifier la requête d'engagement et simplifier si nécessaire:

```python
# Vérifier que les calculs de fenêtrage sont corrects
# Simplifier les agrégations complexes
# Tester avec un jeu de données réduit
```

### 2.3 Corriger les calculs de percentiles

**Fichier**: `monitoring/metrics.py`

```python
# Option 1: Utiliser numpy pour les percentiles
import numpy as np

def calculate_percentile(data, percentile):
    if not data:
        return 0
    return np.percentile(data, percentile)

# Option 2: Utiliser statistics (Python standard)
import statistics

def calculate_median(data):
    if not data:
        return 0
    return statistics.median(data)
```

---

## 🔴 ÉTAPE 3: Réexécuter les Tests

### 3.1 Tests complets

```powershell
# Tous les tests
python -m pytest tests/ -v

# Avec rapport détaillé
python -m pytest tests/ -v --tb=short
```

### 3.2 Tests spécifiques (problématiques)

```powershell
# Test Query 2 uniquement
python -m pytest tests/test_spark_streaming.py::TestSparkStreamingQueries::test_query_2_engagement_dataframe -v

# Tests de percentiles uniquement
python -m pytest tests/test_monitoring.py -k "percentile" -v
```

### 3.3 Tests sans les problématiques (pour validation)

```powershell
# Exclure les tests qui échouent
python -m pytest tests/ -v -k "not percentile and not engagement"
```

---

## 🟡 ÉTAPE 4: Solutions Alternatives

### 4.1 Si les erreurs Py4J persistent

**Option A**: Downgrade de PySpark

```powershell
pip uninstall pyspark
pip install pyspark==3.3.0  # Version stable
```

**Option B**: Upgrade de PySpark

```powershell
pip install --upgrade pyspark
```

**Option C**: Réinstaller complètement

```powershell
pip uninstall pyspark py4j
pip install pyspark==3.4.1
```

### 4.2 Utiliser des mocks pour les tests

Modifier les tests pour utiliser des mocks au lieu de vraies connexions Spark:

```python
from unittest.mock import Mock, patch

@patch('pyspark.sql.SparkSession')
def test_with_mock(mock_spark):
    # Test sans vraie connexion Spark
    pass
```

---

## 🟢 ÉTAPE 5: Validation Finale

### 5.1 Exécuter tous les tests

```powershell
python -m pytest tests/ -v
```

### 5.2 Générer le rapport de couverture

```powershell
python -m pytest tests/ --cov=producer --cov=spark --cov=monitoring --cov-report=html
```

### 5.3 Générer le rapport HTML visuel

```powershell
python generate_test_report.py
```

### 5.4 Ouvrir le rapport

```powershell
# Ouvrir le rapport HTML dans le navigateur
Start-Process test_report.html
```

---

## 📊 Checklist de Validation

- [ ] Variables d'environnement configurées (JAVA_HOME, SPARK_HOME)
- [ ] Mémoire JVM augmentée (SPARK_DRIVER_MEMORY, SPARK_EXECUTOR_MEMORY)
- [ ] Warnings datetime corrigés
- [ ] Query 2 (Engagement) fonctionne
- [ ] Calculs de percentiles fonctionnent
- [ ] Tous les tests passent (44/44)
- [ ] Rapport de couverture généré
- [ ] Rapport HTML généré

---

## 🆘 Dépannage Avancé

### Si les tests échouent toujours

1. **Vérifier les logs Spark**

   ```powershell
   # Activer le logging debug
   $env:SPARK_LOG_LEVEL = "DEBUG"
   ```

2. **Tester Spark manuellement**

   ```powershell
   # Lancer le shell PySpark
   pyspark

   # Dans le shell, tester:
   >>> spark.version
   >>> df = spark.createDataFrame([(1, "test")], ["id", "value"])
   >>> df.show()
   ```

3. **Vérifier les dépendances**

   ```powershell
   pip list | Select-String -Pattern "spark|py4j"
   ```

4. **Réinstaller les dépendances**
   ```powershell
   pip install -r producer/requirements.txt --force-reinstall
   pip install -r spark/consumer/requirements.txt --force-reinstall
   ```

---

## 📞 Support

Si les problèmes persistent:

1. Consulter la documentation Spark: https://spark.apache.org/docs/latest/
2. Vérifier les issues GitHub de PySpark
3. Consulter Stack Overflow avec le tag `pyspark` et `py4j`

---

## 📝 Notes Importantes

- **Temps estimé de correction**: 30-60 minutes
- **Niveau de difficulté**: Moyen
- **Impact**: Critique pour la validation complète du projet

---

**Dernière mise à jour**: 2 février 2026
**Auteur**: Analyse automatique des tests
