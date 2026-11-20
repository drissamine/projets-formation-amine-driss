require('dotenv').config();
const express = require('express');
const notificationRoutes = require('./infrastructure/controllers/notificationRoutes');
const appointmentConsumer = require('./infrastructure/queue/appointmentConsumer');
const db = require('./infrastructure/database/mongodb');

const app = express();
const PORT = process.env.PORT || 3006;

// Middleware
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'OK', service: 'notification-service' });
});

// Routes
app.use('/api/notifications', notificationRoutes);

// Start server
app.listen(PORT, async () => {
  console.log(`Notification Service running on port ${PORT}`);
  
  // Connect to RabbitMQ and start consuming
  await appointmentConsumer.connect();
  
  // Connect to MongoDB
  await db.connect();
});

module.exports = app;
