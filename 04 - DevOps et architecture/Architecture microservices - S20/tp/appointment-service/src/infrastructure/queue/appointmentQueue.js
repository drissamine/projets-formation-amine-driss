const amqp = require('amqplib');

const RABBITMQ_URL = process.env.RABBITMQ_URL || 'amqp://localhost:5672';
const EXCHANGE = 'appointments';

class AppointmentQueue {
  constructor() {
    this.connection = null;
    this.channel = null;
  }

  async connect() {
    try {
      this.connection = await amqp.connect(RABBITMQ_URL);
      this.channel = await this.connection.createChannel();
      
      // Declare exchange
      await this.channel.assertExchange(EXCHANGE, 'topic', { durable: true });
      
      console.log('[Appointment Queue] Connected to RabbitMQ');
    } catch (error) {
      console.error('[Appointment Queue] Failed to connect:', error.message);
    }
  }

  async publishAppointmentScheduled(appointment) {
    const event = {
      type: 'appointment.scheduled',
      data: appointment,
      timestamp: new Date().toISOString()
    };
    
    this.channel.publish(
      EXCHANGE,
      'appointment.scheduled',
      Buffer.from(JSON.stringify(event)),
      { persistent: true }
    );
    
    console.log(`[Appointment Queue] Published: appointment.scheduled for ${appointment.id}`);
  }

  async publishAppointmentCancelled(appointment) {
    const event = {
      type: 'appointment.cancelled',
      data: appointment,
      timestamp: new Date().toISOString()
    };
    
    this.channel.publish(
      EXCHANGE,
      'appointment.cancelled',
      Buffer.from(JSON.stringify(event)),
      { persistent: true }
    );
    
    console.log(`[Appointment Queue] Published: appointment.cancelled for ${appointment.id}`);
  }

  async publishAppointmentCompleted(appointment) {
    const event = {
      type: 'appointment.completed',
      data: appointment,
      timestamp: new Date().toISOString()
    };
    
    this.channel.publish(
      EXCHANGE,
      'appointment.completed',
      Buffer.from(JSON.stringify(event)),
      { persistent: true }
    );
    
    console.log(`[Appointment Queue] Published: appointment.completed for ${appointment.id}`);
  }
}

module.exports = new AppointmentQueue();
