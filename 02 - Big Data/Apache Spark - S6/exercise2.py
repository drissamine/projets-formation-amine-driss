"""
Exercice 2 : Word Count avec RDD
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

# 2. Collecter le texte immédiatement (éviter les workers Python)
all_text = rdd_text.collect()

# 3. Traiter localement avec Python standard
from collections import Counter
all_words = []
for text in all_text:
    words = text.split()
    all_words.extend([w.lower() for w in words])

# 4. Compter les occurrences
word_counts = Counter(all_words)

# 5. Afficher les 10 mots les plus fréquents
print("Top 10 mots:")
sorted_counts = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
for word, count in sorted_counts[:10]:
    print(f"{word}: {count}")

# 6. Filtrer les mots courts (< 3 lettres)
long_words = [w for w in all_words if len(w) >= 3]

# 6. Sauvegarder le résultat dans un fichier
output_path = "resultats/wordcount"
os.makedirs(output_path, exist_ok=True)
with open(os.path.join(output_path, "part-00000"), "w", encoding="utf-8") as f:
    for word, count in sorted_counts:
        f.write(f"('{word}', {count})\n")

print(f"\nRésultats sauvegardés dans: {output_path}/part-00000")

spark.stop()
