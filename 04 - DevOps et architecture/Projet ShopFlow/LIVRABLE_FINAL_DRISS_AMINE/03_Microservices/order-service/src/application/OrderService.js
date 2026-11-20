import { Order, OrderLine } from '../domain/Order.js';
import Redis from 'ioredis';

const redis = new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379,
});

export class OrderService {
  constructor(orderRepository) {
    this.orderRepository = orderRepository;
    this.PRODUCT_SERVICE_URL = process.env.PRODUCT_SERVICE_URL || 'http://localhost:3002';
  }

  async placeOrder({ userId, items }) {
    let totalAmount = 0;
    const orderLines = [];

    for (const item of items) {
      // Internal call to Product Service
      const response = await fetch(`${this.PRODUCT_SERVICE_URL}/${item.productId}`);
      if (!response.ok) throw new Error(`Product ${item.productId} not found`);
      const product = await response.json();

      if (product.stock < item.quantity) throw new Error(`Insufficient stock for ${product.name}`);

      totalAmount += product.price * item.quantity;
      orderLines.push(new OrderLine({
        productId: product.id,
        quantity: item.quantity,
        price: product.price
      }));

      // Update stock via Product Service API
      await fetch(`${this.PRODUCT_SERVICE_URL}/${product.id}/stock`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ stock: product.stock - item.quantity })
      });
    }

    const order = new Order({
      userId,
      totalAmount,
      items: orderLines
    });

    const savedOrder = await this.orderRepository.save(order);

    // Async Notification via Redis
    redis.publish('shopflow_notifications', JSON.stringify({
        type: 'ORDER_PLACED',
        data: {
            orderId: savedOrder.id,
            userId: savedOrder.userId,
            amount: savedOrder.totalAmount
        }
    }));

    return savedOrder;
  }

  async getOrderById(id) {
    return await this.orderRepository.findById(id);
  }

  async getUserOrders(userId) {
    return await this.orderRepository.findByUserId(userId);
  }
}
