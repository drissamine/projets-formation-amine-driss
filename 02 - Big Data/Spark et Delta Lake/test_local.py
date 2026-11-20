"""
Script de test local pour le projet d'analyse des ventes avec Spark et Delta Lake
Exécute les parties 1 à 6 (sans les commandes Databricks spécifiques)
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType
import os

# Création de la session Spark avec Delta Lake
from delta import configure_spark_with_delta_pip
builder = SparkSession.builder \
    .appName("SalesAnalysisDelta_Local") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.sql.adaptive.enabled", "false")
spark = configure_spark_with_delta_pip(builder).getOrCreate()

print(f"Spark version: {spark.version}")

# ============================================================
# Partie 1 – Préparation des données
# ============================================================
print("\n" + "="*60)
print("PARTIE 1 - PREPARATION DES DONNEES")
print("="*60)

schema = StructType([
    StructField("SaleID", IntegerType(), True),
    StructField("Date", StringType(), True),
    StructField("Product", StringType(), True),
    StructField("Category", StringType(), True),
    StructField("UnitPrice", DoubleType(), True),
    StructField("Quantity", IntegerType(), True),
    StructField("City", StringType(), True),
    StructField("Customer", StringType(), True)
])

df = spark.read \
    .option("header", "true") \
    .option("delimiter", ",") \
    .option("quote", "\"") \
    .option("escape", "\\") \
    .schema(schema) \
    .csv("sales_data.csv")

print("\nSchema du DataFrame:")
df.printSchema()

print("\n10 premieres lignes:")
df.show(10, truncate=False)

total_ventes = df.count()
print(f"\nNombre total de ventes: {total_ventes}")

df = df.withColumn("Total", col("UnitPrice") * col("Quantity"))
print("\nDataFrame avec colonne Total:")
df.show(5, truncate=False)

# ============================================================
# Partie 2 – Création d'une table Delta
# ============================================================
print("\n" + "="*60)
print("PARTIE 2 - CREATION TABLE DELTA")
print("="*60)

# Table gérée
df.write.mode("overwrite").format("delta").saveAsTable("sales_delta")
print("Table Delta 'sales_delta' creee.")

# Table externe
external_path = os.path.abspath("./data/sales_external")
df.write.mode("overwrite").format("delta").option("path", external_path).saveAsTable("sales_external")
print(f"Table externe 'sales_external' creee a {external_path}")

# Table gérée 2
spark.sql("CREATE TABLE IF NOT EXISTS sales_managed USING delta AS SELECT * FROM sales_delta")
print("Table geree 'sales_managed' creee.")

# Comparaison
print("\n--- Location table externe ---")
spark.sql("DESCRIBE EXTENDED sales_external").filter(col("col_name") == "Location").show(truncate=False)
print("\n--- Location table geree ---")
spark.sql("DESCRIBE EXTENDED sales_managed").filter(col("col_name") == "Location").show(truncate=False)

# ============================================================
# Partie 3 – Manipulation des données
# ============================================================
print("\n" + "="*60)
print("PARTIE 3 - MANIPULATION DES DONNEES")
print("="*60)

# 3.1 Augmentation de 10%
print("\n--- 3.1 Augmentation 10% prix Électronique ---")
spark.sql("""
    UPDATE sales_delta
    SET UnitPrice = ROUND(UnitPrice * 1.10, 2),
        Total = ROUND(UnitPrice * 1.10 * Quantity, 2)
    WHERE Category = 'Électronique'
""")
spark.sql("""
    SELECT Category, ROUND(AVG(UnitPrice), 2) as prix_moyen
    FROM sales_delta WHERE Category = 'Électronique' GROUP BY Category
""").show()

# 3.2 Suppression ville
print("\n--- 3.2 Suppression ventes Lyon ---")
nb_lyon = spark.sql("SELECT COUNT(*) as n FROM sales_delta WHERE City = 'Lyon'").collect()[0][0]
print(f"Ventes a Lyon avant suppression: {nb_lyon}")
spark.sql("DELETE FROM sales_delta WHERE City = 'Lyon'")
nb_lyon = spark.sql("SELECT COUNT(*) as n FROM sales_delta WHERE City = 'Lyon'").collect()[0][0]
print(f"Ventes a Lyon apres suppression: {nb_lyon}")

# 3.3 Ajout de ventes
print("\n--- 3.3 Ajout de 5 nouvelles ventes ---")
new_sales = [
    (106, "2024-03-01", "Drone DJI", "Électronique", 999.99, 1, "Paris", "Moreau"),
    (107, "2024-03-02", "Montre Connectée", "Électronique", 349.99, 2, "Marseille", "Dupont"),
    (108, "2024-03-03", "Sac à Dos Randonnée", "Sports", 79.99, 3, "Bordeaux", "Petit"),
    (109, "2024-03-04", "Romans Policiers", "Livres", 24.99, 5, "Toulouse", "Martin"),
    (110, "2024-03-05", "Grille-Pain", "Maison", 49.99, 2, "Lille", "Bernard")
]
new_df = spark.createDataFrame(new_sales, schema).withColumn("Total", col("UnitPrice") * col("Quantity"))
new_df.write.mode("append").format("delta").saveAsTable("sales_delta")
total = spark.sql("SELECT COUNT(*) as n FROM sales_delta").collect()[0][0]
print(f"Total ventes apres ajout: {total}")

# 3.4 Correction de nom
print("\n--- 3.4 Correction nom produit ---")
spark.sql("UPDATE sales_delta SET Product = 'Table Basse' WHERE Product = 'Table basse'")
spark.sql("SELECT * FROM sales_delta WHERE Product LIKE 'Table%'").show(truncate=False)

# ============================================================
# Partie 4 – Historique et Time Travel
# ============================================================
print("\n" + "="*60)
print("PARTIE 4 - HISTORIQUE ET TIME TRAVEL")
print("="*60)

print("\n--- Historique des modifications ---")
spark.sql("DESCRIBE HISTORY sales_delta").show(truncate=False)

print("\n--- Version 0 (originale) ---")
df_v0 = spark.read.format("delta").option("versionAsOf", "0").table("sales_delta")
print(f"Nombre de ventes version 0: {df_v0.count()}")

print(f"\nNombre de ventes version actuelle: {spark.table('sales_delta').count()}")

print("\n--- Différence ---")
print(f"Difference: {spark.table('sales_delta').count() - df_v0.count()} ventes")
print("(Ventes de Lyon supprimees + 5 nouvelles ventes ajoutees)")

# ============================================================
# Partie 5 – Analyses avec Spark SQL
# ============================================================
print("\n" + "="*60)
print("PARTIE 5 - ANALYSES SPARK SQL")
print("="*60)

queries = [
    ("1 - Chiffre d'affaires total",
     "SELECT ROUND(SUM(Total), 2) AS Chiffre_Affaires_Total FROM sales_delta"),
    ("2 - CA par ville",
     "SELECT City, ROUND(SUM(Total), 2) AS CA FROM sales_delta GROUP BY City ORDER BY CA DESC"),
    ("3 - CA par catégorie",
     "SELECT Category, ROUND(SUM(Total), 2) AS CA FROM sales_delta GROUP BY Category ORDER BY CA DESC"),
    ("4 - Produit le plus vendu",
     "SELECT Product, SUM(Quantity) AS Qte, ROUND(SUM(Total), 2) AS CA FROM sales_delta GROUP BY Product ORDER BY Qte DESC LIMIT 10"),
    ("5 - Client le plus actif",
     "SELECT Customer, COUNT(*) AS Achats, ROUND(SUM(Total), 2) AS Montant FROM sales_delta GROUP BY Customer ORDER BY Achats DESC LIMIT 10"),
    ("6 - Top 5 villes",
     "SELECT City, ROUND(SUM(Total), 2) AS CA, COUNT(*) AS Ventes FROM sales_delta GROUP BY City ORDER BY CA DESC LIMIT 5"),
    ("7 - Ventes par mois",
     "SELECT SUBSTRING(Date, 1, 7) AS Mois, COUNT(*) AS Ventes, ROUND(SUM(Total), 2) AS CA FROM sales_delta GROUP BY SUBSTRING(Date, 1, 7) ORDER BY Mois"),
    ("8 - Moyenne des prix par catégorie",
     "SELECT Category, ROUND(AVG(UnitPrice), 2) AS Prix_Moyen FROM sales_delta GROUP BY Category ORDER BY Prix_Moyen DESC"),
    ("9 - Produit le plus cher",
     "SELECT Product, UnitPrice FROM sales_delta ORDER BY UnitPrice DESC LIMIT 5"),
    ("10 - Ventes par catégorie",
     "SELECT Category, COUNT(*) AS Ventes, SUM(Quantity) AS Qte FROM sales_delta GROUP BY Category ORDER BY Ventes DESC")
]

for title, query in queries:
    print(f"\n--- {title} ---")
    spark.sql(query).show(truncate=False)

# ============================================================
# Partie 6 – Optimisation
# ============================================================
print("\n" + "="*60)
print("PARTIE 6 - OPTIMISATION")
print("="*60)

print("\n--- OPTIMIZE ---")
spark.sql("OPTIMIZE sales_delta")

print("\n--- VACUUM ---")
spark.sql("VACUUM sales_delta RETAIN 24 HOURS")

print("\n" + "="*60)
print("PROJET TERMINE AVEC SUCCES!")
print("="*60)

spark.stop()
