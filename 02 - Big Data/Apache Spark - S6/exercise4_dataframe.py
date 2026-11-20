"""
Exercice 4 : Spark SQL - Version API DataFrame
Objectif: Utiliser Spark SQL et l'API DataFrame pour l'analyse
Note: Version utilisant l'API DataFrame qui fonctionne mieux avec Python 3.14
"""
import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, count, sum as spark_sum, min as spark_min, max as spark_max, round as spark_round, col, when

# Configuration pour Windows - Indiquer à Spark où trouver Python
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

# Configuration de Spark pour Windows avec Python 3.14
spark = SparkSession.builder \
    .appName("TP2-SQL-DataFrame") \
    .master("local[1]") \
    .config("spark.python.worker.reuse", "false") \
    .config("spark.executor.instances", "1") \
    .config("spark.sql.execution.arrow.pyspark.enabled", "false") \
    .config("spark.python.use.daemon", "false") \
    .config("spark.ui.enabled", "false") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

print("🔧 Spark SQL (API DataFrame) initialisé avec succès!\n")

# Données employés
employes_data = [
    (1, "Alice", "IT", 5000, "Paris"),
    (2, "Bob", "Sales", 4500, "Lyon"),
    (3, "Charlie", "IT", 5500, "Paris"),
    (4, "Diana", "HR", 4000, "Marseille"),
    (5, "Eve", "Sales", 4800, "Lyon")
]

employes_df = spark.createDataFrame(
    employes_data, 
    ["id", "nom", "departement", "salaire", "ville"]
)

print("=" * 60)
print("ANALYSE DES EMPLOYÉS AVEC SPARK SQL (API DataFrame)")
print("=" * 60)

# 1. Salaire moyen par département
print("\n1. SALAIRE MOYEN PAR DÉPARTEMENT:")
print("-" * 60)
result1 = employes_df.groupBy("departement") \
    .agg(
        spark_round(avg("salaire"), 2).alias("salaire_moyen"),
        count("*").alias("nombre_employes")
    ) \
    .orderBy(col("salaire_moyen").desc())

result1.show()

# 2. Nombre d'employés par ville
print("\n2. NOMBRE D'EMPLOYÉS PAR VILLE:")
print("-" * 60)
result2 = employes_df.groupBy("ville") \
    .agg(
        count("*").alias("nombre_employes"),
        spark_round(avg("salaire"), 2).alias("salaire_moyen")
    ) \
    .orderBy(col("nombre_employes").desc())

result2.show()

# 3. Top 3 des salaires
print("\n3. TOP 3 DES SALAIRES:")
print("-" * 60)
result3 = employes_df.select("nom", "departement", "salaire", "ville") \
    .orderBy(col("salaire").desc()) \
    .limit(3)

result3.show()

# 4. Employés avec salaire > moyenne département
print("\n4. EMPLOYÉS AVEC SALAIRE > MOYENNE DE LEUR DÉPARTEMENT:")
print("-" * 60)

# Calculer la moyenne par département
avg_par_dept = employes_df.groupBy("departement") \
    .agg(avg("salaire").alias("salaire_moyen"))

# Joindre avec les employés
result4 = employes_df.join(avg_par_dept, "departement") \
    .where(col("salaire") > col("salaire_moyen")) \
    .select(
        "nom",
        "departement",
        "salaire",
        spark_round("salaire_moyen", 2).alias("moyenne_dept"),
        spark_round(col("salaire") - col("salaire_moyen"), 2).alias("difference")
    ) \
    .orderBy("departement", col("salaire").desc())

result4.show()

# 5. Jointure avec table départements
print("\n5. JOINTURE EMPLOYÉS - DÉPARTEMENTS:")
print("-" * 60)

departements_data = [
    ("IT", "Informatique", "John"),
    ("Sales", "Ventes", "Sarah"),
    ("HR", "Ressources Humaines", "Mike")
]

departements_df = spark.createDataFrame(
    departements_data,
    ["code", "nom_complet", "manager"]
)

# Jointure - Employés avec salaire > 4500
print("   a) Employés avec salaire > 4500€:")
result5 = employes_df.join(
    departements_df,
    employes_df.departement == departements_df.code
) \
    .where(col("salaire") > 4500) \
    .select(
        col("nom").alias("employe"),
        "nom_complet",
        "manager",
        "salaire",
        "ville"
    ) \
    .orderBy(col("salaire").desc())

result5.show()

# BONUS: Analyses supplémentaires
print("\n" + "=" * 60)
print("ANALYSES SUPPLÉMENTAIRES")
print("=" * 60)

# 6. Statistiques par département
print("\n6. STATISTIQUES COMPLÈTES PAR DÉPARTEMENT:")
print("-" * 60)
result6 = employes_df.groupBy("departement") \
    .agg(
        count("*").alias("nb_employes"),
        spark_min("salaire").alias("salaire_min"),
        spark_max("salaire").alias("salaire_max"),
        spark_round(avg("salaire"), 2).alias("salaire_moyen"),
        (spark_max("salaire") - spark_min("salaire")).alias("ecart_salaire")
    ) \
    .orderBy(col("nb_employes").desc())

result6.show()

# 7. Liste complète avec détails et niveau
print("\n7. LISTE COMPLÈTE DES EMPLOYÉS AVEC DÉTAILS:")
print("-" * 60)
result7 = employes_df.join(
    departements_df,
    employes_df.departement == departements_df.code
) \
    .select(
        "id",
        col("nom").alias("employe"),
        "ville",
        col("nom_complet").alias("departement"),
        "manager",
        "salaire",
        when(col("salaire") >= 5000, "Senior")
        .when(col("salaire") >= 4500, "Intermédiaire")
        .otherwise("Junior")
        .alias("niveau")
    ) \
    .orderBy(col("salaire").desc())

result7.show()

# 8. Masse salariale par département
print("\n8. MASSE SALARIALE PAR DÉPARTEMENT:")
print("-" * 60)
result8 = departements_df.join(
    employes_df,
    departements_df.code == employes_df.departement,
    "left"
) \
    .groupBy("nom_complet", "manager") \
    .agg(
        count("id").alias("nb_employes"),
        spark_sum("salaire").alias("masse_salariale"),
        spark_round(avg("salaire"), 2).alias("salaire_moyen")
    ) \
    .orderBy(col("masse_salariale").desc())

result8.show()

# Résumé final
print("\n" + "=" * 60)
print("RÉSUMÉ GÉNÉRAL")
print("=" * 60)

total_employes = employes_df.count()
stats = employes_df.agg(
    spark_sum("salaire").alias("total"),
    avg("salaire").alias("moyenne"),
    spark_min("salaire").alias("minimum"),
    spark_max("salaire").alias("maximum")
).collect()[0]

salaire_total = stats["total"]
salaire_moyen = stats["moyenne"]
salaire_min = stats["minimum"]
salaire_max = stats["maximum"]

print(f"Nombre total d'employés      : {total_employes}")
print(f"Masse salariale totale       : {salaire_total:,}€")
print(f"Salaire moyen                : {salaire_moyen:,.2f}€")
print(f"Salaire minimum              : {salaire_min:,}€")
print(f"Salaire maximum              : {salaire_max:,}€")
print(f"Écart salarial               : {salaire_max - salaire_min:,}€")

print("\n✅ Exercice Spark SQL (API DataFrame) terminé avec succès!")

spark.stop()
