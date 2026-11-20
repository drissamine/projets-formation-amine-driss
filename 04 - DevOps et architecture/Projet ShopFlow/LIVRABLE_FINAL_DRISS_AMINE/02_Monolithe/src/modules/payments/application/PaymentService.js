import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export class PaymentService {
  async processPayment({ orderId, amount }) {
    // Simulation: Success for even amounts, fail for odd? No, simple success for now.
    const transactionId = `TXN-${Math.random().toString(36).substr(2, 9).toUpperCase()}`;
    
    // Create payment entry
    const payment = await prisma.payment.create({
      data: {
        orderId,
        amount,
        transactionId,
        status: 'SUCCESS'
      }
    });

    // Update Order status
    await prisma.order.update({
      where: { id: orderId },
      data: { status: 'CONFIRMED' }
    });

    return payment;
  }
}
