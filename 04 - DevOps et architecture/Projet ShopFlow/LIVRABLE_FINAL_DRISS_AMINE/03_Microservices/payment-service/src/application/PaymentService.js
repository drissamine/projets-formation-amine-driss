import { PrismaClient } from '@prisma/client';
import Redis from 'ioredis';

const prisma = new PrismaClient();
const redis = new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379,
});

export class PaymentService {
  constructor() {
    this.ORDER_SERVICE_URL = process.env.ORDER_SERVICE_URL || 'http://localhost:3003';
  }

  async processPayment({ orderId, amount }) {
    const transactionId = `TXN-${Math.random().toString(36).substr(2, 9).toUpperCase()}`;
    
    // Create payment entry in its own DB
    const payment = await prisma.payment.create({
      data: {
        orderId,
        amount,
        transactionId,
        status: 'SUCCESS'
      }
    });

    // Notify Order Service to update status (Internal HTTP call)
    await fetch(`${this.ORDER_SERVICE_URL}/orders/${orderId}/confirm`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' }
    });

    // Async Notification via Redis
    redis.publish('shopflow_notifications', JSON.stringify({
        type: 'PAYMENT_SUCCESS',
        data: {
            orderId: payment.orderId,
            amount: payment.amount
        }
    }));

    return payment;
  }
}
