import { Order, OrderLine } from '../domain/Order.js';

export class OrderService {
  constructor(orderRepository, productService) {
    this.orderRepository = orderRepository;
    this.productService = productService;
  }

  async placeOrder({ userId, items }) {
    let totalAmount = 0;
    const orderLines = [];

    for (const item of items) {
      const product = await this.productService.productRepository.findById(item.productId);
      if (!product) throw new Error(`Product ${item.productId} not found`);
      if (product.stock < item.quantity) throw new Error(`Insufficient stock for ${product.name}`);

      totalAmount += product.price * item.quantity;
      orderLines.push(new OrderLine({
        productId: product.id,
        quantity: item.quantity,
        price: product.price
      }));

      // Update stock (Simple implementation for monolith)
      await this.productService.productRepository.updateStock(product.id, product.stock - item.quantity);
    }

    const order = new Order({
      userId,
      totalAmount,
      items: orderLines
    });

    return await this.orderRepository.save(order);
  }

  async getOrderById(id) {
    return await this.orderRepository.findById(id);
  }

  async getUserOrders(userId) {
    return await this.orderRepository.findByUserId(userId);
  }
}
