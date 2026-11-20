import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const app = express();

// Middlewares
app.use(helmet());
app.use(cors());
app.use(morgan('dev'));
app.use(express.json());

// Routes
import userRoutes from './modules/users/interfaces/userRoutes.js';
import productRoutes from './modules/products/interfaces/productRoutes.js';
import orderRoutes from './modules/orders/interfaces/orderRoutes.js';
import paymentRoutes from './modules/payments/interfaces/paymentRoutes.js';

app.use('/api/auth', userRoutes);
app.use('/api/products', productRoutes);
app.use('/api/orders', orderRoutes);
app.use('/api/payments', paymentRoutes);
app.use('/api/users', orderRoutes); // Reusing orderRoutes for /api/users/:id/orders logic if mapped there

// Basic Route for Health Check
app.get('/health', (req, res) => {
  res.json({ status: 'ShopFlow Monolith is up and running!' });
});

// Port and Listen
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🚀 ShopFlow Monolith running on http://localhost:${PORT}`);
});

export default app;
