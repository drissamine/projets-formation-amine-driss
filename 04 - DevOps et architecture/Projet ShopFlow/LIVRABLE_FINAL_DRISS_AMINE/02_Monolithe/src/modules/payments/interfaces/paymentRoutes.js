import express from 'express';
import { simPayment } from './paymentController.js';
import { authMiddleware } from '../../../shared/authMiddleware.js';

const router = express.Router();

router.post('/', authMiddleware, simPayment);

export default router;
