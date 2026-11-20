from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime

@dataclass
class Produit:
    id: str
    nom: str
    tags: List[str]
    categorie: str = ""
    prix: float = 0.0

@dataclass
class Utilisateur:
    id: str
    interets: List[str]

@dataclass
class Evenement:
    user_id: str
    session_id: str
    event_type: str  # VIEW_PRODUCT, ADD_TO_CART, PURCHASE, etc.
    product_id: str
    product_name: str
    categorie: str
    prix: float
    timestamp: str
    page_duration: int = 0
    user_agent: str = ""
    location: str = ""

@dataclass
class Recommandation:
    user_id: str
    product_ids: List[str]
    algorithm: str  # 'categorie' ou 'recommandation'
    timestamp: str
    scores: Dict[str, float] = None

# Données de test
produits = [
    {"id": "PROD_001", "name": "iPhone 15", "tags": ["électronique", "apple", "téléphone"], "categorie": "Électronique/Smartphones", "prix": 1199.99},
    {"id": "PROD_002", "name": "Samsung Galaxy", "tags": ["électronique", "android", "téléphone"], "categorie": "Électronique/Smartphones", "prix": 899.99},
    {"id": "PROD_003", "name": "Cuisine de A à Z", "tags": ["livre", "cuisine"], "categorie": "Livres/Cuisine", "prix": 29.99},
    {"id": "PROD_004", "name": "Livre Kafka", "tags": ["livre", "big data", "programmation"], "categorie": "Livres/Informatique", "prix": 49.99},
    {"id": "PROD_005", "name": "Formation Spark", "tags": ["formation", "big data", "programmation"], "categorie": "Formation/Online", "prix": 199.99}
]

utilisateurs = [
    {"id": "USER_TECH", "interests": ["électronique", "programmation"]},
    {"id": "USER_FOODIE", "interests": ["cuisine", "voyage"]}
]
