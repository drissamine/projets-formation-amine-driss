import express from 'express';
import { PrismaProductRepository } from '../infrastructure/PrismaProductRepository.js';
import { ProductService } from '../application/ProductService.js';
import { authMiddleware } from './authMiddleware.js'; // I'll need to create this for Admin check

const productRepository = new PrismaProductRepository();
const productService = new ProductService(productRepository);
const router = express.Router();

router.get('/', async (req, res) => {
  try {
    const products = await productService.listProducts(req.query);
    res.json(products);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Route for Order Service to check specific product
router.get('/:id', async (req, res) => {
  try {
    const product = await productRepository.findById(req.params.id);
    if (!product) return res.status(404).json({ error: 'Not found' });
    res.json(product);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

router.post('/', async (req, res) => {
  try {
    const product = await productService.addProduct(req.body);
    res.status(201).json(product);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// Stock update endpoint (for Order Service)
router.put('/:id/stock', async (req, res) => {
  try {
    const { stock } = req.body;
    await productRepository.updateStock(req.params.id, stock);
    res.json({ message: 'Stock updated' });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

export default router;
