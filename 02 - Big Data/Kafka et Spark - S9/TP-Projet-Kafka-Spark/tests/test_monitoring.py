#!/usr/bin/env python3
"""
Tests for Monitoring and Metrics Collection

Unit tests for the pipeline monitoring and metrics collection system.
"""

import unittest
import time
import json
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from monitoring.metrics import PipelineMetrics


class TestPipelineMetrics(unittest.TestCase):
    """Test cases for PipelineMetrics"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.metrics = PipelineMetrics(
            kafka_bootstrap_servers='localhost:9092',
            kafka_topic='test-streaming-events',
            spark_ui_url='http://localhost:4040'
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.metrics.monitoring_active:
            self.metrics.stop_monitoring()
    
    def test_initialization(self):
        """Test metrics initialization"""
        self.assertEqual(self.metrics.kafka_bootstrap_servers, 'localhost:9092')
        self.assertEqual(self.metrics.kafka_topic, 'test-streaming-events')
        self.assertEqual(self.metrics.spark_ui_url, 'http://localhost:4040')
        
        self.assertEqual(self.metrics.event_count, 0)
        self.assertGreater(time.time() - self.metrics.start_time, 0)
        self.assertEqual(len(self.metrics.event_timestamps), 0)
        self.assertEqual(len(self.metrics.latencies), 0)
    
    def test_record_event(self):
        """Test event recording"""
        initial_count = self.metrics.event_count
        event_time = time.time() - 1.0  # 1 second ago
        
        self.metrics.record_event(event_time)
        
        self.assertEqual(self.metrics.event_count, initial_count + 1)
        self.assertEqual(len(self.metrics.event_timestamps), 1)
        self.assertEqual(len(self.metrics.latencies), 1)
        
        # Check that latency was calculated correctly
        recorded_latency = self.metrics.latencies[0]
        expected_latency = time.time() - event_time
        self.assertAlmostEqual(recorded_latency, expected_latency, delta=0.1)
    
    def test_record_event_without_timestamp(self):
        """Test event recording without timestamp"""
        initial_count = self.metrics.event_count
        
        self.metrics.record_event()
        
        self.assertEqual(self.metrics.event_count, initial_count + 1)
        self.assertEqual(len(self.metrics.event_timestamps), 1)
        self.assertEqual(len(self.metrics.latencies), 0)  # No latency without timestamp
    
    def test_get_throughput(self):
        """Test throughput calculation"""
        # Record some events over time
        start_time = time.time()
        
        for i in range(10):
            time.sleep(0.1)  # Small delay between events
            self.metrics.record_event(time.time() - 0.05)  # 50ms latency
        
        elapsed_time = time.time() - start_time
        throughput = self.metrics.get_throughput()
        
        self.assertEqual(throughput['total_events'], 10)
        self.assertGreater(throughput['total_throughput'], 0)
        self.assertGreater(throughput['recent_throughput'], 0)
        self.assertAlmostEqual(throughput['elapsed_time'], elapsed_time, delta=1.0)
    
    def test_get_latency_stats(self):
        """Test latency statistics calculation"""
        # Record events with different latencies
        latencies = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        for latency in latencies:
            self.metrics.record_event(time.time() - latency)
        
        stats = self.metrics.get_latency_stats()
        
        self.assertAlmostEqual(stats['avg_latency'], 0.3, places=1)
        self.assertEqual(stats['min_latency'], 0.1)
        self.assertEqual(stats['max_latency'], 0.5)
        self.assertEqual(stats['sample_count'], 5)
        
        # P95 and P99 should be close to max for small sample
        self.assertGreater(stats['p95_latency'], 0.4)
        self.assertGreater(stats['p99_latency'], 0.4)
    
    def test_get_latency_stats_empty(self):
        """Test latency stats with no data"""
        stats = self.metrics.get_latency_stats()
        
        expected = {
            'avg_latency': 0.0,
            'min_latency': 0.0,
            'max_latency': 0.0,
            'p95_latency': 0.0,
            'p99_latency': 0.0,
            'sample_count': 0
        }
        
        self.assertEqual(stats, expected)
    
    def test_percentile_calculation(self):
        """Test percentile calculation"""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        # Test P50 (median)
        p50 = self.metrics._percentile(data, 50)
        self.assertEqual(p50, 5)
        
        # Test P90
        p90 = self.metrics._percentile(data, 90)
        self.assertEqual(p90, 9)
        
        # Test P100
        p100 = self.metrics._percentile(data, 100)
        self.assertEqual(p100, 10)
        
        # Test with empty data
        empty_p50 = self.metrics._percentile([], 50)
        self.assertEqual(empty_p50, 0.0)
    
    @patch('monitoring.metrics.psutil')
    def test_get_system_stats(self, mock_psutil):
        """Test system statistics collection"""
        # Mock psutil functions
        mock_psutil.cpu_percent.return_value = 45.2
        mock_psutil.virtual_memory.return_value = Mock(
            total=17179869184,
            available=5432109876,
            percent=67.8
        )
        mock_psutil.disk_usage.return_value = Mock(
            total=512105932800,
            free=392105932800
        )
        
        stats = self.metrics.get_system_stats()
        
        self.assertEqual(stats['cpu_usage'], 45.2)
        self.assertEqual(stats['memory']['total'], 17179869184)
        self.assertEqual(stats['memory']['available'], 5432109876)
        self.assertEqual(stats['memory']['percent'], 67.8)
        self.assertEqual(stats['disk']['total'], 512105932800)
        self.assertEqual(stats['disk']['free'], 392105932800)
        self.assertAlmostEqual(stats['disk']['percent'], 23.4, places=1)
    
    @patch('monitoring.metrics.requests.get')
    def test_collect_spark_metrics(self, mock_get):
        """Test Spark metrics collection"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'id': 'app_1234567890'}
        ]
        mock_get.return_value = mock_response
        
        # Mock jobs response
        mock_jobs_response = Mock()
        mock_jobs_response.status_code = 200
        mock_jobs_response.json.return_value = [
            {'status': 'RUNNING'},
            {'status': 'RUNNING'},
            {'status': 'COMPLETED'}
        ]
        
        # Mock stages response
        mock_stages_response = Mock()
        mock_stages_response.status_code = 200
        mock_stages_response.json.return_value = [
            {'status': 'ACTIVE'},
            {'status': 'COMPLETE'},
            {'status': 'COMPLETE'}
        ]
        
        # Set up different responses for different URLs
        def mock_get_side_effect(url, **kwargs):
            if 'jobs' in url:
                return mock_jobs_response
            elif 'stages' in url:
                return mock_stages_response
            else:
                return mock_response
        
        mock_get.side_effect = mock_get_side_effect
        
        # This should not raise an exception
        try:
            self.metrics._collect_spark_metrics()
        except Exception as e:
            self.fail(f"collect_spark_metrics raised {e} unexpectedly")
    
    @patch('monitoring.metrics.requests.get')
    def test_collect_spark_metrics_failure(self, mock_get):
        """Test Spark metrics collection failure handling"""
        # Mock failed response
        mock_get.return_value.status_code = 500
        
        # Should not raise exception
        try:
            self.metrics._collect_spark_metrics()
        except Exception as e:
            self.fail(f"collect_spark_metrics should handle failures gracefully, got {e}")
    
    @patch('monitoring.metrics.KafkaConsumer')
    def test_collect_kafka_metrics(self, mock_consumer_class):
        """Test Kafka metrics collection"""
        # Mock Kafka consumer
        mock_consumer = Mock()
        mock_consumer.partitions_for_topic.return_value = [0, 1, 2]
        
        # Mock TopicPartition behavior
        mock_tp_0 = Mock()
        mock_tp_0.topic = 'test-streaming-events'
        mock_tp_0.partition = 0
        
        mock_tp_1 = Mock()
        mock_tp_1.topic = 'test-streaming-events'
        mock_tp_1.partition = 1
        
        mock_tp_2 = Mock()
        mock_tp_2.topic = 'test-streaming-events'
        mock_tp_2.partition = 2
        
        # Mock position returns
        mock_consumer.position.side_effect = [100, 50, 75]  # latest offsets
        mock_consumer.seek_to_end.return_value = None
        mock_consumer.seek_to_beginning.return_value = None
        
        mock_consumer_class.return_value = mock_consumer
        
        # Should not raise exception
        try:
            self.metrics._collect_kafka_metrics()
        except Exception as e:
            self.fail(f"collect_kafka_metrics should handle failures gracefully, got {e}")
    
    @patch('monitoring.metrics.KafkaConsumer')
    def test_collect_kafka_metrics_no_topic(self, mock_consumer_class):
        """Test Kafka metrics collection when topic doesn't exist"""
        # Mock Kafka consumer with no partitions
        mock_consumer = Mock()
        mock_consumer.partitions_for_topic.return_value = None
        
        mock_consumer_class.return_value = mock_consumer
        
        # Should not raise exception
        try:
            self.metrics._collect_kafka_metrics()
        except Exception as e:
            self.fail(f"collect_kafka_metrics should handle missing topic gracefully, got {e}")
    
    def test_generate_report(self):
        """Test comprehensive metrics report generation"""
        # Record some test data
        for i in range(5):
            self.metrics.record_event(time.time() - 0.1)
        
        report = self.metrics.generate_report()
        
        # Check report structure
        required_fields = [
            'timestamp', 'throughput', 'latency', 'system_stats', 'system_metrics_history'
        ]
        
        for field in required_fields:
            self.assertIn(field, report)
        
        # Check throughput data
        self.assertIn('total_events', report['throughput'])
        self.assertIn('total_throughput', report['throughput'])
        
        # Check latency data
        self.assertIn('avg_latency', report['latency'])
        self.assertIn('sample_count', report['latency'])
    
    def test_save_report(self):
        """Test saving metrics report to file"""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            # Generate and save report
            self.metrics.save_report(temp_file)
            
            # Check that file was created and has content
            with open(temp_file, 'r') as f:
                content = f.read()
                self.assertGreater(len(content), 0)
                
                # Parse JSON to verify structure
                report = json.loads(content)
                self.assertIn('timestamp', report)
                self.assertIn('throughput', report)
        
        finally:
            # Clean up
            import os
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    @patch('monitoring.metrics.threading.Thread')
    def test_start_monitoring(self, mock_thread):
        """Test starting background monitoring"""
        self.assertFalse(self.metrics.monitoring_active)
        
        self.metrics.start_monitoring(interval=10)
        
        self.assertTrue(self.metrics.monitoring_active)
        mock_thread.assert_called_once()
    
    def test_stop_monitoring(self):
        """Test stopping background monitoring"""
        # Start monitoring first
        self.metrics.start_monitoring(interval=10)
        self.assertTrue(self.metrics.monitoring_active)
        
        # Stop monitoring
        self.metrics.stop_monitoring()
        self.assertFalse(self.metrics.monitoring_active)
    
    def test_monitoring_loop(self):
        """Test monitoring loop execution"""
        # This is a basic test to ensure the loop method exists and can be called
        # Full testing would require mocking all dependencies
        
        # Start monitoring briefly then stop
        self.metrics.start_monitoring(interval=1)
        time.sleep(2)  # Let it run for 2 seconds
        self.metrics.stop_monitoring()
        
        # Should complete without errors
        self.assertFalse(self.metrics.monitoring_active)


class TestIntegration(unittest.TestCase):
    """Integration tests for monitoring system"""
    
    def test_full_metrics_collection_cycle(self):
        """Test complete metrics collection cycle"""
        metrics = PipelineMetrics()
        
        # Record some events
        for i in range(10):
            time.sleep(0.01)  # Small delay
            metrics.record_event(time.time() - 0.05)  # 50ms latency
        
        # Get all metrics
        throughput = metrics.get_throughput()
        latency = metrics.get_latency_stats()
        system_stats = metrics.get_system_stats()
        report = metrics.generate_report()
        
        # Verify all metrics are collected
        self.assertGreater(throughput['total_events'], 0)
        self.assertGreater(throughput['total_throughput'], 0)
        self.assertGreater(latency['sample_count'], 0)
        self.assertGreater(latency['avg_latency'], 0)
        
        # System stats should have data (may be mocked in test environment)
        if system_stats:  # Only check if we have real data
            self.assertIn('cpu_usage', system_stats)
        
        # Report should contain all sections
        self.assertIn('timestamp', report)
        self.assertIn('throughput', report)
        self.assertIn('latency', report)
    
    def test_metrics_with_real_time_simulation(self):
        """Test metrics collection with simulated real-time events"""
        metrics = PipelineMetrics()
        
        start_time = time.time()
        
        # Simulate events over 2 seconds
        for i in range(20):
            # Simulate some processing time
            time.sleep(0.1)
            
            # Record event with simulated latency
            event_time = time.time() - 0.05  # 50ms processing time
            metrics.record_event(event_time)
        
        elapsed = time.time() - start_time
        
        # Calculate expected throughput
        expected_throughput = 20 / elapsed
        
        actual_throughput = metrics.get_throughput()
        
        self.assertEqual(actual_throughput['total_events'], 20)
        self.assertAlmostEqual(actual_throughput['total_throughput'], expected_throughput, delta=2.0)
        
        # Should have latency data
        latency_stats = metrics.get_latency_stats()
        self.assertEqual(latency_stats['sample_count'], 20)
        self.assertAlmostEqual(latency_stats['avg_latency'], 0.05, delta=0.01)


if __name__ == '__main__':
    unittest.main()