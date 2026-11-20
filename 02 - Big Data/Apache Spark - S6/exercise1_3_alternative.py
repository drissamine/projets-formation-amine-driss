"""
Exercice 3 : Analyse de ventes - Version Alternative
Objectif: Analyser des données de ventes
Note: Version utilisant Python natif en raison de problèmes de compatibilité PySpark/Python 3.14
      Cette version démontre la même logique que le code RDD attendu.
"""

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

print("=" * 60)
print("ANALYSE DES VENTES")
print("=" * 60)

# 1. Chiffre d'affaires total
def calcul_ca(vente):
    """Calcule le CA pour une vente : quantité * prix"""
    ville, produit, quantite, prix = vente
    return quantite * prix

# Équivalent de: rdd.map(calcul_ca).reduce(lambda a, b: a + b)
ca_total = sum(calcul_ca(vente) for vente in ventes)
print(f"\n1. CA TOTAL: {ca_total:,}€")

# 2. CA par ville
print("\n2. CA PAR VILLE:")
ca_par_ville = {}
# Équivalent de: rdd.map(lambda v: (v[0], v[2] * v[3])).reduceByKey(lambda a, b: a + b)
for ville, produit, quantite, prix in ventes:
    ca = quantite * prix
    ca_par_ville[ville] = ca_par_ville.get(ville, 0) + ca

for ville, ca in sorted(ca_par_ville.items(), key=lambda x: x[1], reverse=True):
    print(f"   {ville:12} : {ca:6,}€")

# 3. Produit le plus vendu (quantité)
print("\n3. PRODUIT LE PLUS VENDU (quantité):")
quantite_par_produit = {}
# Équivalent de: rdd.map(lambda v: (v[1], v[2])).reduceByKey(lambda a, b: a + b)
for ville, produit, quantite, prix in ventes:
    quantite_par_produit[produit] = quantite_par_produit.get(produit, 0) + quantite

# Équivalent de: reduce(lambda a, b: a if a[1] > b[1] else b)
produit_plus_vendu = max(quantite_par_produit.items(), key=lambda x: x[1])
print(f"   🏆 {produit_plus_vendu[0]} : {produit_plus_vendu[1]} unités vendues")

print("\n   Détail par produit:")
for produit, quantite in sorted(quantite_par_produit.items(), key=lambda x: x[1], reverse=True):
    print(f"      {produit:12} : {quantite:2} unités")

# 4. Ville avec le plus haut panier moyen
print("\n4. VILLE AVEC LE PLUS HAUT PANIER MOYEN:")
ville_stats = {}
# Équivalent de: rdd.map(lambda v: (v[0], (v[2] * v[3], 1))).reduceByKey(...)
for ville, produit, quantite, prix in ventes:
    ca = quantite * prix
    if ville not in ville_stats:
        ville_stats[ville] = {'ca_total': 0, 'nb_ventes': 0}
    ville_stats[ville]['ca_total'] += ca
    ville_stats[ville]['nb_ventes'] += 1

# Équivalent de: map(lambda v: (v[0], v[1][0] / v[1][1]))
panier_moyen = {ville: stats['ca_total'] / stats['nb_ventes'] 
                for ville, stats in ville_stats.items()}

# Équivalent de: reduce(lambda a, b: a if a[1] > b[1] else b)
ville_meilleur_panier = max(panier_moyen.items(), key=lambda x: x[1])
print(f"   🏆 {ville_meilleur_panier[0]} : {ville_meilleur_panier[1]:,.2f}€ de panier moyen")

print("\n   Détail par ville:")
for ville, panier in sorted(panier_moyen.items(), key=lambda x: x[1], reverse=True):
    nb_ventes = ville_stats[ville]['nb_ventes']
    print(f"      {ville:12} : {panier:8,.2f}€ ({nb_ventes} vente{'s' if nb_ventes > 1 else ''})")

# 5. Filtrer les ventes > 5000€
print("\n5. VENTES AVEC CA > 5000€:")
# Équivalent de: rdd.filter(lambda v: v[2] * v[3] > 5000)
ventes_importantes = [v for v in ventes if v[2] * v[3] > 5000]
if ventes_importantes:
    for ville, produit, quantite, prix in ventes_importantes:
        ca = quantite * prix
        print(f"   💰 {ville:12} - {produit:12} : {quantite} x {prix:,}€ = {ca:,}€")
else:
    print("   Aucune vente supérieure à 5000€")

# Afficher un résumé général
print("\n" + "=" * 60)
print("RÉSUMÉ GÉNÉRAL")
print("=" * 60)
print(f"Nombre total de transactions : {len(ventes)}")
print(f"CA total                     : {ca_total:,}€")
print(f"CA moyen par transaction     : {ca_total / len(ventes):,.2f}€")
print(f"Nombre de villes             : {len(ca_par_ville)}")
print(f"Nombre de produits           : {len(quantite_par_produit)}")
print(f"Vente minimum                : {min(calcul_ca(v) for v in ventes):,}€")
print(f"Vente maximum                : {max(calcul_ca(v) for v in ventes):,}€")

print("\n✅ Exercice terminé avec succès!")
print("\n📝 Note: Cette version utilise Python natif. Pour la version RDD,")
print("   voir exercise1_3.py (nécessite Python ≤ 3.12)")
