import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { User } from '../domain/User.js';

export class AuthService {
  constructor(userRepository) {
    this.userRepository = userRepository;
  }

  async register({ email, password, name }) {
    const existing = await this.userRepository.findByEmail(email);
    if (existing) throw new Error('User already exists');

    const hashedPassword = await bcrypt.hash(password, 10);
    const user = User.create({ email, password: hashedPassword, name });
    
    return await this.userRepository.save(user);
  }

  async login({ email, password }) {
    const user = await this.userRepository.findByEmail(email);
    if (!user) throw new Error('Invalid credentials');

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) throw new Error('Invalid credentials');

    const token = jwt.sign(
      { userId: user.id, role: user.role },
      process.env.JWT_SECRET || 'secret_key',
      { expiresIn: '24h' }
    );

    return { token, user: { id: user.id, email: user.email, name: user.name, role: user.role } };
  }
}
