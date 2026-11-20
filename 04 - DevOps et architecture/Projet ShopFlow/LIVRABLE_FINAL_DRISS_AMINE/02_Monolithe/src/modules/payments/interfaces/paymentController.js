import { PaymentService } from '../application/PaymentService.js';

const paymentService = new PaymentService();

export const simPayment = async (req, res) => {
  try {
    const { orderId, amount } = req.body;
    const payment = await paymentService.processPayment({ orderId, amount });
    res.status(201).json(payment);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
};
