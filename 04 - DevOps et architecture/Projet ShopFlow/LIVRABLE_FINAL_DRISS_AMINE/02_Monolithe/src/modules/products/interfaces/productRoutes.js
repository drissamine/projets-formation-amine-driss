import express from 'express';
import { getProducts, createProduct } from './productController.js';
import { authMiddleware, adminOnly } from '../../../shared/authMiddleware.js';

const router = express.Router();

router.get('/', getProducts);
router.post('/', authMiddleware, adminOnly, createProduct);

export default router;
