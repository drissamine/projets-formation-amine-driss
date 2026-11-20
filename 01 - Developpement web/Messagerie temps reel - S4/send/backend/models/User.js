// Modèle utilisateur pour l'application de messagerie
// Définit la structure des données utilisateur dans MongoDB
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

// Schéma de l'utilisateur avec validation des champs
const userSchema = new mongoose.Schema({
  username: {  // Nom d'utilisateur unique
    type: String,
    required: true,
    unique: true,
    trim: true,
    minlength: 3,
    maxlength: 30
  },
  email: {  // Adresse email unique avec validation regex
    type: String,
    required: true,
    unique: true,
    trim: true,
    lowercase: true,
    match: [/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/, 'Veuillez entrer un email valide']
  },
  password: {  // Mot de passe haché (minimum 6 caractères)
    type: String,
    required: true,
    minlength: 6
  },
  avatar: {  // URL de l'avatar utilisateur
    type: String,
    default: ''
  },
  status: {  // Statut de présence de l'utilisateur
    type: String,
    enum: ['online', 'offline', 'away'],
    default: 'offline'
  },
  lastSeen: {  // Dernière activité de l'utilisateur
    type: Date,
    default: Date.now
  },
  oauth: {  // Informations d'authentification OAuth
    google: {
      id: { type: String, sparse: true },
      email: String,
      accessToken: String
    },
    github: {
      id: { type: String, sparse: true },
      username: String,
      email: String,
      accessToken: String
    }
  },
  isVerified: {  // Compte vérifié (pour OAuth)
    type: Boolean,
    default: false
  },
  channels: [{  // Liste des canaux auxquels l'utilisateur est abonné
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Channel'
  }]
}, {
  timestamps: true  // Ajoute automatiquement createdAt et updatedAt
});

// Hash du mot de passe avant sauvegarde
userSchema.pre('save', async function(next) {
  if (!this.isModified('password')) return next();
  
  try {
    const salt = await bcrypt.genSalt(10);
    this.password = await bcrypt.hash(this.password, salt);
    next();
  } catch (error) {
    next(error);
  }
});

// Méthode pour comparer les mots de passe
userSchema.methods.comparePassword = async function(candidatePassword) {
  return bcrypt.compare(candidatePassword, this.password);
};

// Méthode pour exclure le mot de passe et l'email dans les réponses JSON
userSchema.methods.toJSON = function() {
  const userObject = this.toObject();
  delete userObject.password;
  delete userObject.email;
  delete userObject.oauth;
  return userObject;
};

module.exports = mongoose.model('User', userSchema);
