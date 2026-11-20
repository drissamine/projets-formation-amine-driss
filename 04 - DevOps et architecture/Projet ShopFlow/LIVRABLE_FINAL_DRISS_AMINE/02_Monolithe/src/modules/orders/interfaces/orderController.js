import { PrismaOrderRepository } from '../infrastructure/PrismaOrderRepository.js';
import { OrderService } from '../application/OrderService.js'; // Wait, I named it AuthService by mistake? No, I should fix the filename in a bit if I did. 
import { PrismaProductRepository } from '../../products/infrastructure/PrismaProductRepository.js';
import { ProductService } from '../../products/application/ProductService.js';

// Dependencies wiring
const orderRepository = new PrismaOrderRepository();
const productRepository = new PrismaProductRepository();
const productService = new ProductService(productRepository);
const orderService = new OrderService(orderRepository, productService);

export const createOrder = async (req, res) => {
  try {
    const { items } = req.body;
    const userId = req.user.userId;
    const order = await orderService.placeOrder({ userId, items });
    res.status(201).json(order);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
};

export const getOrder = async (req, res) => {
  try {
    const order = await orderService.getOrderById(req.params.id);
    if (!order) return res.status(404).json({ error: 'Order not found' });
    res.json(order);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

export const getUserOrders = async (req, res) => {
  try {
    const orders = await orderService.getUserOrders(req.params.id);
    res.json(orders);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
