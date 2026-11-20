const mongoose = require('mongoose');
const { Schema } = mongoose;

const postSchema = new Schema({
  contenu: {
    type: String,
    required: [true, 'Contenu obligatoire'],
    maxlength: [5000, 'Maximum 5000 caracteres']
  },
    
  auteur: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
    
  // Donnees imbriquees de l'auteur (pour affichage rapide)
  auteurInfo: {
    nom: String,
    avatar: String
  },
    
  // Commentaires imbriques
  commentaires: [{
    auteur: {
      type: Schema.Types.ObjectId,
      ref: 'User'
    },
    nom: String,
    avatar: String,
    texte: String,
    dateCommentaire: { type: Date, default: Date.now }
  }],
    
  // Likes: IDs d'utilisateurs
  likes: [{
    type: Schema.Types.ObjectId,
    ref: 'User'
  }],
  nombreLikes: { type: Number, default: 0 },
    
  // Partages
  partages: [{
    type: Schema.Types.ObjectId,
    ref: 'User'
  }],
  nombrePartages: { type: Number, default: 0 },
    
  // Images
  images: [String],
    
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

// Index pour la recherche par contenu
postSchema.index({ contenu: 'text' });

// Index pour createdAt
postSchema.index({ createdAt: -1 });

// PRE-HOOK: Remplir auteurInfo avant sauvegarder
postSchema.pre('save', async function(next) {
  if (this.isNew && this.auteur) {
    const User = mongoose.model('User');
    const user = await User.findById(this.auteur).select('nom avatar');
    if (user) {
      this.auteurInfo = {
        nom: user.nom,
        avatar: user.avatar
      };
    }
  }
  next();
});

module.exports = mongoose.model('Post', postSchema);
