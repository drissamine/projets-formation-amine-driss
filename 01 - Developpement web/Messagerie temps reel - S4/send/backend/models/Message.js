// Modèle message pour l'application de messagerie
// Définit la structure des messages avec support des réactions et pièces jointes
const mongoose = require('mongoose');

// Schéma du message avec support complet des fonctionnalités de chat
const messageSchema = new mongoose.Schema({
  content: {  // Contenu textuel du message
    type: String,
    required: true,
    trim: true,
    maxlength: 1000
  },
  channel: {  // Canal dans lequel le message est envoyé (référence Channel)
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Channel',
    required: true
  },
  author: {  // Auteur du message (référence User)
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  type: {  // Type de message : text, image, file ou system
    type: String,
    enum: ['text', 'image', 'file', 'system'],
    default: 'text'
  },
  attachments: [{  // Pièces jointes du message
    name: String,  // Nom du fichier
    url: String,   // URL du fichier
    type: String,  // Type MIME
    size: Number   // Taille en octets
  }],
  replyTo: {  // Message auquel celui-ci répond (référence Message)
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Message'
  },
  isEdited: {  // Indique si le message a été modifié
    type: Boolean,
    default: false
  },
  editedAt: {  // Date de dernière modification
    type: Date
  },
  isDeleted: {  // Indique si le message a été supprimé
    type: Boolean,
    default: false
  },
  deletedAt: {  // Date de suppression
    type: Date
  },
  reactions: [{  // Réactions au message
    emoji: {  // Emoji de la réaction
      type: String,
      required: true
    },
    users: [{  // Utilisateurs qui ont réagi avec cet emoji
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User'
    }],
    createdAt: {  // Date de la première réaction
      type: Date,
      default: Date.now
    }
  }],
  mentions: [{  // Utilisateurs mentionnés dans le message (référence User)
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  }]
}, {
  timestamps: true  // Ajoute automatiquement createdAt et updatedAt
});

// Index pour optimiser les requêtes
messageSchema.index({ channel: 1, createdAt: -1 });
messageSchema.index({ author: 1 });
messageSchema.index({ createdAt: -1 });

// Méthode pour ajouter une réaction
messageSchema.methods.addReaction = function(userId, emoji) {
  const existingReaction = this.reactions.find(r => r.emoji === emoji);

  if (existingReaction) {
    // Ajouter l'utilisateur s'il n'a pas déjà réagi avec cet emoji
    if (!existingReaction.users.includes(userId)) {
      existingReaction.users.push(userId);
    }
  } else {
    // Créer une nouvelle réaction
    this.reactions.push({
      emoji,
      users: [userId],
      createdAt: new Date()
    });
  }
};

// Méthode pour retirer une réaction
messageSchema.methods.removeReaction = function(userId, emoji) {
  const reaction = this.reactions.find(r => r.emoji === emoji);

  if (reaction) {
    // Retirer l'utilisateur de la liste
    reaction.users = reaction.users.filter(
      u => u.toString() !== userId.toString()
    );

    // Supprimer la réaction si plus personne ne l'utilise
    if (reaction.users.length === 0) {
      this.reactions = this.reactions.filter(r => r.emoji !== emoji);
    }
  }
};

// Méthode pour marquer le message comme supprimé
messageSchema.methods.markAsDeleted = function() {
  this.isDeleted = true;
  this.deletedAt = new Date();
  this.content = '[Message supprimé]';
};

// Méthode pour éditer le message
messageSchema.methods.edit = function(newContent) {
  this.content = newContent;
  this.isEdited = true;
  this.editedAt = new Date();
};

// Méthode statique pour obtenir les messages d'un canal
messageSchema.statics.getChannelMessages = function(channelId, limit = 50, skip = 0) {
  return this.find({ channel: channelId, isDeleted: false })
    .populate('author', 'username avatar')
    .populate('replyTo')
    .sort({ createdAt: -1 })
    .limit(limit)
    .skip(skip);
};

// Méthode pour rechercher dans les messages
messageSchema.statics.searchInChannel = function(channelId, query, limit = 20) {
  return this.find({
    channel: channelId,
    isDeleted: false,
    content: { $regex: query, $options: 'i' }
  })
    .populate('author', 'username avatar')
    .sort({ createdAt: -1 })
    .limit(limit);
};

module.exports = mongoose.model('Message', messageSchema);
