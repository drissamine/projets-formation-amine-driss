import { PrismaProductRepository } from '../infrastructure/PrismaProductRepository.js';
import { ProductService } from '../application/ProductService.js';

const productRepository = new PrismaProductRepository();
const productService = new ProductService(productRepository);

export const getProducts = async (req, res) => {
  try {
    const filters = req.query;
    const products = await productService.listProducts(filters);
    res.json(products);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

export const createProduct = async (req, res) => {
  try {
    const product = await productService.addProduct(req.body);
    res.status(201).json(product);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
};
