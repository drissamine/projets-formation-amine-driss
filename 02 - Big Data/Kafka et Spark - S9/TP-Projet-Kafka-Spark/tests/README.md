# Tests et Validation

## Description
Suite de tests unitaires et d'intégration pour valider le fonctionnement du pipeline Kafka-Spark Streaming.

## Structure des Tests

### Tests Unitaires
- **`test_kafka_producer.py`**: Tests pour le producteur Kafka
- **`test_spark_streaming.py`**: Tests pour le consommateur Spark
- **`test_monitoring.py`**: Tests pour le système de monitoring

### Tests d'Intégration
- **Simulation de charge**: Tests avec 100K événements
- **Reprise sur incident**: Tests de checkpointing et recovery
- **Performance**: Tests de throughput et latence

## Exécution des Tests

### Prérequis
```bash
# Installer les dépendances de test
pip install pytest pytest-cov unittest-xml-reporting
```

### Exécution des Tests Unitaires
```bash
# Exécuter tous les tests
python -m pytest tests/ -v

# Exécuter tests spécifiques
python -m pytest tests/test_kafka_producer.py -v
python -m pytest tests/test_spark_streaming.py -v
python -m pytest tests/test_monitoring.py -v

# Générer rapport de couverture
python -m pytest tests/ --cov=producer --cov=spark --cov=monitoring --cov-report=html
```

### Exécution avec unittest
```bash
# Exécuter tests Kafka Producer
python tests/test_kafka_producer.py

# Exécuter tests Spark Streaming
python tests/test_spark_streaming.py

# Exécuter tests Monitoring
python tests/test_monitoring.py
```

## Couverture des Tests

### Kafka Producer Tests
- **Event Generation**: Validation de la structure et distribution des événements
- **Producer Functionality**: Tests d'envoi, gestion d'erreurs, fermeture
- **Integration**: Tests de sérialisation JSON et validation de schéma

#### Tests Clés
```python
# Structure des événements
def test_generate_event_structure(self)

# Distribution des types d'événements
def test_event_type_distribution(self)

# Gestion des erreurs
def test_send_event_failure(self)

# Fermeture propre
def test_close_producer(self)
```

### Spark Streaming Tests
- **Schema Validation**: Vérification du schéma JSON et parsing
- **Query Logic**: Tests des requêtes d'analyse (popularité, engagement, genre, anomalies)
- **Windowing**: Tests des fenêtres glissantes et calculs d'agrégation
- **DataFrame Operations**: Tests des transformations Spark

#### Tests Clés
```python
# Validation du schéma
def test_schema_definition(self)

# Calcul de popularité
def test_query_1_popularity(self)

# Détection d'inactivité
def test_query_2_engagement(self)

# Analyse par genre
def test_query_3_genre_analysis(self)

# Détection d'anomalies
def test_query_4_anomaly_detection(self)
```

### Monitoring Tests
- **Metrics Collection**: Tests de collecte de métriques (throughput, latence, système)
- **Background Monitoring**: Tests du monitoring en arrière-plan
- **Report Generation**: Tests de génération et sauvegarde de rapports
- **Error Handling**: Tests de gestion des erreurs de monitoring

#### Tests Clés
```python
# Collecte de métriques
def test_record_event(self)
def test_get_throughput(self)
def test_get_latency_stats(self)

# Monitoring en arrière-plan
def test_start_monitoring(self)
def test_stop_monitoring(self)

# Génération de rapports
def test_generate_report(self)
def test_save_report(self)
```

## Tests d'Intégration

### Simulation de Charge
```python
def test_full_pipeline_with_100k_events(self):
    """Test full pipeline with 100K events"""
    # Generate 100K events
    # Process through Kafka -> Spark
    # Validate results
    # Check performance metrics
```

### Reprise sur Incident
```python
def test_checkpoint_recovery(self):
    """Test recovery from checkpoint after crash"""
    # Start pipeline
    # Process some events
    # Simulate crash
    # Restart from checkpoint
    # Verify continuity
```

### Performance Tests
```python
def test_throughput_under_load(self):
    """Test throughput with high event rate"""
    # Generate events at high rate
    # Measure actual throughput
    # Verify system stability
```

## Mocking et Isolation

### Kafka Mocking
```python
@patch('producer.kafka_producer.KafkaProducer')
def test_producer_with_mock(self, mock_producer):
    # Mock Kafka connection for testing
    # Test producer logic without actual Kafka
```

### Spark Mocking
```python
@patch('spark.consumer.spark_streaming_app.SparkSession')
def test_spark_with_mock(self, mock_spark):
    # Mock Spark session for testing
    # Test streaming logic without actual Spark cluster
```

### System Metrics Mocking
```python
@patch('monitoring.metrics.psutil')
def test_system_metrics_with_mock(self, mock_psutil):
    # Mock system metrics for consistent testing
    # Test monitoring logic without real system calls
```

## Validation des Résultats

### Expected Results Validation
```python
def validate_query_results(self, results):
    """Validate that query results meet expectations"""
    # Check result structure
    # Verify aggregation accuracy
    # Validate window calculations
```

### Performance Benchmarks
```python
def validate_performance_metrics(self, metrics):
    """Validate performance meets requirements"""
    # Check throughput > 100 events/sec
    # Check latency < 1 second
    # Check system resource usage
```

### Data Quality Checks
```python
def validate_data_quality(self, events):
    """Validate data quality and consistency"""
    # Check for missing fields
    # Validate field ranges
    # Check for data corruption
```

## Rapports de Test

### Coverage Report
```bash
# Générer rapport HTML de couverture
python -m pytest tests/ --cov=producer --cov=spark --cov=monitoring --cov-report=html

# Ouvrir rapport dans navigateur
open htmlcov/index.html
```

### Test Results XML
```bash
# Générer rapport XML pour CI/CD
python -m pytest tests/ --junitxml=test-results.xml
```

### Performance Report
```bash
# Exécuter tests de performance
python -m pytest tests/ -k "performance" --html=performance-report.html
```

## Dépannage des Tests

### Problèmes Courants

#### Kafka Connection Errors
```bash
# Vérifier que Kafka est accessible
telnet localhost 9092

# Vérifier les topics
kafka-topics.sh --list --bootstrap-server localhost:9092
```

#### Spark Session Errors
```bash
# Vérifier la configuration Spark
export SPARK_HOME=/path/to/spark
export PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-*.zip:$PYTHONPATH
```

#### Memory Issues
```bash
# Augmenter la mémoire pour les tests
export SPARK_DRIVER_MEMORY=2g
export SPARK_EXECUTOR_MEMORY=4g
```

### Debugging Tips

#### Enable Debug Logging
```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

#### Use Test Fixtures
```python
class TestWithRealKafka(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Setup real Kafka for integration tests
        pass
```

#### Isolate Test Dependencies
```python
# Use temporary directories for test data
import tempfile
self.test_dir = tempfile.mkdtemp()
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Test Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: python -m pytest tests/ -v
      - name: Generate coverage
        run: python -m pytest tests/ --cov=producer --cov=spark --cov=monitoring --cov-report=xml
```

### Test Automation
```bash
# Script de test automatisé
#!/bin/bash
set -e

echo "Running unit tests..."
python -m pytest tests/ -v

echo "Running integration tests..."
python -m pytest tests/ -k "integration" -v

echo "Generating coverage report..."
python -m pytest tests/ --cov=producer --cov=spark --cov=monitoring --cov-report=html

echo "All tests passed!"