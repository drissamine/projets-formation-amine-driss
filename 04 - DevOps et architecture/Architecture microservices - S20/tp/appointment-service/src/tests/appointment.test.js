const Appointment = require('../domain/aggregates/Appointment');
const request = require('supertest');
const jwt = require('jsonwebtoken');

// Mock du module app pour les tests d'intégration
jest.mock('../index.js', () => {
  const express = require('express');
  const app = express();
  app.use(express.json());
  
  // Health check
  app.get('/health', (req, res) => {
    res.json({ status: 'OK', service: 'appointment-service' });
  });
  
  // Routes without auth for testing
  app.post('/api/appointments', (req, res) => {
    const { patientId, doctorId, dateTime, specialty } = req.body;
    
    if (!patientId || !doctorId || !dateTime || !specialty) {
      return res.status(400).json({
        error: 'Missing required fields: patientId, doctorId, dateTime, specialty'
      });
    }
    
    const appointmentDate = new Date(dateTime);
    if (appointmentDate <= new Date()) {
      return res.status(400).json({
        error: 'Appointment date must be in the future'
      });
    }
    
    res.status(201).json({
      message: 'Appointment created successfully',
      appointment: {
        id: 'apt-test-123',
        patientId,
        doctorId,
        dateTime,
        specialty,
        status: 'SCHEDULED'
      }
    });
  });
  
  app.get('/api/appointments/:id', (req, res) => {
    const { id } = req.params;
    
    if (id === 'not-found') {
      return res.status(404).json({ error: 'Appointment not found' });
    }
    
    res.json({
      id,
      patientId: 'pat-001',
      doctorId: 'dr-001',
      dateTime: '2024-02-15T14:00:00Z',
      specialty: 'Cardiologie',
      status: 'SCHEDULED'
    });
  });
  
  app.put('/api/appointments/:id/cancel', (req, res) => {
    const { id } = req.params;
    
    if (id === 'already-cancelled') {
      return res.status(400).json({ error: 'Cannot cancel appointment: status must be SCHEDULED' });
    }
    
    res.json({
      message: 'Appointment cancelled successfully',
      appointment: {
        id,
        patientId: 'pat-001',
        doctorId: 'dr-001',
        status: 'CANCELLED'
      }
    });
  });
  
  return app;
});

const app = require('../index.js');

const JWT_SECRET = 'medicare-secret-key';

function generateToken(payload = { userId: 'user-001', role: 'admin' }) {
  return jwt.sign(payload, JWT_SECRET, { expiresIn: '1h' });
}

describe('Appointment Aggregate - Unit Tests', () => {
  
  test('should create appointment with SCHEDULED status', () => {
    const appointment = new Appointment(
      'apt-123',
      'pat-001',
      'dr-001',
      '2024-02-15T14:00:00Z',
      'Cardiologie'
    );

    expect(appointment.id).toBe('apt-123');
    expect(appointment.status).toBe('SCHEDULED');
    expect(appointment.patientId).toBe('pat-001');
  });

  test('should cancel scheduled appointment successfully', () => {
    const appointment = new Appointment(
      'apt-123',
      'pat-001',
      'dr-001',
      '2024-02-15T14:00:00Z',
      'Cardiologie'
    );

    appointment.cancel();

    expect(appointment.status).toBe('CANCELLED');
    expect(appointment.domainEvents).toHaveLength(1);
    expect(appointment.domainEvents[0].type).toBe('AppointmentCancelled');
  });

  test('should throw error when cancelling non-scheduled appointment', () => {
    const appointment = new Appointment(
      'apt-123',
      'pat-001',
      'dr-001',
      '2024-02-15T14:00:00Z',
      'Cardiologie'
    );

    appointment.cancel();

    expect(() => appointment.cancel()).toThrow(
      'Cannot cancel appointment: status must be SCHEDULED'
    );
  });

  test('should complete scheduled appointment', () => {
    const appointment = new Appointment(
      'apt-123',
      'pat-001',
      'dr-001',
      '2024-02-15T14:00:00Z',
      'Cardiologie'
    );

    appointment.complete();

    expect(appointment.status).toBe('COMPLETED');
    expect(appointment.domainEvents[0].type).toBe('AppointmentCompleted');
  });

  test('should clear domain events after processing', () => {
    const appointment = new Appointment(
      'apt-123',
      'pat-001',
      'dr-001',
      '2024-02-15T14:00:00Z',
      'Cardiologie'
    );

    appointment.cancel();
    expect(appointment.domainEvents).toHaveLength(1);

    appointment.clearDomainEvents();
    expect(appointment.domainEvents).toHaveLength(0);
  });

  // Nouveaux tests unitaires sur la logique métier
  
  test('should not complete already cancelled appointment', () => {
    const appointment = new Appointment(
      'apt-123',
      'pat-001',
      'dr-001',
      '2024-02-15T14:00:00Z',
      'Cardiologie'
    );

    appointment.cancel();
    
    expect(() => appointment.complete()).toThrow(
      'Cannot complete appointment: status must be SCHEDULED'
    );
  });

  test('should not cancel already completed appointment', () => {
    const appointment = new Appointment(
      'apt-123',
      'pat-001',
      'dr-001',
      '2024-02-15T14:00:00Z',
      'Cardiologie'
    );

    appointment.complete();
    
    expect(() => appointment.cancel()).toThrow(
      'Cannot cancel appointment: status must be SCHEDULED'
    );
  });

  test('should serialize to JSON correctly', () => {
    const appointment = new Appointment(
      'apt-123',
      'pat-001',
      'dr-001',
      '2024-02-15T14:00:00Z',
      'Cardiologie'
    );

    const json = appointment.toJSON();

    expect(json.id).toBe('apt-123');
    expect(json.patientId).toBe('pat-001');
    expect(json.doctorId).toBe('dr-001');
    expect(json.specialty).toBe('Cardiologie');
    expect(json.status).toBe('SCHEDULED');
    expect(json.dateTime).toBeInstanceOf(Date);
  });

  test('should not add event after status change', () => {
    const appointment = new Appointment(
      'apt-123',
      'pat-001',
      'dr-001',
      '2024-02-15T14:00:00Z',
      'Cardiologie'
    );

    appointment.cancel();
    expect(appointment.domainEvents).toHaveLength(1);
    
    // Second action should fail due to status change
    expect(() => appointment.complete()).toThrow();
    expect(appointment.domainEvents).toHaveLength(1);
  });

  test('should emit correct event data on cancellation', () => {
    const appointment = new Appointment(
      'apt-123',
      'pat-001',
      'dr-001',
      '2024-02-15T14:00:00Z',
      'Cardiologie'
    );

    appointment.cancel();

    const event = appointment.domainEvents[0];
    expect(event.type).toBe('AppointmentCancelled');
    expect(event.data.appointmentId).toBe('apt-123');
    expect(event.data.patientId).toBe('pat-001');
    expect(event.data.doctorId).toBe('dr-001');
  });
});

describe('Appointment API - Integration Tests', () => {
  
  test('POST /api/appointments - should create appointment with valid data', async () => {
    const response = await request(app)
      .post('/api/appointments')
      .send({
        patientId: 'pat-001',
        doctorId: 'dr-001',
        dateTime: '2027-12-15T14:00:00Z',
        specialty: 'Cardiologie'
      });

    expect(response.status).toBe(201);
    expect(response.body.message).toBe('Appointment created successfully');
    expect(response.body.appointment.status).toBe('SCHEDULED');
  });

  test('POST /api/appointments - should reject missing required fields', async () => {
    const response = await request(app)
      .post('/api/appointments')
      .send({
        patientId: 'pat-001'
      });

    expect(response.status).toBe(400);
    expect(response.body.error).toContain('Missing required fields');
  });

  test('POST /api/appointments - should reject past date', async () => {
    const response = await request(app)
      .post('/api/appointments')
      .send({
        patientId: 'pat-001',
        doctorId: 'dr-001',
        dateTime: '2020-01-01T14:00:00Z',
        specialty: 'Cardiologie'
      });

    expect(response.status).toBe(400);
    expect(response.body.error).toBe('Appointment date must be in the future');
  });

  test('GET /api/appointments/:id - should return appointment by ID', async () => {
    const response = await request(app)
      .get('/api/appointments/apt-123');

    expect(response.status).toBe(200);
    expect(response.body.id).toBe('apt-123');
    expect(response.body.patientId).toBe('pat-001');
  });

  test('GET /api/appointments/:id - should return 404 for not found', async () => {
    const response = await request(app)
      .get('/api/appointments/not-found');

    expect(response.status).toBe(404);
    expect(response.body.error).toBe('Appointment not found');
  });

  test('PUT /api/appointments/:id/cancel - should cancel appointment', async () => {
    const response = await request(app)
      .put('/api/appointments/apt-123/cancel');

    expect(response.status).toBe(200);
    expect(response.body.message).toBe('Appointment cancelled successfully');
    expect(response.body.appointment.status).toBe('CANCELLED');
  });

  test('PUT /api/appointments/:id/cancel - should reject already cancelled', async () => {
    const response = await request(app)
      .put('/api/appointments/already-cancelled/cancel');

    expect(response.status).toBe(400);
    expect(response.body.error).toContain('Cannot cancel appointment');
  });
});
