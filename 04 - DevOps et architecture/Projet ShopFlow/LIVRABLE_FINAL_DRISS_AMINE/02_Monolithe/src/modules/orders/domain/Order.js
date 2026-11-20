export class Order {
  constructor({ id, userId, status, totalAmount, items, createdAt }) {
    this.id = id;
    this.userId = userId;
    this.status = status || 'PENDING';
    this.totalAmount = totalAmount;
    this.items = items || [];
    this.createdAt = createdAt;
  }
}

export class OrderLine {
  constructor({ productId, quantity, price }) {
    this.productId = productId;
    this.quantity = quantity;
    this.price = price;
  }
}
