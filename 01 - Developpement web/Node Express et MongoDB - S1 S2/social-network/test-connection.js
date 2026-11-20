require('dotenv').config();
const mongoose = require('mongoose');

console.log('🧪 Test de connexion MongoDB Atlas\n');

// Fonction de test de connexion
async function testConnection() {
  try {
    console.log('📍 Configuration:');
    console.log('   URI:', process.env.MONGODB_URI || 'Non définie');
    console.log('   DEBUG:', process.env.DEBUG || 'Non défini');
    console.log('   NODE_ENV:', process.env.NODE_ENV || 'Non défini');
    console.log('');

    if (!process.env.MONGODB_URI) {
      throw new Error('❌ MONGODB_URI non définie dans les variables d\'environnement');
    }

    console.log('🔍 Test de connexion à MongoDB Atlas...');
    
    const options = {
      serverSelectionTimeoutMS: 10000,
      socketTimeoutMS: 45000,
      maxPoolSize: 10,
      retryWrites: true,
      w: 'majority'
    };

    const startTime = Date.now();
    await mongoose.connect(process.env.MONGODB_URI, options);
    const connectionTime = Date.now() - startTime;

    console.log('✅ Connexion réussie!');
    console.log('⏱️ Temps de connexion:', connectionTime + 'ms');
    console.log('📊 État de la connexion:', mongoose.connection.readyState);
    console.log('🗄️ Base de données:', mongoose.connection.name || 'Non définie');
    console.log('🌐 Hôte:', mongoose.connection.host);
    console.log('🔌 Port:', mongoose.connection.port);
    console.log('🆔 ID de connexion:', mongoose.connection.id);

    // Test de lecture simple
    console.log('\n📖 Test de lecture...');
    const admin = mongoose.connection.db.admin();
    const result = await admin.ping();
    console.log('🏓 Ping réussi:', result);

    // Test de création d'une collection temporaire
    console.log('\n🔧 Test d\'écriture...');
    const testCollection = mongoose.connection.collection('test_connection');
    await testCollection.insertOne({
      message: 'Test de connexion réussi',
      timestamp: new Date(),
      connectionTime: connectionTime
    });
    console.log('✅ Écriture de test réussie');

    // Nettoyage
    await testCollection.drop();
    console.log('🧹 Collection de test supprimée');

    console.log('\n🎉 Tous les tests sont passés avec succès!');
    
  } catch (error) {
    console.error('\n❌ Échec du test de connexion:');
    console.error('📝 Message:', error.message);
    console.error('🔍 Code:', error.code);
    console.error('📋 Stack:', error.stack);
    
    console.log('\n🔧 Suggestions:');
    console.log('1. Vérifiez que votre IP est autorisée dans MongoDB Atlas');
    console.log('2. Vérifiez que l\'utilisateur et le mot de passe sont corrects');
    console.log('3. Vérifiez que le cluster MongoDB Atlas est actif');
    console.log('4. Vérifiez que la chaîne de connexion est correcte');
    
    process.exit(1);
  } finally {
    if (mongoose.connection.readyState !== 0) {
      await mongoose.disconnect();
      console.log('\n🔌 Connexion fermée');
    }
  }
}

// Exécution du test
testConnection();
