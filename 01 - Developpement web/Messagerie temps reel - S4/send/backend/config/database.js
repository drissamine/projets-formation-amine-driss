const mongoose = require('mongoose');
const User = require('../models/User');
require('dotenv').config();

const connectDB = async () => {
  try {
    const conn = await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/messagerie-app', {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });

    console.log(`MongoDB Connecté: ${conn.connection.host}`);

    // Créer un compte démo si il n'existe pas
    await createDemoUser();

    // Gestion des événements de connexion
    mongoose.connection.on('error', (err) => {
      console.error('Erreur de connexion MongoDB:', err);
    });

    mongoose.connection.on('disconnected', () => {
      console.log('MongoDB déconnecté');
    });

    // Fermer la connexion lors de l'arrêt de l'application
    process.on('SIGINT', async () => {
      await mongoose.connection.close();
      console.log('Connexion MongoDB fermée');
      process.exit(0);
    });

  } catch (error) {
    console.error('Erreur de connexion à MongoDB:', error.message);
    process.exit(1);
  }
};

// Fonction pour créer un compte démo
const createDemoUser = async () => {
  try {
    const demoEmail = 'demo@example.com';
    const existingDemo = await User.findOne({ email: demoEmail });

    if (!existingDemo) {
      const demoUser = new User({
        username: 'DemoUser',
        email: demoEmail,
        password: 'demopassword123'
      });

      await demoUser.save();
      console.log('Compte démo créé avec succès');
    } else {
      console.log('Le compte démo existe déjà');
    }
  } catch (error) {
    console.error('Erreur lors de la création du compte démo:', error);
  }
};

module.exports = connectDB;
