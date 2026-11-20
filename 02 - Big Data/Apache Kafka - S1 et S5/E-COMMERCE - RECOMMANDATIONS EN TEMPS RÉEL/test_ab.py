import json
from collections import defaultdict
from kafka import KafkaConsumer
import threading
import time

import config

class TestAB:
    def __init__(self):
        self.metrics = defaultdict(lambda: {'total_recommandations': 0, 'clics': 0, 'conversions': 0})

        # Consumer pour les métriques
        self.consumer_clics = KafkaConsumer(
            'clics_recommandations',  # Topic pour les clics sur recommandations
            bootstrap_servers=config.KAFKA_SERVERS,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            group_id='ab_testing',
            auto_offset_reset='earliest'
        )

        self.consumer_conversions = KafkaConsumer(
            'conversions',  # Topic pour les conversions
            bootstrap_servers=config.KAFKA_SERVERS,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            group_id='ab_testing_conversions',
            auto_offset_reset='earliest'
        )

    def traiter_clic(self, message):
        """Traite un clic sur une recommandation"""
        data = message.value
        algorithm = data.get('algorithm')
        if algorithm:
            self.metrics[algorithm]['clics'] += 1

    def traiter_conversion(self, message):
        """Traite une conversion"""
        data = message.value
        algorithm = data.get('algorithm')
        if algorithm:
            self.metrics[algorithm]['conversions'] += 1

    def calculer_taux(self):
        """Calcule les taux de conversion pour chaque algorithme"""
        resultats = {}
        for algo, metriques in self.metrics.items():
            total = metriques['total_recommandations']
            clics = metriques['clics']
            conversions = metriques['conversions']

            taux_clic = (clics / total * 100) if total > 0 else 0
            taux_conversion = (conversions / total * 100) if total > 0 else 0

            resultats[algo] = {
                'total_recommandations': total,
                'clics': clics,
                'conversions': conversions,
                'taux_clic': round(taux_clic, 2),
                'taux_conversion': round(taux_conversion, 2)
            }

        return resultats

    def demarrer(self):
        """Démarre l'écoute des événements A/B"""
        print("Test A/B démarré...")

        # Thread pour les clics
        def ecouter_clics():
            for message in self.consumer_clics:
                self.traiter_clic(message)

        # Thread pour les conversions
        def ecouter_conversions():
            for message in self.consumer_conversions:
                self.traiter_conversion(message)

        thread_clics = threading.Thread(target=ecouter_clics, daemon=True)
        thread_conversions = threading.Thread(target=ecouter_conversions, daemon=True)

        thread_clics.start()
        thread_conversions.start()

        # Garder le thread principal actif
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Arrêt du test A/B")

    def obtenir_resultats(self):
        """Retourne les résultats actuels du test A/B"""
        return self.calculer_taux()

if __name__ == "__main__":
    test_ab = TestAB()
    test_ab.demarrer()
