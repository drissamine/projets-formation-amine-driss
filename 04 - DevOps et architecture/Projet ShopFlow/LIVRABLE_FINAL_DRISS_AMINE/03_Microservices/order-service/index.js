import express from 'express';
import morgan from 'morgan';
import dotenv from 'dotenv';

import orderRoutes from './src/interfaces/orderController.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3003;

app.use(express.json());
app.use(morgan('dev'));

// Routes
app.use('/', orderRoutes);

app.get('/health', (req, res) => {
  res.json({ service: 'Order Service', status: 'OK' });
});

app.listen(PORT, () => {
  console.log(`📦 Order Service running on http://localhost:${PORT}`);
});
