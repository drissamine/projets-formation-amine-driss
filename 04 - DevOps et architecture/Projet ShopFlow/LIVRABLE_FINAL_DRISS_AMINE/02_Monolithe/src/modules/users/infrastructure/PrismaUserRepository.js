import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export class PrismaUserRepository {
  async findByEmail(email) {
    return await prisma.user.findUnique({ where: { email } });
  }

  async findById(id) {
    return await prisma.user.findUnique({ where: { id } });
  }

  async save(user) {
    return await prisma.user.create({
      data: {
        email: user.email,
        password: user.password,
        name: user.name,
        role: user.role
      }
    });
  }
}
