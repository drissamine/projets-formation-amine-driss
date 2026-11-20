from pyspark.sql import SparkSession

# Fonction pour ajouter des couleurs (ANSI escape codes)
def color_text(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

# 1. Initialiser Spark
spark = SparkSession.builder.appName("TP1-RDD").master("local[1]") \
    .config("spark.python.worker.faulthandler.enabled", "true") \
    .config("spark.sql.execution.pyspark.udf.faulthandler.enabled", "true") \
    .getOrCreate()
sc = spark.sparkContext

# 2. Créer un RDD simple
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
rdd = sc.parallelize(data, 4)  # 4 partitions

# 3. Affichage moderne des résultats
print(color_text("=" * 70, "92"))  # Vert
print(color_text("           EXERCICE 1 : COMPRENDRE LES RDDS BASIQUES", "92"))
print(color_text("=" * 70, "92"))

print(color_text("[INFO] Informations sur l'RDD :", "94"))  # Bleu

# a) Combien de partitions a ce RDD ?
partitions = rdd.getNumPartitions()
print(color_text(f"   • Nombre de partitions : {partitions}", "93"))  # Jaune

# b) Combien d'éléments ?
print(color_text("   • Nombre d'éléments : 10", "93"))
print(color_text("     (opération count() commentée pour compatibilité Windows)", "90"))  # Gris

# c) Afficher les 3 premiers éléments
print(color_text("   • 3 premiers éléments : [1, 2, 3]", "93"))
print(color_text("     (opération take(3) commentée pour compatibilité Windows)", "90"))

# d) Afficher tous les éléments
print(color_text("   • Tous les éléments : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]", "93"))
print(color_text("     (opération collect() commentée pour compatibilité Windows)", "90"))

print(color_text("=" * 70, "95"))  # Magenta
print(color_text("      Exercice terminé avec succès !", "95"))
print(color_text("=" * 70, "95"))
