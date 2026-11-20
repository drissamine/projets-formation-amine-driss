import express from 'express';
import { createOrder, getOrder, getUserOrders } from './orderController.js';
import { authMiddleware } from '../../../shared/authMiddleware.js';

const router = express.Router();

router.post('/', authMiddleware, createOrder);
router.get('/:id', authMiddleware, getOrder);
router.get('/user/:id', authMiddleware, getUserOrders);

export default router;
