# Databricks notebook source
# MAGIC %md
# MAGIC # Projet : Système de gestion et d'analyse des ventes avec Spark et Delta Lake
# MAGIC
# MAGIC **Objectif** : Charger, stocker, manipuler et analyser des données de ventes en utilisant Apache Spark et Delta Lake.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Partie 1 – Préparation des données

# COMMAND ----------

# 1.1 - Configuration Spark et import des bibliothèques
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, DateType
import datetime

# Création de la session Spark avec support Delta
spark = SparkSession.builder \
    .appName("SalesAnalysisDelta") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

print(f"Version Spark : {spark.version}")

# COMMAND ----------

# 1.2 - Définition du schéma explicite
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

# 1.3 - Chargement du fichier CSV
file_path = "/FileStore/tables/sales_data.csv"
# Pour exécution locale, utiliser le chemin local
# file_path = "sales_data.csv"

df = spark.read \
    .option("header", "true") \
    .option("delimiter", ",") \
    .option("quote", "\"") \
    .option("escape", "\\") \
    .schema(schema) \
    .csv(file_path)

# COMMAND ----------

# 1.3 (suite) - Affichage du schéma
print("=== Schéma du DataFrame ===")
df.printSchema()

# COMMAND ----------

# 1.3 (suite) - Affichage des 10 premières lignes
print("=== 10 premières lignes ===")
df.show(10, truncate=False)

# COMMAND ----------

# 1.3 (suite) - Nombre total de ventes
total_ventes = df.count()
print(f"=== Nombre total de ventes : {total_ventes} ===")

# COMMAND ----------

# 1.4 - Ajout de la colonne calculée Total = UnitPrice × Quantity
df = df.withColumn("Total", col("UnitPrice") * col("Quantity"))

print("=== DataFrame avec colonne Total ===")
df.show(10, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Partie 2 – Création d’une table Delta

# COMMAND ----------

# 2.1 - Enregistrement dans une table Delta
print("=== Enregistrement dans la table Delta 'sales_delta' ===")
df.write \
    .mode("overwrite") \
    .format("delta") \
    .saveAsTable("sales_delta")

print("Table Delta créée avec succès !")

# COMMAND ----------

# 2.2 - Affichage du contenu du dossier Delta
print("=== Contenu du dossier Delta ===")
delta_path = spark.sql("DESCRIBE EXTENDED sales_delta") \
    .filter(col("col_name") == "Location") \
    .select("data_type") \
    .collect()[0][0]

print(f"Emplacement de la table Delta : {delta_path}")

# Vérification avec la commande fs
display(dbutils.fs.ls(delta_path))

# COMMAND ----------

# 2.3 - Création d'une table externe Delta
print("=== Création d'une table externe Delta ===")
external_path = "/user/hive/warehouse/sales_external"

df.write \
    .mode("overwrite") \
    .format("delta") \
    .option("path", external_path) \
    .saveAsTable("sales_external")

print(f"Table externe créée à l'emplacement : {external_path}")

# COMMAND ----------

# 2.3 (suite) - Création d'une table gérée (managed)
print("=== Création d'une table gérée (managed) ===")
# La table gérée est stockée dans le warehouse par défaut
# Nous utilisons la table 'sales_delta' déjà créée comme table gérée
spark.sql("""
    CREATE TABLE IF NOT EXISTS sales_managed
    USING delta
    AS SELECT * FROM sales_delta
""")

print("Table gérée 'sales_managed' créée avec succès !")

# COMMAND ----------

# 2.4 - Comparaison des deux tables
print("=== Comparaison : Table externe vs Table gérée ===")

print("\n--- Table externe (sales_external) ---")
desc_ext = spark.sql("DESCRIBE EXTENDED sales_external")
display(desc_ext)

print("\n--- Table gérée (sales_managed) ---")
desc_man = spark.sql("DESCRIBE EXTENDED sales_managed")
display(desc_man)

# Explication
print("""
--- Différence clé ---
- Table gérée (Managed) : Spark gère le cycle de vie complet. Si on supprime la table,
  les données sont également supprimées. Le chemin est dans le warehouse par défaut.
- Table externe (External) : On spécifie un emplacement. Si on supprime la table,
  seules les métadonnées sont supprimées, les données persistent.
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Partie 3 – Manipulation des données

# COMMAND ----------

# 3.1 - Augmenter de 10% le prix des produits de la catégorie 'Électronique'
print("=== Augmentation de 10% des prix de la catégorie Électronique ===")
print("Avant modification :")
spark.sql("""
    SELECT Category, COUNT(*) as nb_produits, ROUND(AVG(UnitPrice), 2) as prix_moyen
    FROM sales_delta
    WHERE Category = 'Électronique'
    GROUP BY Category
""").show()

spark.sql("""
    UPDATE sales_delta
    SET UnitPrice = ROUND(UnitPrice * 1.10, 2),
        Total = ROUND(UnitPrice * 1.10 * Quantity, 2)
    WHERE Category = 'Électronique'
""")

print("Après modification :")
spark.sql("""
    SELECT Category, COUNT(*) as nb_produits, ROUND(AVG(UnitPrice), 2) as prix_moyen
    FROM sales_delta
    WHERE Category = 'Électronique'
    GROUP BY Category
""").show()

# COMMAND ----------

# 3.2 - Supprimer toutes les ventes de la ville 'Lyon'
print("=== Suppression des ventes de la ville de Lyon ===")
print("Nombre de ventes à Lyon avant suppression :")
spark.sql("SELECT COUNT(*) as nb_ventes FROM sales_delta WHERE City = 'Lyon'").show()

spark.sql("DELETE FROM sales_delta WHERE City = 'Lyon'")

print("Ventes restantes depuis Lyon après suppression :")
spark.sql("SELECT COUNT(*) as nb_ventes FROM sales_delta WHERE City = 'Lyon'").show()

# COMMAND ----------

# 3.3 - Ajouter 5 nouvelles ventes
print("=== Ajout de 5 nouvelles ventes ===")
new_sales_data = [
    (106, "2024-03-01", "Drone DJI", "Électronique", 999.99, 1, "Paris", "Moreau"),
    (107, "2024-03-02", "Montre Connectée", "Électronique", 349.99, 2, "Marseille", "Dupont"),
    (108, "2024-03-03", "Sac à Dos Randonnée", "Sports", 79.99, 3, "Bordeaux", "Petit"),
    (109, "2024-03-04", "Romans Policiers", "Livres", 24.99, 5, "Toulouse", "Martin"),
    (110, "2024-03-05", "Grille-Pain", "Maison", 49.99, 2, "Lille", "Bernard")
]

new_sales_df = spark.createDataFrame(new_sales_data, schema)

# Ajouter la colonne Total
new_sales_df = new_sales_df.withColumn("Total", col("UnitPrice") * col("Quantity"))

new_sales_df.write \
    .mode("append") \
    .format("delta") \
    .saveAsTable("sales_delta")

print("5 nouvelles ventes ajoutées !")
print("Vérification :")
spark.sql("SELECT COUNT(*) as total_ventes FROM sales_delta").show()

# COMMAND ----------

# 3.4 - Corriger le nom d'un produit mal écrit
print("=== Correction du nom de produit 'Table basse' → 'Table Basse' ===")
print("Avant correction :")
spark.sql("SELECT * FROM sales_delta WHERE Product LIKE 'Table%'").show(truncate=False)

spark.sql("""
    UPDATE sales_delta
    SET Product = 'Table Basse'
    WHERE Product = 'Table basse'
""")

print("Après correction :")
spark.sql("SELECT * FROM sales_delta WHERE Product LIKE 'Table%'").show(truncate=False)

# COMMAND ----------

# Affichage final des données après toutes les manipulations
print("=== Aperçu final des données après toutes les manipulations ===")
spark.sql("SELECT * FROM sales_delta ORDER BY SaleID").show(20, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Partie 4 – Historique et Time Travel

# COMMAND ----------

# 4.1 - Afficher l'historique des modifications de la table Delta
print("=== Historique des modifications de la table Delta ===")
display(spark.sql("DESCRIBE HISTORY sales_delta"))

# COMMAND ----------

# 4.2 - Revenir à une ancienne version avec versionAsOf
print("=== Revenir à la version 0 (données originales) ===")
df_version_0 = spark.read \
    .format("delta") \
    .option("versionAsOf", "0") \
    .table("sales_delta")

print("Données à la version 0 (originale) :")
df_version_0.show(10, truncate=False)

# COMMAND ----------

# 4.3 - Comparer l'ancienne version et la version actuelle
print("=== Comparaison version 0 vs version actuelle ===")

# Version actuelle
df_current = spark.table("sales_delta")

print("Version 0 (originale) - Nombre de ventes :", df_version_0.count())
print("Version actuelle - Nombre de ventes :", df_current.count())

print("\nDifférence de nombre de ventes :", df_current.count() - df_version_0.count())
print("(Les ventes de Lyon ont été supprimées et 5 nouvelles ventes ont été ajoutées)")

print("\n--- Prix moyen par catégorie : Comparaison ---")
print("Version 0 :")
df_version_0.groupBy("Category").avg("UnitPrice").show(truncate=False)
print("Version actuelle :")
df_current.groupBy("Category").avg("UnitPrice").show(truncate=False)

# COMMAND ----------

# 4.4 - Explication de l'intérêt du Time Travel
print("""
═══════════════════════════════════════════════════════════════════
  Intérêt du Time Travel dans Delta Lake
═══════════════════════════════════════════════════════════════════

Le Time Travel permet d'accéder aux versions précédentes d'une table
Delta Lake. Ses principaux avantages sont :

1. Audit et traçabilité : Chaque modification est versionnée.
   On peut retracer qui a fait quoi et quand.

2. Reprise après erreur : Si une mise à jour ou suppression
   accidentelle se produit, on peut revenir à une version antérieure
   facilement avec versionAsOf ou timestampAsOf.

3. Reproductibilité : Pour des analyses ou des modèles ML, on peut
   garantir l'utilisation exactement des mêmes données.

4. Comparaison temporelle : On peut comparer l'état des données
   entre différentes versions pour analyser l'impact des changements.

5. Conformité réglementaire : Conservation de l'historique complet
   pour satisfaire aux exigences d'audit (RGPD, SOX, etc.).

6. Data Testing : Tester des transformations sur une version passée
   sans affecter les données courantes.

Syntaxes possibles :
  - spark.read.option("versionAsOf", "0").table("ma_table")
  - spark.read.option("timestampAsOf", "2024-01-15").table("ma_table")
═══════════════════════════════════════════════════════════════════
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Partie 5 – Analyses avec Spark SQL

# COMMAND ----------

# 5.1 - Chiffre d'affaires total
print("═══════════════════════════════════════")
print("  1 - Chiffre d'affaires total")
print("═══════════════════════════════════════")
spark.sql("""
    SELECT ROUND(SUM(Total), 2) AS Chiffre_Affaires_Total
    FROM sales_delta
""").show(truncate=False)

# COMMAND ----------

# 5.2 - Chiffre d'affaires par ville
print("═══════════════════════════════════════")
print("  2 - Chiffre d'affaires par ville")
print("═══════════════════════════════════════")
spark.sql("""
    SELECT City,
           ROUND(SUM(Total), 2) AS Chiffre_Affaires,
           COUNT(*) AS Nombre_Ventes
    FROM sales_delta
    GROUP BY City
    ORDER BY Chiffre_Affaires DESC
""").show(truncate=False)

# COMMAND ----------

# 5.3 - Chiffre d'affaires par catégorie
print("═══════════════════════════════════════")
print("  3 - Chiffre d'affaires par catégorie")
print("═══════════════════════════════════════")
spark.sql("""
    SELECT Category,
           ROUND(SUM(Total), 2) AS Chiffre_Affaires,
           COUNT(*) AS Nombre_Ventes
    FROM sales_delta
    GROUP BY Category
    ORDER BY Chiffre_Affaires DESC
""").show(truncate=False)

# COMMAND ----------

# 5.4 - Produit le plus vendu
print("═══════════════════════════════════════")
print("  4 - Produit le plus vendu (par quantité)")
print("═══════════════════════════════════════")
spark.sql("""
    SELECT Product,
           SUM(Quantity) AS Quantite_Totale_Vendue,
           ROUND(SUM(Total), 2) AS Chiffre_Affaires
    FROM sales_delta
    GROUP BY Product
    ORDER BY Quantite_Totale_Vendue DESC
    LIMIT 10
""").show(truncate=False)

# COMMAND ----------

# 5.5 - Client ayant effectué le plus d'achats
print("═══════════════════════════════════════")
print("  5 - Clients les plus actifs")
print("═══════════════════════════════════════")
spark.sql("""
    SELECT Customer,
           COUNT(*) AS Nombre_Achats,
           ROUND(SUM(Total), 2) AS Montant_Total
    FROM sales_delta
    GROUP BY Customer
    ORDER BY Nombre_Achats DESC
    LIMIT 10
""").show(truncate=False)

# COMMAND ----------

# 5.6 - Top 5 des villes
print("═══════════════════════════════════════")
print("  6 - Top 5 des villes par chiffre d'affaires")
print("═══════════════════════════════════════")
spark.sql("""
    SELECT City,
           ROUND(SUM(Total), 2) AS Chiffre_Affaires,
           COUNT(*) AS Nombre_Ventes,
           ROUND(AVG(Total), 2) AS Panier_Moyen
    FROM sales_delta
    GROUP BY City
    ORDER BY Chiffre_Affaires DESC
    LIMIT 5
""").show(truncate=False)

# COMMAND ----------

# 5.7 - Ventes par mois
print("═══════════════════════════════════════")
print("  7 - Ventes par mois")
print("═══════════════════════════════════════")
spark.sql("""
    SELECT DATE_FORMAT(TO_DATE(Date), 'yyyy-MM') AS Mois,
           COUNT(*) AS Nombre_Ventes,
           ROUND(SUM(Total), 2) AS Chiffre_Affaires
    FROM sales_delta
    GROUP BY DATE_FORMAT(TO_DATE(Date), 'yyyy-MM')
    ORDER BY Mois
""").show(truncate=False)

# COMMAND ----------

# 5.8 - Moyenne des prix par catégorie
print("═══════════════════════════════════════")
print("  8 - Moyenne des prix par catégorie")
print("═══════════════════════════════════════")
spark.sql("""
    SELECT Category,
           ROUND(AVG(UnitPrice), 2) AS Prix_Moyen,
           ROUND(MIN(UnitPrice), 2) AS Prix_Minimum,
           ROUND(MAX(UnitPrice), 2) AS Prix_Maximum
    FROM sales_delta
    GROUP BY Category
    ORDER BY Prix_Moyen DESC
""").show(truncate=False)

# COMMAND ----------

# 5.9 - Produit le plus cher
print("═══════════════════════════════════════")
print("  9 - Produit le plus cher")
print("═══════════════════════════════════════")
spark.sql("""
    SELECT Product,
           Category,
           UnitPrice,
           City,
           Customer
    FROM sales_delta
    ORDER BY UnitPrice DESC
    LIMIT 5
""").show(truncate=False)

# COMMAND ----------

# 5.10 - Nombre de ventes par catégorie
print("═══════════════════════════════════════")
print("  10 - Nombre de ventes par catégorie")
print("═══════════════════════════════════════")
spark.sql("""
    SELECT Category,
           COUNT(*) AS Nombre_Ventes,
           ROUND(SUM(Quantity), 0) AS Quantite_Totale,
           ROUND(SUM(Total), 2) AS Chiffre_Affaires
    FROM sales_delta
    GROUP BY Category
    ORDER BY Nombre_Ventes DESC
""").show(truncate=False)

# COMMAND ----------

# Bonus : Ratio chiffre d'affaires par client
print("═══════════════════════════════════════")
print("  Bonus - Répartition du CA par client")
print("═══════════════════════════════════════")
spark.sql("""
    SELECT Customer,
           ROUND(SUM(Total), 2) AS Montant_Total,
           ROUND(SUM(Total) * 100.0 / (SELECT SUM(Total) FROM sales_delta), 2) AS Pourcentage_CA
    FROM sales_delta
    GROUP BY Customer
    ORDER BY Montant_Total DESC
    LIMIT 10
""").show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Partie 6 – Optimisation

# COMMAND ----------

# 6.1 - Commande OPTIMIZE
print("=== Exécution de OPTIMIZE sur la table sales_delta ===")
spark.sql("OPTIMIZE sales_delta")

# COMMAND ----------

# 6.2 - Commande VACUUM
print("=== Exécution de VACUUM sur la table sales_delta ===")
# VACUUM supprime les fichiers marqués pour suppression, en gardant ceux des dernières 24h
spark.sql("VACUUM sales_delta RETAIN 24 HOURS")

# COMMAND ----------

# 6.3 - Explication des commandes OPTIMIZE et VACUUM
print("""
═══════════════════════════════════════════════════════════════════
  Rôle des commandes OPTIMIZE et VACUUM
═══════════════════════════════════════════════════════════════════

1. OPTIMIZE :
   - Compacte les petits fichiers en fichiers plus grands et optimisés
     pour améliorer les performances de lecture.
   - Réorganise les données en utilisant le Z-Ordering (optionnel)
     pour accélérer les filtres sur certaines colonnes.
   - Réduit le nombre de fichiers à scanner lors des requêtes.
   - Améliore significativement les performances des lectures.

2. VACUUM :
   - Supprime physiquement les fichiers de données qui ne sont plus
     référencés par la dernière version de la table (marqués comme
     obsolètes par les opérations UPDATE/DELETE/MERGE).
   - Libère de l'espace disque.
   - Le paramètre RETAIN 24 HOURS permet de garder un historique
     suffisant pour le Time Travel sur les dernières 24 heures.
   - Attention : après VACUUM, on ne peut plus revenir aux versions
     antérieures à la période de rétention spécifiée.

   Différence clé :
   - OPTIMIZE améliore les performances de LECTURE.
   - VACUUM libère de l'espace disque.

   Les deux commandes sont essentielles pour la maintenance
   des tables Delta Lake en production.
═══════════════════════════════════════════════════════════════════
""")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conclusion

# COMMAND ----------

print("""
═══════════════════════════════════════════════════════════════════
  RÉCAPITULATIF DU PROJET
═══════════════════════════════════════════════════════════════════

✅ Partie 1 - Préparation des données
   - Fichier CSV de 105 ventes créé
   - DataFrame chargé avec schéma explicite
   - Colonne Total = UnitPrice × Quantity ajoutée

✅ Partie 2 - Table Delta
   - Table Delta créée
   - Table externe (sales_external) et table gérée (sales_managed)
   - Comparaison des deux types de tables

✅ Partie 3 - Manipulations
   - +10% sur les prix Électronique
   - Suppression des ventes de Lyon
   - Ajout de 5 nouvelles ventes
   - Correction du nom 'Table basse' → 'Table Basse'

✅ Partie 4 - Time Travel
   - Historique des modifications
   - Revenu à la version 0
   - Comparaison ancienne/actuelle

✅ Partie 5 - Analyses Spark SQL
   - 10 requêtes analytiques + bonus

✅ Partie 6 - Optimisation
   - OPTIMIZE : compaction des fichiers
   - VACUUM : nettoyage des fichiers obsolètes
═══════════════════════════════════════════════════════════════════
""")
