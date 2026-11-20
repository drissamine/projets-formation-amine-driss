"""
Exercice 4 : Spark SQL
Objectif: Utiliser Spark SQL pour l'analyse
"""
import os
import sys
from pyspark.sql import SparkSession

# Configuration pour Windows - Indiquer à Spark où trouver Python
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

# Configuration de Spark pour Windows avec Python 3.14
spark = SparkSession.builder \
    .appName("TP2-SQL") \
    .master("local[1]") \
    .config("spark.python.worker.reuse", "false") \
    .config("spark.executor.instances", "1") \
    .config("spark.sql.execution.arrow.pyspark.enabled", "false") \
    .config("spark.python.use.daemon", "false") \
    .config("spark.ui.enabled", "false") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")  # Réduire les logs

print("🔧 Spark SQL initialisé avec succès!\n")

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

# Créer une vue
employes_df.createOrReplaceTempView("employes")

print("=" * 60)
print("ANALYSE DES EMPLOYÉS AVEC SPARK SQL")
print("=" * 60)

# 1. Salaire moyen par département
print("\n1. SALAIRE MOYEN PAR DÉPARTEMENT:")
print("-" * 60)
query1 = """
SELECT departement, 
       AVG(salaire) as salaire_moyen,
       COUNT(*) as nombre_employes
FROM employes
GROUP BY departement
ORDER BY salaire_moyen DESC
"""
spark.sql(query1).show()

# 2. Nombre d'employés par ville
print("\n2. NOMBRE D'EMPLOYÉS PAR VILLE:")
print("-" * 60)
query2 = """
SELECT ville, 
       COUNT(*) as nombre_employes,
       AVG(salaire) as salaire_moyen
FROM employes
GROUP BY ville
ORDER BY nombre_employes DESC
"""
spark.sql(query2).show()

# 3. Top 3 des salaires
print("\n3. TOP 3 DES SALAIRES:")
print("-" * 60)
query3 = """
SELECT nom, 
       departement, 
       salaire,
       ville
FROM employes
ORDER BY salaire DESC
LIMIT 3
"""
spark.sql(query3).show()

# 4. Employés avec salaire > moyenne département
print("\n4. EMPLOYÉS AVEC SALAIRE > MOYENNE DE LEUR DÉPARTEMENT:")
print("-" * 60)
query4 = """
SELECT e.nom, 
       e.departement, 
       e.salaire,
       ROUND(avg_dept.salaire_moyen, 2) as moyenne_dept,
       ROUND(e.salaire - avg_dept.salaire_moyen, 2) as difference
FROM employes e
JOIN (
    SELECT departement, AVG(salaire) as salaire_moyen
    FROM employes
    GROUP BY departement
) avg_dept ON e.departement = avg_dept.departement
WHERE e.salaire > avg_dept.salaire_moyen
ORDER BY e.departement, e.salaire DESC
"""
spark.sql(query4).show()

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

# Créer la vue
departements_df.createOrReplaceTempView("departements")

# Jointure SQL - Employés avec salaire > 4500
print("   a) Employés avec salaire > 4500€:")
query_jointure = """
SELECT e.nom as employe, 
       d.nom_complet as departement, 
       d.manager,
       e.salaire,
       e.ville
FROM employes e
JOIN departements d ON e.departement = d.code
WHERE e.salaire > 4500
ORDER BY e.salaire DESC
"""
spark.sql(query_jointure).show()

# BONUS: Quelques requêtes supplémentaires
print("\n" + "=" * 60)
print("ANALYSES SUPPLÉMENTAIRES")
print("=" * 60)

# 6. Statistiques par département (min, max, moyenne)
print("\n6. STATISTIQUES COMPLÈTES PAR DÉPARTEMENT:")
print("-" * 60)
query6 = """
SELECT departement,
       COUNT(*) as nb_employes,
       MIN(salaire) as salaire_min,
       MAX(salaire) as salaire_max,
       ROUND(AVG(salaire), 2) as salaire_moyen,
       ROUND(MAX(salaire) - MIN(salaire), 2) as ecart_salaire
FROM employes
GROUP BY departement
ORDER BY nb_employes DESC
"""
spark.sql(query6).show()

# 7. Liste complète avec détails département
print("\n7. LISTE COMPLÈTE DES EMPLOYÉS AVEC DÉTAILS:")
print("-" * 60)
query7 = """
SELECT e.id,
       e.nom as employe,
       e.ville,
       d.nom_complet as departement,
       d.manager,
       e.salaire,
       CASE 
           WHEN e.salaire >= 5000 THEN 'Senior'
           WHEN e.salaire >= 4500 THEN 'Intermédiaire'
           ELSE 'Junior'
       END as niveau
FROM employes e
JOIN departements d ON e.departement = d.code
ORDER BY e.salaire DESC
"""
spark.sql(query7).show()

# 8. Masse salariale par département et manager
print("\n8. MASSE SALARIALE PAR DÉPARTEMENT:")
print("-" * 60)
query8 = """
SELECT d.nom_complet as departement,
       d.manager,
       COUNT(e.id) as nb_employes,
       SUM(e.salaire) as masse_salariale,
       ROUND(AVG(e.salaire), 2) as salaire_moyen
FROM departements d
LEFT JOIN employes e ON d.code = e.departement
GROUP BY d.nom_complet, d.manager
ORDER BY masse_salariale DESC
"""
spark.sql(query8).show()

# Résumé final
print("\n" + "=" * 60)
print("RÉSUMÉ GÉNÉRAL")
print("=" * 60)

# Utiliser l'API DataFrame pour le résumé
total_employes = employes_df.count()
salaire_total = employes_df.agg({"salaire": "sum"}).collect()[0][0]
salaire_moyen = employes_df.agg({"salaire": "avg"}).collect()[0][0]
salaire_min = employes_df.agg({"salaire": "min"}).collect()[0][0]
salaire_max = employes_df.agg({"salaire": "max"}).collect()[0][0]

print(f"Nombre total d'employés      : {total_employes}")
print(f"Masse salariale totale       : {salaire_total:,}€")
print(f"Salaire moyen                : {salaire_moyen:,.2f}€")
print(f"Salaire minimum              : {salaire_min:,}€")
print(f"Salaire maximum              : {salaire_max:,}€")
print(f"Écart salarial               : {salaire_max - salaire_min:,}€")

print("\n✅ Exercice Spark SQL terminé avec succès!")

spark.stop()
