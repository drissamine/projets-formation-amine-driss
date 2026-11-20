const amqp = require('amqplib');
const notificationService = require('../../services/notificationService');

const RABBITMQ_URL = process.env.RABBITMQ_URL || 'amqp://localhost:5672';
const EXCHANGE = 'appointments';

class AppointmentConsumer {
  
  async connect() {
    try {
      const connection = await amqp.connect(RABBITMQ_URL);
      const channel = await connection.createChannel();
      
      // Declare exchange
      await channel.assertExchange(EXCHANGE, 'topic', { durable: true });
      
      // Create queue for notifications
      const queue = await channel.assertQueue('notification-appointments', { durable: true });
      
      // Bind queue to exchange
      await channel.bindQueue(
        queue.queue,
        EXCHANGE,
        'appointment.*'
      );

      console.log('[Notification Service] Waiting for messages...');

      // Consume messages
      channel.consume(queue.queue, async (msg) => {
        if (msg) {
          const event = JSON.parse(msg.content.toString());
          console.log(`[Notification Service] Received: ${event.type}`);

          try {
            switch (event.type) {
              case 'appointment.scheduled':
                await notificationService.sendConfirmation(event.data);
                break;
              case 'appointment.cancelled':
                await notificationService.sendCancellation(event.data);
                break;
              case 'appointment.completed':
                await notificationService.sendCompletion(event.data);
                break;
            }
            channel.ack(msg);
          } catch (error) {
            console.error('Error processing message:', error);
            channel.nack(msg, false, true);
          }
        }
      });

    } catch (error) {
      console.error('Failed to connect to RabbitMQ:', error);
    }
  }
}

module.exports = new AppointmentConsumer();
