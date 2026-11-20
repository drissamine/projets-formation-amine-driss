import { PrismaUserRepository } from '../infrastructure/PrismaUserRepository.js';
import { AuthService } from '../application/AuthService.js';
import express from 'express';

const userRepository = new PrismaUserRepository();
const authService = new AuthService(userRepository);
const router = express.Router();

router.post('/register', async (req, res) => {
  try {
    const user = await authService.register(req.body);
    res.status(201).json({ id: user.id, email: user.email });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

router.post('/login', async (req, res) => {
  try {
    const result = await authService.login(req.body);
    res.json(result);
  } catch (err) {
    res.status(401).json({ error: err.message });
  }
});

export default router;
