import Redis from 'ioredis';
import dotenv from 'dotenv';

dotenv.config();

const redis = new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379,
});

console.log('🔔 Notification Service waiting for events...');

redis.subscribe('shopflow_notifications', (err, count) => {
  if (err) {
    console.error('Failed to subscribe:', err.message);
  } else {
    console.log(`Subscribed to ${count} channel(s).`);
  }
});

redis.on('message', (channel, message) => {
  if (channel === 'shopflow_notifications') {
    const event = JSON.parse(message);
    processNotification(event);
  }
});

function processNotification(event) {
  const { type, data } = event;
  console.log(`\n--- NEW NOTIFICATION ---`);
  console.log(`Type: ${type}`);
  
  switch(type) {
    case 'ORDER_PLACED':
      console.log(`📧 Sending Confirmation Email to User ${data.userId} for Order ${data.orderId}`);
      console.log(`Content: Your order of $${data.amount} has been received.`);
      break;
    case 'PAYMENT_SUCCESS':
      console.log(`📱 Sending SMS to User: Payment confirmed for Order ${data.orderId}`);
      console.log(`Content: Payment of $${data.amount} successful!`);
      break;
    default:
      console.log('Unknown event type:', type);
  }
  console.log(`------------------------\n`);
}
