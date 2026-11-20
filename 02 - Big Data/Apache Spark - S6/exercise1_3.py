"""
Exercice 3 : Analyse de ventes
Objectif: Analyser des données de ventes avec RDD
"""
import os
import sys

# Configuration pour Windows - Indiquer à Spark où trouver Python
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

from pyspark.sql import SparkSession

# Configuration de Spark pour Windows avec Python 3.14
spark = SparkSession.builder \
    .appName("Ventes-RDD") \
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

# Données de ventes : (ville, produit, quantité, prix)
ventes = [
    ("Paris", "Laptop", 5, 1200),
    ("Lyon", "Smartphone", 10, 800),
    ("Paris", "Tablette", 3, 500),
    ("Marseille", "Laptop", 2, 1200),
    ("Lyon", "Laptop", 4, 1200),
    ("Paris", "Smartphone", 8, 800),
    ("Toulouse", "Tablette", 6, 500)
]

rdd_ventes = sc.parallelize(ventes)

# 1. Chiffre d'affaires total
def calcul_ca(vente):
    """Calcule le CA pour une vente : quantité * prix"""
    ville, produit, quantite, prix = vente
    return quantite * prix

rdd_ca = rdd_ventes.map(calcul_ca)
ca_total = rdd_ca.reduce(lambda a, b: a + b)
print(f"\n1. CA total: {ca_total}€")

# 2. CA par ville
print("\n2. CA par ville:")
rdd_ca_par_ville = rdd_ventes.map(lambda v: (v[0], v[2] * v[3]))  # (ville, CA)
ca_par_ville = rdd_ca_par_ville.reduceByKey(lambda a, b: a + b)
for ville, ca in ca_par_ville.collect():
    print(f"   {ville}: {ca}€")

# 3. Produit le plus vendu (quantité)
print("\n3. Produit le plus vendu (quantité):")
rdd_quantite_par_produit = rdd_ventes.map(lambda v: (v[1], v[2]))  # (produit, quantité)
quantite_par_produit = rdd_quantite_par_produit.reduceByKey(lambda a, b: a + b)
produit_plus_vendu = quantite_par_produit.reduce(lambda a, b: a if a[1] > b[1] else b)
print(f"   {produit_plus_vendu[0]}: {produit_plus_vendu[1]} unités vendues")

# 4. Ville avec le plus haut panier moyen
print("\n4. Ville avec le plus haut panier moyen:")
# Calculer le CA et le nombre de ventes par ville
rdd_ville_ca_count = rdd_ventes.map(lambda v: (v[0], (v[2] * v[3], 1)))  # (ville, (CA, count))
ville_ca_count = rdd_ville_ca_count.reduceByKey(lambda a, b: (a[0] + b[0], a[1] + b[1]))
# Calculer le panier moyen
panier_moyen_par_ville = ville_ca_count.map(lambda v: (v[0], v[1][0] / v[1][1]))
ville_meilleur_panier = panier_moyen_par_ville.reduce(lambda a, b: a if a[1] > b[1] else b)
print(f"   {ville_meilleur_panier[0]}: {ville_meilleur_panier[1]:.2f}€ de panier moyen")

# 5. Filtrer les ventes > 5000€
print("\n5. Ventes avec CA > 5000€:")
ventes_importantes = rdd_ventes.filter(lambda v: v[2] * v[3] > 5000)
for vente in ventes_importantes.collect():
    ville, produit, quantite, prix = vente
    ca = quantite * prix
    print(f"   {ville} - {produit}: {quantite} x {prix}€ = {ca}€")

# Afficher un résumé général
print("\n" + "="*50)
print("RÉSUMÉ GÉNÉRAL")
print("="*50)
print(f"Nombre total de transactions: {rdd_ventes.count()}")
print(f"CA total: {ca_total}€")
print(f"CA moyen par transaction: {ca_total / rdd_ventes.count():.2f}€")

spark.stop()
