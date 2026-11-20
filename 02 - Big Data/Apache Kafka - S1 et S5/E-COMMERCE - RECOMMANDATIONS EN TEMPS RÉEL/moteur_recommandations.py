import json
import threading
import time
from collections import defaultdict, Counter
from datetime import datetime
from kafka import KafkaConsumer, KafkaProducer

import modeles
import config

class MoteurRecommandations:
    def __init__(self):
        # État en mémoire
        self.profils_utilisateurs = defaultdict(lambda: {
            'vus': set(),
            'achetes': set(),
            'categories_preferees': Counter(),
            'derniere_activite': None
        })

        self.matrice_recommandation = defaultdict(Counter)  # produit -> produits associés
        self.achats_par_categorie = defaultdict(Counter)  # categorie -> produits populaires

        # Kafka
        self.consumer = KafkaConsumer(
            config.TOPIC_EVENEMENTS,
            bootstrap_servers=config.KAFKA_SERVERS,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            group_id='recommendation_engine',
            auto_offset_reset='earliest'
        )

        self.producer = KafkaProducer(
            bootstrap_servers=config.KAFKA_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        # A/B Testing
        self.assignation_groupes = {}  # user_id -> groupe ('categorie' ou 'recommandation')
        self.metrics_ab = {'categorie': {'total': 0, 'clics': 0},
                          'recommandation': {'total': 0, 'clics': 0}}

    def assigner_groupe_ab(self, user_id: str) -> str:
        """Assigne un utilisateur à un groupe A/B"""
        if user_id not in self.assignation_groupes:
            self.assignation_groupes[user_id] = config.GROUPES_AB[len(self.assignation_groupes) % len(config.GROUPES_AB)]
        return self.assignation_groupes[user_id]

    def mettre_a_jour_etat(self, evenement: dict):
        """Met à jour l'état interne basé sur l'événement"""
        user_id = evenement['user_id']
        product_id = evenement['product_id']
        event_type = evenement['event_type']
        categorie = evenement['categorie']

        profil = self.profils_utilisateurs[user_id]

        if event_type == 'VIEW_PRODUCT':
            profil['vus'].add(product_id)
            profil['categories_preferees'][categorie] += 1

        elif event_type == 'PURCHASE':
            profil['achetes'].add(product_id)
            profil['categories_preferees'][categorie] += 3  # Plus de poids pour achat

            # Mettre à jour matrice de recommandation
            for produit_achete in profil['achetes']:
                if produit_achete != product_id:
                    self.matrice_recommandation[produit_achete][product_id] += 1
                    self.matrice_recommandation[product_id][produit_achete] += 1

        profil['derniere_activite'] = evenement['timestamp']

        # Mettre à jour achats par catégorie
        if event_type == 'PURCHASE':
            self.achats_par_categorie[categorie][product_id] += 1

    def recommander_par_categorie(self, user_id: str, produit_courant: str) -> list:
        """Algorithme simple basé sur la catégorie"""
        profil = self.profils_utilisateurs[user_id]
        categorie_courante = None

        # Trouver la catégorie du produit courant
        for prod in modeles.produits:
            if prod['id'] == produit_courant:
                categorie_courante = prod['categorie']
                break

        if not categorie_courante:
            return []

        # Produits populaires dans cette catégorie
        produits_categorie = [p['id'] for p in modeles.produits if p['categorie'] == categorie_courante]
        produits_categorie = [p for p in produits_categorie if p not in profil['vus'] and p != produit_courant]

        # Trier par popularité
        produits_tries = sorted(produits_categorie,
                              key=lambda p: self.achats_par_categorie[categorie_courante][p],
                              reverse=True)

        return produits_tries[:config.NOMBRE_RECOMMANDATIONS_MAX]

    def recommander_par_recommandation(self, user_id: str, produit_courant: str) -> list:
        """Algorithme avancé basé sur la recommandation"""
        profil = self.profils_utilisateurs[user_id]

        # Produits associés au produit courant
        produits_associes = self.matrice_recommandation[produit_courant]

        # Filtrer ceux déjà vus/achetés
        recommandations = [(pid, score) for pid, score in produits_associes.items()
                          if pid not in profil['vus'] and pid not in profil['achetes']]

        # Trier par score
        recommandations.sort(key=lambda x: x[1], reverse=True)

        return [pid for pid, _ in recommandations[:config.NOMBRE_RECOMMANDATIONS_MAX]]

    def generer_recommandations(self, user_id: str, produit_courant: str) -> dict:
        """Génère des recommandations pour un utilisateur"""
        groupe = self.assigner_groupe_ab(user_id)

        if groupe == 'categorie':
            produits_recommandes = self.recommander_par_categorie(user_id, produit_courant)
        else:
            produits_recommandes = self.recommander_par_recommandation(user_id, produit_courant)

        return {
            'user_id': user_id,
            'product_ids': produits_recommandes,
            'algorithm': groupe,
            'timestamp': datetime.now().isoformat(),
            'current_product': produit_courant
        }

    def traiter_evenement(self, evenement: dict):
        """Traite un événement et génère des recommandations si nécessaire"""
        self.mettre_a_jour_etat(evenement)

        # Générer recommandations pour VIEW_PRODUCT
        if evenement['event_type'] == 'VIEW_PRODUCT':
            recommandations = self.generer_recommandations(evenement['user_id'], evenement['product_id'])

            if recommandations['product_ids']:
                # Envoyer recommandations
                self.producer.send(config.TOPIC_RECOMMANDATIONS, value=recommandations)

                # Mettre à jour métriques A/B
                algo = recommandations['algorithm']
                self.metrics_ab[algo]['total'] += 1

                print(f"Recommandations générées pour {evenement['user_id']}: {recommandations['product_ids']} (algo: {algo})")

    def demarrer(self):
        """Démarre le traitement des événements"""
        print("Moteur de recommandations démarré...")
        try:
            for message in self.consumer:
                evenement = message.value
                self.traiter_evenement(evenement)
        except KeyboardInterrupt:
            print("Arrêt du moteur de recommandations")
        finally:
            self.consumer.close()
            self.producer.close()

if __name__ == "__main__":
    moteur = MoteurRecommandations()
    moteur.demarrer()
