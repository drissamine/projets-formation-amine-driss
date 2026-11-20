const mongoose = require('mongoose');
const bcryptjs = require('bcryptjs');
const { Schema } = mongoose;

const userSchema = new Schema({
  nom: {
    type: String,
    required: [true, 'Nom obligatoire'],
    minlength: [2, 'Minimum 2 caracteres'],
    maxlength: [50, 'Maximum 50 caracteres']
  },
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    match: [/^\S+@\S+\.\S+$/, 'Email invalide']
  },
  motDePasse: {
    type: String,
    required: true,
    minlength: 6,
    select: false
  },
  bio: {
    type: String,
    maxlength: 500,
    default: ''
  },
  avatar: {
    type: String,
    default: 'https://via.placeholder.com/150'
  },
  dateNaissance: Date,
  localisation: String,

  // Statistiques
  nombreFollowers: { type: Number, default: 0 },
  nombreFollowing: { type: Number, default: 0 },
  nombrePosts: { type: Number, default: 0 },

  // Relations
  followers: [{
    type: Schema.Types.ObjectId,
    ref: 'User'
  }],
  following: [{
    type: Schema.Types.ObjectId,
    ref: 'User'
  }],

  createdAt: { type: Date, default: Date.now }
}, { timestamps: true });

// Index pour la recherche par nom
userSchema.index({ nom: 'text' });

// Index pour l'email et createdAt
userSchema.index({ email: 1 }, { unique: true });
userSchema.index({ createdAt: -1 });



// Methode: Comparer les mots de passe
userSchema.methods.comparePassword = async function (motDePasseText) {
  return await bcryptjs.compare(motDePasseText, this.motDePasse);
};

// Enlever mot de passe dans responses
userSchema.methods.toJSON = function () {
  const obj = this.toObject();
  delete obj.motDePasse;
  return obj;
};

module.exports = mongoose.model('User', userSchema);
