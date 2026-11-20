import express from 'express';
import morgan from 'morgan';
import dotenv from 'dotenv';

import authRoutes from './src/interfaces/authController.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

app.use(express.json());
app.use(morgan('dev'));

// Routes
app.use('/', authRoutes);

app.get('/health', (req, res) => {
  res.json({ service: 'User Service', status: 'OK' });
});

// Routes à implémenter : /api/auth/register, /api/auth/login

app.listen(PORT, () => {
  console.log(`👤 User Service running on http://localhost:${PORT}`);
});
