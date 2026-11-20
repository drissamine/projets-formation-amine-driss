const mongoose = require('mongoose'); 

async function connectDB() { 
  try { 
    const mongoURL = process.env.MONGODB_URI || 'mongodb://localhost:27017/social-network';
    
    console.log('🔍 Tentative de connexion à MongoDB...');
    console.log('📍 URI utilisée:', mongoURL);
    
    // Options de connexion optimisées pour MongoDB Atlas
    const options = {
      serverSelectionTimeoutMS: 10000, // 10 secondes pour la sélection du serveur
      socketTimeoutMS: 45000, // 45 secondes pour les sockets
      maxPoolSize: 10, // Taille maximale du pool de connexions
      retryWrites: true,
      w: 'majority'
    };
    
    console.log('⚙️ Options de connexion:', options);
    
    // Connexion à MongoDB
    await mongoose.connect(mongoURL, options);
    
    console.log('✅ Connecté avec succès à MongoDB!');
    console.log('📊 État de la connexion:', mongoose.connection.readyState);
    console.log('🗄️ Nom de la base:', mongoose.connection.name);
    console.log('🌐 Hôte:', mongoose.connection.host);
    console.log('🔌 Port:', mongoose.connection.port);
    
    // Événements de connexion pour le debugging
    mongoose.connection.on('connected', () => {
      console.log('🔗 Mongoose connecté à MongoDB');
    });
    
    mongoose.connection.on('error', (err) => {
      console.error('❌ Erreur Mongoose:', err);
    });
    
    mongoose.connection.on('disconnected', () => {
      console.log('🔌 Mongoose déconnecté de MongoDB');
    });
    
  } catch (err) { 
    console.error('❌ Erreur connexion MongoDB:', err.message);
    console.error('📝 Détails de l\'erreur:', err);
    
    // Afficher des conseils de dépannage
    console.log('\n🔧 Conseils de dépannage:');
    console.log('1. Vérifiez que MongoDB Atlas est accessible');
    console.log('2. Assurez-vous que votre IP est autorisée dans Network Access');
    console.log('3. Vérifiez que l\'URI de connexion est correcte');
    console.log('4. Vérifiez que l\'utilisateur et le mot de passe sont corrects');
    
    process.exit(1); 
  } 
} 

module.exports = connectDB;
