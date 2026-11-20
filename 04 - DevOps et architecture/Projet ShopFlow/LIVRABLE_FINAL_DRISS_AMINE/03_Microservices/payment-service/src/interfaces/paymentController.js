import express from 'express';
import { PaymentService } from '../application/PaymentService.js';
import { authMiddleware } from './authMiddleware.js';

const paymentService = new PaymentService();
const router = express.Router();

router.post('/', authMiddleware, async (req, res) => {
  try {
    const { orderId, amount } = req.body;
    const payment = await paymentService.processPayment({ orderId, amount });
    res.status(201).json(payment);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

export default router;
