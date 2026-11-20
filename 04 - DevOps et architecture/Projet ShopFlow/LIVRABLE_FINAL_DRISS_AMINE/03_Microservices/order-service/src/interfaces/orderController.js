import express from 'express';
import { PrismaOrderRepository } from '../infrastructure/PrismaOrderRepository.js';
import { OrderService } from '../application/OrderService.js';
import { authMiddleware } from './authMiddleware.js';

const orderRepository = new PrismaOrderRepository();
const orderService = new OrderService(orderRepository);
const router = express.Router();

router.post('/', authMiddleware, async (req, res) => {
  try {
    const { items } = req.body;
    const userId = req.user.userId;
    const order = await orderService.placeOrder({ userId, items });
    res.status(201).json(order);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

router.get('/:id', authMiddleware, async (req, res) => {
  try {
    const order = await orderService.getOrderById(req.params.id);
    if (!order) return res.status(404).json({ error: 'Order not found' });
    res.json(order);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.get('/user/:id', authMiddleware, async (req, res) => {
  try {
    const orders = await orderService.getUserOrders(req.params.id);
    res.json(orders);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Internal endpoint for Payment Service
router.put('/:id/confirm', async (req, res) => {
  try {
    await orderRepository.updateStatus(req.params.id, 'CONFIRMED');
    res.json({ message: 'Order confirmed' });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

export default router;
