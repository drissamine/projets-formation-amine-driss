import { Product } from '../domain/Product.js';

export class ProductService {
  constructor(productRepository) {
    this.productRepository = productRepository;
  }

  async listProducts(filters) {
    return await this.productRepository.findAll(filters);
  }

  async addProduct(data) {
    // Validation: Price > 0, Stock >= 0
    if (data.price <= 0) throw new Error('Price must be positive');
    if (data.stock < 0) throw new Error('Stock cannot be negative');

    return await this.productRepository.create(data);
  }
}
