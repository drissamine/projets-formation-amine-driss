import express from 'express';
import morgan from 'morgan';
import dotenv from 'dotenv';

import paymentRoutes from './src/interfaces/paymentController.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3004;

app.use(express.json());
app.use(morgan('dev'));

// Routes
app.use('/', paymentRoutes);

app.get('/health', (req, res) => {
  res.json({ service: 'Payment Service', status: 'OK' });
});

app.listen(PORT, () => {
  console.log(`💳 Payment Service running on http://localhost:${PORT}`);
});
