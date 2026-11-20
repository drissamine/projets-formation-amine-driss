import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export class PrismaProductRepository {
  async findAll({ category, minPrice, maxPrice }) {
    const where = {};
    if (category) where.category = category;
    if (minPrice || maxPrice) {
      where.price = {};
      if (minPrice) where.price.gte = parseFloat(minPrice);
      if (maxPrice) where.price.lte = parseFloat(maxPrice);
    }
    return await prisma.product.findMany({ where });
  }

  async findById(id) {
    return await prisma.product.findUnique({ where: { id } });
  }

  async create(product) {
    return await prisma.product.create({ data: product });
  }

  async updateStock(id, newStock) {
    return await prisma.product.update({
      where: { id },
      data: { stock: newStock }
    });
  }
}
