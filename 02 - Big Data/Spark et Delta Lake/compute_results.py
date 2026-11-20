import csv
from collections import defaultdict

rows = list(csv.DictReader(open('D:/M2/AWS/Azure/sales_delta_results.csv','r',encoding='utf-8')))

for r in rows:
    r['Total'] = float(r['Total'])
    r['UnitPrice'] = float(r['UnitPrice'])
    r['Quantity'] = int(r['Quantity'])

# 1 - CA total
ca_total = sum(r['Total'] for r in rows)
print(f"CA_TOTAL|{ca_total:.2f}")

# 2 - CA par ville
ca_ville = defaultdict(float)
nv_ville = defaultdict(int)
for r in rows:
    ca_ville[r['City']] += r['Total']
    nv_ville[r['City']] += 1
print("CA_VILLE|" + "|".join(f"{v}|{ca_ville[v]:.2f}|{nv_ville[v]}" for v in sorted(ca_ville, key=lambda x: ca_ville[x], reverse=True)))

# 3 - CA par catégorie
ca_cat = defaultdict(float)
nv_cat = defaultdict(int)
for r in rows:
    ca_cat[r['Category']] += r['Total']
    nv_cat[r['Category']] += 1
print("CA_CAT|" + "|".join(f"{c}|{ca_cat[c]:.2f}|{nv_cat[c]}" for c in sorted(ca_cat, key=lambda x: ca_cat[x], reverse=True)))

# 4 - Produit le plus vendu
qte_prod = defaultdict(int)
ca_prod = defaultdict(float)
for r in rows:
    qte_prod[r['Product']] += r['Quantity']
    ca_prod[r['Product']] += r['Total']
print("TOP_PROD|" + "|".join(f"{p}|{qte_prod[p]}|{ca_prod[p]:.2f}" for p in sorted(qte_prod, key=lambda x: qte_prod[x], reverse=True)[:5]))

# 5 - Client le plus actif
achats_client = defaultdict(int)
montant_client = defaultdict(float)
for r in rows:
    achats_client[r['Customer']] += 1
    montant_client[r['Customer']] += r['Total']
print("TOP_CLIENT|" + "|".join(f"{c}|{achats_client[c]}|{montant_client[c]:.2f}" for c in sorted(achats_client, key=lambda x: achats_client[x], reverse=True)[:5]))

# 6 - Ventes par mois
mois_data = defaultdict(lambda: {'n':0, 'ca':0.0})
for r in rows:
    m = r['Date'][:7]
    mois_data[m]['n'] += 1
    mois_data[m]['ca'] += r['Total']
print("MOIS|" + "|".join(f"{m}|{mois_data[m]['n']}|{mois_data[m]['ca']:.2f}" for m in sorted(mois_data)))

# 7 - Prix moyen par catégorie
from statistics import mean
prix_cat = defaultdict(list)
for r in rows:
    prix_cat[r['Category']].append(r['UnitPrice'])
print("PRIX_CAT|" + "|".join(f"{c}|{mean(prix_cat[c]):.2f}|{min(prix_cat[c]):.2f}|{max(prix_cat[c]):.2f}" for c in sorted(prix_cat, key=lambda x: mean(prix_cat[x]), reverse=True)))

# 8 - Top 5 villes
print("TOP_VILLE|" + "|".join(f"{v}|{ca_ville[v]:.2f}|{nv_ville[v]}" for v in sorted(ca_ville, key=lambda x: ca_ville[x], reverse=True)[:5]))

# 9 - Produit le plus cher
prods = sorted(rows, key=lambda x: x['UnitPrice'], reverse=True)[:5]
print("CHER|" + "|".join(f"{p['Product']}|{p['UnitPrice']:.2f}|{p['Category']}" for p in prods))

# 10 - Ventes par catégorie
qte_cat = defaultdict(int)
for r in rows:
    qte_cat[r['Category']] += r['Quantity']
print("VENTES_CAT|" + "|".join(f"{c}|{nv_cat[c]}|{qte_cat[c]}|{ca_cat[c]:.2f}" for c in sorted(nv_cat, key=lambda x: nv_cat[x], reverse=True)))

# 11 - Total ventes
print(f"NB_VENTES|{len(rows)}")

# 12 - Panier moyen par ville
for v in sorted(ca_ville, key=lambda x: ca_ville[x], reverse=True)[:5]:
    panier = ca_ville[v] / nv_ville[v]
    print(f"PANIER|{v}|{panier:.2f}")
