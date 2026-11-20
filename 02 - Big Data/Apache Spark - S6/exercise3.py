"""
Exercice 3 : Analyse de ventes - Version Alternative (sans RDD)
Objectif: Analyser des données de ventes
Note: Version utilisant Python natif en raison de problèmes de compatibilité PySpark/Python 3.14
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

# 1. Chiffre d'affaires total
def calcul_ca(vente):
    """Calcule le CA pour une vente : quantité * prix"""
    ville, produit, quantite, prix = vente
    return quantite * prix

ca_total = sum(calcul_ca(vente) for vente in ventes)
print(f"\n1. CA total: {ca_total}€")

# 2. CA par ville
print("\n2. CA par ville:")
ca_par_ville = {}
for ville, produit, quantite, prix in ventes:
    ca = quantite * prix
    ca_par_ville[ville] = ca_par_ville.get(ville, 0) + ca

for ville, ca in sorted(ca_par_ville.items()):
    print(f"   {ville}: {ca}€")

# 3. Produit le plus vendu (quantité)
print("\n3. Produit le plus vendu (quantité):")
quantite_par_produit = {}
for ville, produit, quantite, prix in ventes:
    quantite_par_produit[produit] = quantite_par_produit.get(produit, 0) + quantite

produit_plus_vendu = max(quantite_par_produit.items(), key=lambda x: x[1])
print(f"   {produit_plus_vendu[0]}: {produit_plus_vendu[1]} unités vendues")

# 4. Ville avec le plus haut panier moyen
print("\n4. Ville avec le plus haut panier moyen:")
ville_stats = {}
for ville, produit, quantite, prix in ventes:
    ca = quantite * prix
    if ville not in ville_stats:
        ville_stats[ville] = {'ca_total': 0, 'nb_ventes': 0}
    ville_stats[ville]['ca_total'] += ca
    ville_stats[ville]['nb_ventes'] += 1

panier_moyen = {ville: stats['ca_total'] / stats['nb_ventes'] 
                for ville, stats in ville_stats.items()}
ville_meilleur_panier = max(panier_moyen.items(), key=lambda x: x[1])
print(f"   {ville_meilleur_panier[0]}: {ville_meilleur_panier[1]:.2f}€ de panier moyen")

# 5. Filtrer les ventes > 5000€
print("\n5. Ventes avec CA > 5000€:")
ventes_importantes = [v for v in ventes if v[2] * v[3] > 5000]
for ville, produit, quantite, prix in ventes_importantes:
    ca = quantite * prix
    print(f"   {ville} - {produit}: {quantite} x {prix}€ = {ca}€")

# Afficher un résumé général
print("\n" + "="*50)
print("RÉSUMÉ GÉNÉRAL")
print("="*50)
print(f"Nombre total de transactions: {len(ventes)}")
print(f"CA total: {ca_total}€")
print(f"CA moyen par transaction: {ca_total / len(ventes):.2f}€")

print("\n✅ Exercice terminé avec succès!")
