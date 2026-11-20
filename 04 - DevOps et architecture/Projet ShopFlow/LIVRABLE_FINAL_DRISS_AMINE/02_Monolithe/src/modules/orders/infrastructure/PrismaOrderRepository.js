import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export class PrismaOrderRepository {
  async save(orderData) {
    return await prisma.order.create({
      data: {
        userId: orderData.userId,
        totalAmount: orderData.totalAmount,
        status: orderData.status,
        items: {
          create: orderData.items.map(item => ({
            productId: item.productId,
            quantity: item.quantity,
            price: item.price
          }))
        }
      },
      include: { items: true }
    });
  }

  async findById(id) {
    return await prisma.order.findUnique({
      where: { id },
      include: { items: true }
    });
  }

  async findByUserId(userId) {
    return await prisma.order.findMany({
      where: { userId },
      include: { items: true },
      orderBy: { createdAt: 'desc' }
    });
  }
}
