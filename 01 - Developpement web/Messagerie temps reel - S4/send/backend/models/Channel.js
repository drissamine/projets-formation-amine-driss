// Modèle canal pour l'application de messagerie
// Définit la structure des canaux de discussion
const mongoose = require('mongoose');

// Schéma du canal avec gestion des participants et permissions
const channelSchema = new mongoose.Schema({
  name: {  // Nom du canal
    type: String,
    required: true,
    trim: true,
    maxlength: 50
  },
  description: {  // Description optionnelle du canal
    type: String,
    trim: true,
    maxlength: 200
  },
  type: {  // Type de canal : public, privé ou direct
    type: String,
    enum: ['public', 'private', 'direct'],
    default: 'public'
  },
  creator: {  // Créateur du canal (référence User)
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  participants: [{  // Liste des participants avec leurs rôles
    user: {  // Référence vers l'utilisateur
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true
    },
    role: {  // Rôle dans le canal : admin ou member
      type: String,
      enum: ['admin', 'member'],
      default: 'member'
    },
    joinedAt: {  // Date d'adhésion au canal
      type: Date,
      default: Date.now
    }
  }],
  isActive: {  // Indique si le canal est actif
    type: Boolean,
    default: true
  },
  lastMessage: {  // Dernier message envoyé (référence Message)
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Message'
  }
}, {
  timestamps: true  // Ajoute automatiquement createdAt et updatedAt
});

// Index pour la recherche
channelSchema.index({ name: 'text', description: 'text' });

// Méthode pour ajouter un participant
channelSchema.methods.addParticipant = function(userId, role = 'member') {
  const existingParticipant = this.participants.find(
    p => p.user.toString() === userId.toString()
  );
  
  if (!existingParticipant) {
    this.participants.push({
      user: userId,
      role: role,
      joinedAt: new Date()
    });
  }
};

// Méthode pour retirer un participant
channelSchema.methods.removeParticipant = function(userId) {
  this.participants = this.participants.filter(
    p => p.user.toString() !== userId.toString()
  );
};

// Méthode pour vérifier si un utilisateur est participant
channelSchema.methods.isParticipant = function(userId) {
  return this.participants.some(
    p => p.user.toString() === userId.toString()
  );
};

// Méthode pour vérifier si un utilisateur est admin
channelSchema.methods.isAdmin = function(userId) {
  const participant = this.participants.find(
    p => p.user.toString() === userId.toString()
  );
  return participant && participant.role === 'admin';
};

module.exports = mongoose.model('Channel', channelSchema);
