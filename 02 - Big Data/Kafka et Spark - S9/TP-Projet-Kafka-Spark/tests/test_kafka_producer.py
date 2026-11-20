#!/usr/bin/env python3
"""
Tests for Kafka Producer

Unit tests for the Kafka streaming events producer.
"""

import unittest
import json
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from producer.kafka_producer import StreamingEventGenerator, KafkaStreamingProducer


class TestStreamingEventGenerator(unittest.TestCase):
    """Test cases for StreamingEventGenerator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = StreamingEventGenerator()
    
    def test_generate_event_structure(self):
        """Test that generated events have correct structure"""
        event = self.generator.generate_event()
        
        # Check required fields
        required_fields = [
            'event_id', 'user_id', 'video_id', 'event_type',
            'timestamp', 'current_time', 'duration', 'genre', 'device'
        ]
        
        for field in required_fields:
            self.assertIn(field, event)
        
        # Check field types
        self.assertIsInstance(event['event_id'], str)
        self.assertIsInstance(event['user_id'], str)
        self.assertIsInstance(event['video_id'], str)
        self.assertIsInstance(event['event_type'], str)
        self.assertIsInstance(event['timestamp'], str)
        self.assertIsInstance(event['current_time'], float)
        self.assertIsInstance(event['duration'], int)
        self.assertIsInstance(event['genre'], str)
        self.assertIsInstance(event['device'], str)
    
    def test_event_type_distribution(self):
        """Test that event types follow expected distribution"""
        event_types = []
        for _ in range(1000):
            event = self.generator.generate_event()
            event_types.append(event['event_type'])
        
        # Check that all event types are present
        unique_types = set(event_types)
        self.assertEqual(unique_types, {'PLAY', 'PAUSE', 'STOP', 'SEEK'})
        
        # Check approximate distribution (allowing for randomness)
        play_count = event_types.count('PLAY')
        self.assertGreater(play_count, 500)  # Should be around 60%
    
    def test_user_id_range(self):
        """Test that user IDs are in expected range"""
        event = self.generator.generate_event()
        self.assertTrue(event['user_id'].startswith('user_'))
        user_num = int(event['user_id'].split('_')[1])
        self.assertGreaterEqual(user_num, 1)
        self.assertLessEqual(user_num, 100)
    
    def test_video_id_range(self):
        """Test that video IDs are in expected range"""
        event = self.generator.generate_event()
        self.assertTrue(event['video_id'].startswith('video_'))
        video_num = int(event['video_id'].split('_')[1])
        self.assertGreaterEqual(video_num, 1)
        self.assertLessEqual(video_num, 50)
    
    def test_duration_range(self):
        """Test that video durations are in expected range"""
        event = self.generator.generate_event()
        self.assertGreaterEqual(event['duration'], 60)  # 1 minute
        self.assertLessEqual(event['duration'], 1800)   # 30 minutes
    
    def test_current_time_validity(self):
        """Test that current_time is valid relative to duration"""
        for _ in range(100):
            event = self.generator.generate_event()
            duration = event['duration']
            current_time = event['current_time']
            
            # current_time should be between 0 and duration
            self.assertGreaterEqual(current_time, 0)
            self.assertLessEqual(current_time, duration)
    
    def test_genre_validity(self):
        """Test that genres are valid"""
        valid_genres = {'action', 'comedy', 'drama', 'thriller', 'romance', 'documentary'}
        
        for _ in range(100):
            event = self.generator.generate_event()
            self.assertIn(event['genre'], valid_genres)
    
    def test_device_validity(self):
        """Test that devices are valid"""
        valid_devices = {'mobile', 'desktop', 'tv'}
        
        for _ in range(100):
            event = self.generator.generate_event()
            self.assertIn(event['device'], valid_devices)


class TestKafkaStreamingProducer(unittest.TestCase):
    """Test cases for KafkaStreamingProducer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_producer = Mock()
        self.mock_producer.send.return_value = Mock()
        
        with patch('producer.kafka_producer.KafkaProducer', return_value=self.mock_producer):
            self.producer = KafkaStreamingProducer(
                bootstrap_servers='localhost:9092',
                topic='test-topic'
            )
    
    def test_producer_initialization(self):
        """Test that producer initializes correctly"""
        self.assertIsNotNone(self.producer.generator)
        self.assertIsNotNone(self.producer.producer)
        self.assertEqual(self.producer.topic, 'test-topic')
        self.assertEqual(self.producer.bootstrap_servers, 'localhost:9092')
    
    @patch('producer.kafka_producer.logger')
    def test_send_event_success(self, mock_logger):
        """Test successful event sending"""
        test_event = {
            'event_id': 'test-123',
            'user_id': 'user_0001',
            'video_id': 'video_0001',
            'event_type': 'PLAY',
            'timestamp': '2024-01-01T10:00:00Z',
            'current_time': 0.0,
            'duration': 600,
            'genre': 'action',
            'device': 'mobile'
        }
        
        self.producer.send_event(test_event)
        
        # Verify producer.send was called with correct arguments
        self.mock_producer.send.assert_called_once_with('test-topic', test_event)
        mock_logger.debug.assert_called_once()
    
    @patch('producer.kafka_producer.logger')
    def test_send_event_failure(self, mock_logger):
        """Test event sending failure handling"""
        self.mock_producer.send.side_effect = Exception("Kafka error")
        
        test_event = {'event_id': 'test-123'}
        self.producer.send_event(test_event)
        
        mock_logger.error.assert_called_once()
    
    def test_generate_and_send_events(self):
        """Test generating and sending multiple events"""
        # Mock the generator to return predictable events
        self.producer.generator.generate_event = Mock(return_value={
            'event_id': 'test-123',
            'user_id': 'user_0001',
            'video_id': 'video_0001',
            'event_type': 'PLAY',
            'timestamp': '2024-01-01T10:00:00Z',
            'current_time': 0.0,
            'duration': 600,
            'genre': 'action',
            'device': 'mobile'
        })
        
        # Test with small number of events
        self.producer.generate_and_send_events(num_events=3, delay=0.01)
        
        # Verify send was called 3 times
        self.assertEqual(self.mock_producer.send.call_count, 3)
    
    @patch('producer.kafka_producer.logger')
    def test_generate_and_send_events_with_failure(self, mock_logger):
        """Test generating events with some failures"""
        # Make every second send fail
        call_count = 0
        def mock_send(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count % 2 == 0:
                raise Exception("Simulated failure")
            return Mock()
        
        self.mock_producer.send.side_effect = mock_send
        
        self.producer.generate_and_send_events(num_events=3, delay=0.01)
        
        # Should have tried to send 3 times
        self.assertEqual(self.mock_producer.send.call_count, 3)
        # Should have logged 1 error
        self.assertEqual(mock_logger.error.call_count, 1)
    
    def test_close_producer(self):
        """Test producer closure"""
        self.producer.close()
        
        self.mock_producer.flush.assert_called_once()
        self.mock_producer.close.assert_called_once()


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_full_event_generation_and_validation(self):
        """Test complete event generation and validation"""
        generator = StreamingEventGenerator()
        
        # Generate multiple events
        events = []
        for i in range(10):
            event = generator.generate_event()
            events.append(event)
        
        # Validate all events
        for event in events:
            # Check JSON serialization
            json_str = json.dumps(event)
            parsed_event = json.loads(json_str)
            
            # Verify structure is preserved
            self.assertEqual(event['event_id'], parsed_event['event_id'])
            self.assertEqual(event['user_id'], parsed_event['user_id'])
            self.assertEqual(event['video_id'], parsed_event['video_id'])
            self.assertEqual(event['event_type'], parsed_event['event_type'])
            self.assertEqual(event['timestamp'], parsed_event['timestamp'])
            self.assertEqual(event['current_time'], parsed_event['current_time'])
            self.assertEqual(event['duration'], parsed_event['duration'])
            self.assertEqual(event['genre'], parsed_event['genre'])
            self.assertEqual(event['device'], parsed_event['device'])


if __name__ == '__main__':
    unittest.main()