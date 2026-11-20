const mongoose = require('mongoose');

const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/notifications';

class Database {
  async connect() {
    try {
      await mongoose.connect(MONGO_URI);
      console.log('[MongoDB] Connected to notifications database');
    } catch (error) {
      console.error('[MongoDB] Connection error:', error.message);
    }
  }
}

module.exports = new Database();
