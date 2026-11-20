#!/usr/bin/env python3
import time
import sys
import os
from unittest.mock import Mock, patch
# Add parent directory to path to import producer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_load_test(num_events=100000):
    print(f"🚀 Démarrage du test de charge : {num_events} événements")
    
    # Mocking real Kafka BEFORE instantiation
    with patch('producer.kafka_producer.KafkaProducer') as mock_kp_class:
        mock_producer_instance = Mock()
        mock_kp_class.return_value = mock_producer_instance
        
        from producer.kafka_producer import KafkaStreamingProducer
        producer = KafkaStreamingProducer(bootstrap_servers='localhost:9092', topic='load-test')
        
        start_time = time.time()
        
        # Disable logging for performance
        import logging
        logging.getLogger('producer.kafka_producer').setLevel(logging.WARNING)
        
        # Generation
        producer.generate_and_send_events(num_events=num_events, delay=0)
        
        end_time = time.time()
        duration = end_time - start_time
        throughput = num_events / duration
        
        print(f"✅ Test de charge terminé")
        print(f"⏱️ Durée totale : {duration:.2f} secondes")
        print(f"📊 Débit : {throughput:.2f} événements/seconde")
        
        return duration, throughput

if __name__ == "__main__":
    run_load_test()
