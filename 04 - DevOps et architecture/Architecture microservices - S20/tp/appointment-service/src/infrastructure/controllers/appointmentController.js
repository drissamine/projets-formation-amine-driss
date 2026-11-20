const Appointment = require('../../domain/aggregates/Appointment');
const { v4: uuidv4 } = require('uuid');
const appointmentQueue = require('../queue/appointmentQueue');

class AppointmentController {
  
  // POST /appointments - Create appointment
  async create(req, res) {
    try {
      const { patientId, doctorId, dateTime, specialty } = req.body;
      
      // Validation métier
      if (!patientId || !doctorId || !dateTime || !specialty) {
        return res.status(400).json({
          error: 'Missing required fields: patientId, doctorId, dateTime, specialty'
        });
      }

      // Vérifier que la date est future
      const appointmentDate = new Date(dateTime);
      if (appointmentDate <= new Date()) {
        return res.status(400).json({
          error: 'Appointment date must be in the future'
        });
      }

      const appointment = new Appointment(
        uuidv4(),
        patientId,
        doctorId,
        dateTime,
        specialty
      );

      // Publier l'événement vers RabbitMQ
      await appointmentQueue.publishAppointmentScheduled(appointment.toJSON());

      // Sauvegarder en base (simulation)
      // await AppointmentModel.create(appointment.toJSON());

      // Vider les événements domaine
      appointment.clearDomainEvents();

      res.status(201).json({
        message: 'Appointment created successfully',
        appointment: appointment.toJSON()
      });

    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }

  // GET /appointments/:id - Get appointment by ID
  async getById(req, res) {
    try {
      const { id } = req.params;
      
      // Simuler la récupération depuis MongoDB
      // const appointment = await AppointmentModel.findById(id);
      
      // Simulation pour l'exemple
      const appointment = {
        id,
        patientId: 'pat-001',
        doctorId: 'dr-001',
        dateTime: new Date('2024-02-15T14:00:00Z'),
        specialty: 'Cardiologie',
        status: 'SCHEDULED'
      };

      if (!appointment) {
        return res.status(404).json({ error: 'Appointment not found' });
      }

      res.json(appointment);

    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  }

  // PUT /appointments/:id/cancel - Cancel appointment
  async cancel(req, res) {
    try {
      const { id } = req.params;
      
      const appointment = new Appointment(
        id,
        'pat-001',
        'dr-001',
        '2024-02-15T14:00:00Z',
        'Cardiologie'
      );

      appointment.cancel();

      await appointmentQueue.publishAppointmentCancelled(appointment.toJSON());

      res.json({
        message: 'Appointment cancelled successfully',
        appointment: appointment.toJSON()
      });

    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  }
}

module.exports = new AppointmentController();
