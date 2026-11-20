import express from 'express';
import { createProxyMiddleware } from 'http-proxy-middleware';
import morgan from 'morgan';
import dotenv from 'dotenv';

import { rateLimit } from 'express-rate-limit';
import jwt from 'jsonwebtoken';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Rate Limiting (Security Requirement)
const limiter = rateLimit({
	windowMs: 15 * 60 * 1000,
	max: 100,
	message: { error: 'Too many requests' }
});
app.use(limiter);

// Logging (Dumb pipe requirement by Fowler)
app.use(morgan('dev'));

// Centralized Auth Middleware
const authCheck = (req, res, next) => {
  const path = req.path;
  // Public routes
  if (path.includes('/auth/login') || path.includes('/auth/register') || (req.method === 'GET' && path === '/api/products')) {
    return next();
  }

  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Authentication required' });

  try {
    jwt.verify(token, process.env.JWT_SECRET || 'super_secret_key_shopflow_2026');
    next();
  } catch (err) {
    res.status(401).json({ error: 'Invalid token' });
  }
};
app.use(authCheck);

// Routing Table (Points d'entrée vers les microservices)
const routes = {
  '/api/auth': process.env.USER_SERVICE_URL || 'http://localhost:3001',
  '/api/users': process.env.USER_SERVICE_URL || 'http://localhost:3001',
  '/api/products': process.env.PRODUCT_SERVICE_URL || 'http://localhost:3002',
  '/api/orders': process.env.ORDER_SERVICE_URL || 'http://localhost:3003',
  '/api/payments': process.env.PAYMENT_SERVICE_URL || 'http://localhost:3004',
};

// Application des Proxies
Object.entries(routes).forEach(([path, target]) => {
  app.use(path, createProxyMiddleware({
    target,
    changeOrigin: true,
    pathRewrite: {
      [`^${path}`]: path, // On garde le préfixe pour que le service sache ce qu'il traite
    },
  }));
});

app.get('/health', (req, res) => {
  res.json({ service: 'API Gateway', status: 'OK' });
});

app.listen(PORT, () => {
  console.log(`📡 API Gateway running on http://localhost:${PORT}`);
});
