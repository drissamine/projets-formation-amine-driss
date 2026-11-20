const mongoose = require('mongoose');
const { Schema } = mongoose;

const messageSchema = new Schema({
  conversationId: {
    type: String,
    required: true
  },
  sender: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  receiver: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  content: {
    type: String,
    required: true,
    maxlength: 5000
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

// Générer un ID de conversation basé sur les IDs des utilisateurs
messageSchema.statics.generateConversationId = function(senderId, receiverId) {
  const ids = [senderId, receiverId].sort();
  return `${ids[0]}_${ids[1]}`;
};

// Méthode pour marquer comme lu
messageSchema.methods.markAsRead = async function() {
  this.isRead = true;
  await this.save();
};

// Index pour createdAt
messageSchema.index({ createdAt: -1 });

module.exports = mongoose.model('Message', messageSchema);