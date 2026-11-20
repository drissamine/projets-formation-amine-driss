# 1. Importation de la classe SparkSession : c'est le point d'entrée principal pour utiliser Spark SQL et DataFrame
from pyspark.sql import SparkSession

# 2. Construction de la session Spark
spark = SparkSession.builder \
    .appName("TP_Spark_Jour1") \
    .master("local[*]") \
    .getOrCreate()

# --- Explications des options ci-dessus ---
# .appName : Définit le nom de votre application. Il apparaîtra dans l'interface web de Spark (Spark UI).
# .master("local[*]") : Indique que Spark doit s'exécuter sur VOTRE machine.
#                       Le [*] signifie qu'il doit utiliser TOUS les cœurs (CPU) disponibles de votre processeur.
# .getOrCreate() : Vérifie si une session Spark existe déjà. Si oui, il la récupère, sinon il en crée une nouvelle.

# 3. Récupération du SparkContext (sc)
# Le SparkContext est une version plus ancienne et plus bas-niveau de l'interface Spark.
# On l'utilise ici pour obtenir des informations sur les ressources de la machine (comme le parallélisme).
sc = spark.sparkContext

# 4. Affichage des informations de diagnostic

# Fonction pour ajouter des couleurs (ANSI escape codes)
def color_text(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

# Style moderne avec couleurs
print(color_text("=" * 60, "92"))  # Vert
print(color_text("           SPARK SESSION INITIALISÉE AVEC SUCCÈS !", "92"))
print(color_text("=" * 60, "92"))

print(color_text("[INFO] Informations de la session :", "94"))  # Bleu
print(color_text(f"   • Nom de l'application : {spark.sparkContext.appName}", "93"))  # Jaune
print(color_text(f"   • Version Spark : {spark.version}", "93"))
print(color_text(f"   • Cœurs disponibles pour le parallélisme : {sc.defaultParallelism}", "93"))
print(color_text(f"   • Maître (Master) : {spark.sparkContext.master}", "93"))

print(color_text("=" * 60, "95"))  # Magenta
print(color_text("      Prêt pour vos analyses de données avec PySpark !", "95"))
print(color_text("=" * 60, "95"))

print(color_text("Créé par DRISS Amine", "96"))  # Cyan
