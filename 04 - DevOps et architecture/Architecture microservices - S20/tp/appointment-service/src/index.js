require('dotenv').config();
const express = require('express');
const appointmentRoutes = require('./routes/appointmentRoutes');
const db = require('./infrastructure/database/mongodb');

const app = express();
const PORT = process.env.PORT || 3002;

// Middleware
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'OK', service: 'appointment-service' });
});

// Routes
app.use('/api/appointments', appointmentRoutes);

// Start server
app.listen(PORT, async () => {
  console.log(`Appointment Service running on port ${PORT}`);
  
  // Connect to MongoDB
  await db.connect();
});

module.exports = app;
