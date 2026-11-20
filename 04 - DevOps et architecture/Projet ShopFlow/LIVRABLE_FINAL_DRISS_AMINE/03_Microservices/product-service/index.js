import express from 'express';
import morgan from 'morgan';
import dotenv from 'dotenv';

import productRoutes from './src/interfaces/productController.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3002;

app.use(express.json());
app.use(morgan('dev'));

// Routes
app.use('/', productRoutes);

app.get('/health', (req, res) => {
  res.json({ service: 'Product Service', status: 'OK' });
});

app.listen(PORT, () => {
  console.log(`📦 Product Service running on http://localhost:${PORT}`);
});
