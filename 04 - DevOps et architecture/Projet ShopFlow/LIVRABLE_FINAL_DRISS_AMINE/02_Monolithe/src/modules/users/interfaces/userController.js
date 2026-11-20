import { PrismaUserRepository } from '../infrastructure/PrismaUserRepository.js';
import { AuthService } from '../application/AuthService.js';

const userRepository = new PrismaUserRepository();
const authService = new AuthService(userRepository);

export const register = async (req, res) => {
  try {
    const { email, password, name } = req.body;
    const user = await authService.register({ email, password, name });
    res.status(201).json({ message: 'User registered', userId: user.id });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
};

export const login = async (req, res) => {
  try {
    const { email, password } = req.body;
    const result = await authService.login({ email, password });
    res.json(result);
  } catch (err) {
    res.status(401).json({ error: err.message });
  }
};
