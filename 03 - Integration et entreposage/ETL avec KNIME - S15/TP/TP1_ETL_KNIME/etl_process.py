import pandas as pd
import os

# Define file paths
base_dir = r"d:/M2/s15/TP/TP1_ETL_KNIME"
ventes_path = os.path.join(base_dir, "ventes.csv")
clients_path = os.path.join(base_dir, "clients.csv")
produits_path = os.path.join(base_dir, "produits.csv")
output_path = os.path.join(base_dir, "ventes_analytiques.csv")

print("Step 1: Extraction (Loading Data)...")
try:
    df_ventes = pd.read_csv(ventes_path)
    df_clients = pd.read_csv(clients_path)
    df_produits = pd.read_csv(produits_path)
    print(f"Loaded ventes: {df_ventes.shape}")
    print(f"Loaded clients: {df_clients.shape}")
    print(f"Loaded produits: {df_produits.shape}")
    print(f"Produits columns: {df_produits.columns.tolist()}")
    
    # Strip whitespace from column names
    df_ventes.columns = df_ventes.columns.str.strip()
    df_clients.columns = df_clients.columns.str.strip()
    df_produits.columns = df_produits.columns.str.strip()
except Exception as e:
    print(f"Error loading files: {e}")
    exit(1)

print("\nStep 2: Cleaning (Nettoyage)...")
# 2.1 Date Conversion
# Assuming date_vente is YYYY-MM-DD
df_ventes['date_vente'] = pd.to_datetime(df_ventes['date_vente'])

# 2.2 Missing Values
# Fill missing quantities with 1
df_ventes['quantite'] = df_ventes['quantite'].fillna(1)

# Drop rows where client_id or produit_id is missing
df_ventes = df_ventes.dropna(subset=['client_id', 'produit_id'])

# Ensure IDs are integers for joining
df_ventes['client_id'] = df_ventes['client_id'].astype(int)
df_ventes['produit_id'] = df_ventes['produit_id'].astype(int)

print(f"Ventes after cleaning: {df_ventes.shape}")

print("\nStep 3: Transformation (Enrichment & Calculation)...")
# 3.1 Join with Clients
df_merged = pd.merge(df_ventes, df_clients, on='client_id', how='inner')

# Drop prix_unitaire from ventes if it exists to avoid duplication with products
if 'prix_unitaire' in df_merged.columns:
    df_merged = df_merged.drop(columns=['prix_unitaire'])

# 3.2 Join with Products
df_merged = pd.merge(df_merged, df_produits, on='produit_id', how='inner')

# 3.3 Calculate Total Revenue
# Now prix_unitaire comes solely from produits
print(f"Merged columns: {df_merged.columns.tolist()}")
df_merged['total_vente'] = df_merged['quantite'] * df_merged['prix_unitaire']

print("Sample of enriched data:")
print(df_merged[['date_vente', 'nom_client', 'nom_produit', 'pays', 'categorie', 'total_vente']].head())

# 3.4 Aggregation (GroupBy)
# Group by Pays and Categorie
df_agg = df_merged.groupby(['pays', 'categorie'])['total_vente'].sum().reset_index()
df_agg = df_agg.rename(columns={'total_vente': 'chiffre_affaires'})

print("\nStep 4: Loading (Export)...")
print(df_agg)

df_agg.to_csv(output_path, index=False)
print(f"\nAnalysis saved to: {output_path}")
