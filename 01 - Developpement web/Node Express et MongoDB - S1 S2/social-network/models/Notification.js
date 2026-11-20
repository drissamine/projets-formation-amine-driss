const mongoose = require('mongoose');
const { Schema } = mongoose;

const notificationSchema = new Schema({
  userId: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  type: {
    type: String,
    enum: ['nouveau_follower', 'like', 'commentaire'],
    required: true
  },
  referenceId: {
    type: Schema.Types.ObjectId,
    required: true
  },
  message: {
    type: String,
    required: true
  },
  isRead: {
    type: Boolean,
    default: false
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

// Méthode pour marquer comme lu
notificationSchema.methods.markAsRead = async function() {
  this.isRead = true;
  await this.save();
};

// Méthode pour marquer comme non lu
notificationSchema.methods.markAsUnread = async function() {
  this.isRead = false;
  await this.save();
};

module.exports = mongoose.model('Notification', notificationSchema);