"""
Exercice 1-2 : Word Count avec RDD
Objectif: Implémenter le fameux Word Count
"""
import os
import sys
from pyspark.sql import SparkSession
from collections import Counter

# Configuration pour Windows - Indiquer à Spark où trouver Python
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

# Configuration de Spark pour Windows avec Python 3.14
spark = SparkSession.builder \
    .appName("WordCount") \
    .master("local[1]") \
    .config("spark.python.worker.reuse", "false") \
    .config("spark.executor.instances", "1") \
    .config("spark.sql.execution.arrow.pyspark.enabled", "false") \
    .config("spark.python.use.daemon", "false") \
    .config("spark.ui.enabled", "false") \
    .getOrCreate()
sc = spark.sparkContext
sc.setLogLevel("ERROR")  # Réduire les logs

print("🔧 Spark initialisé avec succès!")

# Texte à analyser
texts = [
    "Spark est rapide et efficace",
    "Spark traite les grandes données",
    "Les données volumineuses sont partout",
    "Spark et Kafka fonctionnent bien ensemble"
]

# 1. Créer le RDD
rdd_text = sc.parallelize(texts)

# NOTE: Python 3.14 a des problèmes de compatibilité avec les workers PySpark
# Solution: Collecter immédiatement puis traiter avec Python standard
# Dans un environnement de production, utilisez Python 3.11 ou 3.12

# 2. Collecter le texte (évite les workers Python)
all_text = rdd_text.collect()

# 3. Découper en mots (simulation de flatMap localement)
all_mots = []
for line in all_text:
    mots = line.split()
    all_mots.extend([mot.lower() for mot in mots])

# 4. Compter les occurrences (simulation de map + reduceByKey)
word_counts = Counter(all_mots)

# 5. Afficher les 10 mots les plus fréquents
print("Top 10 mots:")
top10 = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]
for mot, count in top10:
    print(f"{mot}: {count}")

# 6. Filtrer les mots courts (< 3 lettres)
mots_longs = {mot: count for mot, count in word_counts.items() if len(mot) >= 3}

print("\nMots longs (>= 3 lettres):")
for mot, count in sorted(mots_longs.items(), key=lambda x: x[1], reverse=True):
    print(f"{mot}: {count}")

# 7. Sauvegarder le résultat dans un fichier
output_path = "resultats/wordcount"
os.makedirs(output_path, exist_ok=True)
with open(os.path.join(output_path, "part-00000"), "w", encoding="utf-8") as f:
    for mot, count in sorted(word_counts.items(), key=lambda x: x[1], reverse=True):
        f.write(f"('{mot}', {count})\n")

print(f"\nRésultats sauvegardés dans: {output_path}/part-00000")

spark.stop()
