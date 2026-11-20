"""
Exercice 4 : Spark SQL - Version Python Natif
Objectif: Utiliser des concepts SQL pour l'analyse (simulés avec Python)
Note: Version compatible Python 3.14 utilisant pandas-like operations
"""
from typing import List, Dict, Any
from collections import defaultdict

print("🔧 Analyse SQL (Python natif) initialisée avec succès!\n")

# Données employés (comme des lignes SQL)
employes_data = [
    {"id": 1, "nom": "Alice", "departement": "IT", "salaire": 5000, "ville": "Paris"},
    {"id": 2, "nom": "Bob", "departement": "Sales", "salaire": 4500, "ville": "Lyon"},
    {"id": 3, "nom": "Charlie", "departement": "IT", "salaire": 5500, "ville": "Paris"},
    {"id": 4, "nom": "Diana", "departement": "HR", "salaire": 4000, "ville": "Marseille"},
    {"id": 5, "nom": "Eve", "departement": "Sales", "salaire": 4800, "ville": "Lyon"}
]

# Données départements
departements_data = [
    {"code": "IT", "nom_complet": "Informatique", "manager": "John"},
    {"code": "Sales", "nom_complet": "Ventes", "manager": "Sarah"},
    {"code": "HR", "nom_complet": "Ressources Humaines", "manager": "Mike"}
]

print("=" * 70)
print("ANALYSE DES EMPLOYÉS AVEC SQL (VERSION PYTHON NATIF)")
print("=" * 70)

# 1. Salaire moyen par département (GROUP BY + AVG)
print("\n1. SALAIRE MOYEN PAR DÉPARTEMENT:")
print("-" * 70)
print("SQL: SELECT departement, AVG(salaire), COUNT(*) GROUP BY departement")
print("-" * 70)

dept_stats = defaultdict(lambda: {'total': 0, 'count': 0})
for emp in employes_data:
    dept_stats[emp['departement']]['total'] += emp['salaire']
    dept_stats[emp['departement']]['count'] += 1

result1 = [
    {
        'departement': dept,
        'salaire_moyen': stats['total'] / stats['count'],
        'nombre_employes': stats['count']
    }
    for dept, stats in dept_stats.items()
]
result1.sort(key=lambda x: x['salaire_moyen'], reverse=True)

print(f"{'Département':<12} {'Salaire Moyen':<15} {'Nb Employés'}")
print("-" * 70)
for r in result1:
    print(f"{r['departement']:<12} {r['salaire_moyen']:>10,.2f}€     {r['nombre_employes']:>3}")

# 2. Nombre d'employés par ville (GROUP BY ville)
print("\n2. NOMBRE D'EMPLOYÉS PAR VILLE:")
print("-" * 70)
print("SQL: SELECT ville, COUNT(*), AVG(salaire) GROUP BY ville")
print("-" * 70)

ville_stats = defaultdict(lambda: {'total': 0, 'count': 0})
for emp in employes_data:
    ville_stats[emp['ville']]['total'] += emp['salaire']
    ville_stats[emp['ville']]['count'] += 1

result2 = [
    {
        'ville': ville,
        'nombre_employes': stats['count'],
        'salaire_moyen': stats['total'] / stats['count']
    }
    for ville, stats in ville_stats.items()
]
result2.sort(key=lambda x: x['nombre_employes'], reverse=True)

print(f"{'Ville':<12} {'Nb Employés':<15} {'Salaire Moyen'}")
print("-" * 70)
for r in result2:
    print(f"{r['ville']:<12} {r['nombre_employes']:>5}           {r['salaire_moyen']:>10,.2f}€")

# 3. Top 3 des salaires (ORDER BY + LIMIT)
print("\n3. TOP 3 DES SALAIRES:")
print("-" * 70)
print("SQL: SELECT * FROM employes ORDER BY salaire DESC LIMIT 3")
print("-" * 70)

result3 = sorted(employes_data, key=lambda x: x['salaire'], reverse=True)[:3]

print(f"{'Nom':<10} {'Département':<12} {'Salaire':<12} {'Ville'}")
print("-" * 70)
for emp in result3:
    print(f"{emp['nom']:<10} {emp['departement']:<12} {emp['salaire']:>8,}€   {emp['ville']}")

# 4. Employés avec salaire > moyenne département (Subquery + JOIN)
print("\n4. EMPLOYÉS AVEC SALAIRE > MOYENNE DE LEUR DÉPARTEMENT:")
print("-" * 70)
print("SQL: SELECT * FROM employes e JOIN (avg per dept) WHERE e.salaire > avg")
print("-" * 70)

# Calculer les moyennes par département
moyennes_dept = {
    dept: stats['total'] / stats['count']
    for dept, stats in dept_stats.items()
}

result4 = [
    {
        'nom': emp['nom'],
        'departement': emp['departement'],
        'salaire': emp['salaire'],
        'moyenne_dept': moyennes_dept[emp['departement']],
        'difference': emp['salaire'] - moyennes_dept[emp['departement']]
    }
    for emp in employes_data
    if emp['salaire'] > moyennes_dept[emp['departement']]
]
result4.sort(key=lambda x: (x['departement'], -x['salaire']))

print(f"{'Nom':<10} {'Département':<12} {'Salaire':<12} {'Moy. Dept':<12} {'Différence'}")
print("-" * 70)
for r in result4:
    print(f"{r['nom']:<10} {r['departement']:<12} {r['salaire']:>8,}€   {r['moyenne_dept']:>8,.2f}€  +{r['difference']:>6,.2f}€")

# 5. Jointure avec table départements (JOIN)
print("\n5. JOINTURE EMPLOYÉS - DÉPARTEMENTS:")
print("-" * 70)
print("SQL: SELECT e.*, d.* FROM employes e JOIN departements d")
print("     ON e.departement = d.code WHERE e.salaire > 4500")
print("-" * 70)

# Créer un dictionnaire pour accès rapide aux départements
dept_dict = {d['code']: d for d in departements_data}

result5 = []
for emp in employes_data:
    if emp['salaire'] > 4500:
        dept = dept_dict.get(emp['departement'])
        if dept:
            result5.append({
                'employe': emp['nom'],
                'nom_complet': dept['nom_complet'],
                'manager': dept['manager'],
                'salaire': emp['salaire'],
                'ville': emp['ville']
            })

result5.sort(key=lambda x: x['salaire'], reverse=True)

print(f"{'Employé':<10} {'Département':<20} {'Manager':<10} {'Salaire':<12} {'Ville'}")
print("-" * 70)
for r in result5:
    print(f"{r['employe']:<10} {r['nom_complet']:<20} {r['manager']:<10} {r['salaire']:>8,}€   {r['ville']}")

# BONUS: Analyses supplémentaires
print("\n" + "=" * 70)
print("ANALYSES SUPPLÉMENTAIRES")
print("=" * 70)

# 6. Statistiques complètes par département (MIN, MAX, AVG, COUNT)
print("\n6. STATISTIQUES COMPLÈTES PAR DÉPARTEMENT:")
print("-" * 70)
print("SQL: SELECT dept, COUNT(*), MIN(sal), MAX(sal), AVG(sal) GROUP BY dept")
print("-" * 70)

dept_full_stats = defaultdict(lambda: {'salaires': []})
for emp in employes_data:
    dept_full_stats[emp['departement']]['salaires'].append(emp['salaire'])

result6 = []
for dept, stats in dept_full_stats.items():
    salaires = stats['salaires']
    result6.append({
        'departement': dept,
        'nb_employes': len(salaires),
        'salaire_min': min(salaires),
        'salaire_max': max(salaires),
        'salaire_moyen': sum(salaires) / len(salaires),
        'ecart': max(salaires) - min(salaires)
    })

result6.sort(key=lambda x: x['nb_employes'], reverse=True)

print(f"{'Dept':<8} {'Nb':<5} {'Min':<10} {'Max':<10} {'Moyenne':<12} {'Écart'}")
print("-" * 70)
for r in result6:
    print(f"{r['departement']:<8} {r['nb_employes']:<5} {r['salaire_min']:>7,}€  {r['salaire_max']:>7,}€  {r['salaire_moyen']:>8,.2f}€   {r['ecart']:>6,}€")

# 7. Liste complète avec niveau (CASE WHEN)
print("\n7. LISTE COMPLÈTE AVEC NIVEAUX (CASE WHEN):")
print("-" * 70)
print("SQL: CASE WHEN salaire >= 5000 THEN 'Senior' ...")
print("-" * 70)

result7 = []
for emp in employes_data:
    dept = dept_dict.get(emp['departement'])
    if emp['salaire'] >= 5000:
        niveau = "Senior"
    elif emp['salaire'] >= 4500:
        niveau = "Intermédiaire"
    else:
        niveau = "Junior"
    
    result7.append({
        'id': emp['id'],
        'employe': emp['nom'],
        'ville': emp['ville'],
        'departement': dept['nom_complet'] if dept else emp['departement'],
        'manager': dept['manager'] if dept else 'N/A',
        'salaire': emp['salaire'],
        'niveau': niveau
    })

result7.sort(key=lambda x: x['salaire'], reverse=True)

print(f"{'ID':<4} {'Employé':<10} {'Département':<20} {'Manager':<8} {'Salaire':<12} {'Niveau'}")
print("-" * 70)
for r in result7:
    print(f"{r['id']:<4} {r['employe']:<10} {r['departement']:<20} {r['manager']:<8} {r['salaire']:>8,}€   {r['niveau']}")

# 8. Masse salariale par département (SUM + GROUP BY)
print("\n8. MASSE SALARIALE PAR DÉPARTEMENT:")
print("-" * 70)
print("SQL: SELECT d.*, SUM(e.salaire) FROM dept d LEFT JOIN emp e GROUP BY d")
print("-" * 70)

masse_par_dept = defaultdict(lambda: {'total': 0, 'count': 0})
for emp in employes_data:
    masse_par_dept[emp['departement']]['total'] += emp['salaire']
    masse_par_dept[emp['departement']]['count'] += 1

result8 = []
for dept_info in departements_data:
    code = dept_info['code']
    stats = masse_par_dept[code]
    result8.append({
        'departement': dept_info['nom_complet'],
        'manager': dept_info['manager'],
        'nb_employes': stats['count'],
        'masse_salariale': stats['total'],
        'salaire_moyen': stats['total'] / stats['count'] if stats['count'] > 0 else 0
    })

result8.sort(key=lambda x: x['masse_salariale'], reverse=True)

print(f"{'Département':<20} {'Manager':<10} {'Nb':<5} {'Masse Sal.':<15} {'Moy.'}")
print("-" * 70)
for r in result8:
    print(f"{r['departement']:<20} {r['manager']:<10} {r['nb_employes']:<5} {r['masse_salariale']:>11,}€    {r['salaire_moyen']:>8,.2f}€")

# Résumé final
print("\n" + "=" * 70)
print("RÉSUMÉ GÉNÉRAL")
print("=" * 70)

total_employes = len(employes_data)
salaire_total = sum(emp['salaire'] for emp in employes_data)
salaire_moyen = salaire_total / total_employes
salaire_min = min(emp['salaire'] for emp in employes_data)
salaire_max = max(emp['salaire'] for emp in employes_data)

print(f"Nombre total d'employés      : {total_employes}")
print(f"Masse salariale totale       : {salaire_total:,}€")
print(f"Salaire moyen                : {salaire_moyen:,.2f}€")
print(f"Salaire minimum              : {salaire_min:,}€")
print(f"Salaire maximum              : {salaire_max:,}€")
print(f"Écart salarial               : {salaire_max - salaire_min:,}€")
print(f"Nombre de départements       : {len(departements_data)}")
print(f"Nombre de villes             : {len(ville_stats)}")

print("\n✅ Exercice SQL (Python natif) terminé avec succès!")
print("\n📝 Note: Cette version simule SQL avec Python. Pour Spark SQL réel,")
print("   voir exercise4.py (nécessite Python ≤ 3.12)")
