const mongoose = require('mongoose');

const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/appointments';

class Database {
  async connect() {
    try {
      await mongoose.connect(MONGO_URI);
      console.log('[MongoDB] Connected to appointments database');
    } catch (error) {
      console.error('[MongoDB] Connection error:', error.message);
    }
  }
}

module.exports = new Database();
