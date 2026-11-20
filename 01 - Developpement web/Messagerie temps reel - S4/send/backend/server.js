const http = require('http');
const socketIo = require('socket.io');
const app = require('./app');
require('dotenv').config();

// Configuration du serveur HTTP
const server = http.createServer(app);

// Configuration Socket.io
const io = socketIo(server, {
  cors: {
    origin: function (origin, callback) {
      // Autoriser les requêtes depuis le domaine frontend en production
      if (process.env.NODE_ENV === 'production') {
        // En production Railway, autoriser le domaine frontend (Vercel)
        const allowedOrigins = [
          process.env.FRONTEND_URL,
          'https://your-frontend-url.vercel.app'
        ].filter(Boolean);
        if (allowedOrigins.includes(origin)) {
          callback(null, true);
        } else {
          callback(new Error('Not allowed by CORS'));
        }
      } else {
        // En développement, autoriser localhost
        const allowedOrigins = ['http://localhost:3000', 'http://localhost:3001'];
        if (!origin || allowedOrigins.includes(origin)) {
          callback(null, true);
        } else {
          callback(new Error('Not allowed by CORS'));
        }
      }
    },
    methods: ['GET', 'POST'],
    credentials: true
  },
  // Configuration pour Heroku
  transports: ['polling', 'websocket'],
  allowEIO3: true
});

// Importer le service Socket.io
const socketService = require('./services/socketService');

// Initialisation des données de démonstration
const initializeDemoData = async () => {
  try {
    const User = require('./models/User');
    const Channel = require('./models/Channel');

    // Vérifier si un utilisateur démo existe déjà
    const existingDemoUser = await User.findOne({ email: 'demo@demo.com' });

    if (!existingDemoUser) {
      console.log('📝 Création du compte démo...');

      // Créer un utilisateur démo
      const demoUser = new User({
        username: 'demo',
        email: 'demo@demo.com',
        password: 'demo123' // Sera hashé automatiquement
      });

      await demoUser.save();
      console.log('✅ Compte démo créé: demo@demo.com / demo123');

      // Créer un canal général
      const generalChannel = new Channel({
        name: 'Général',
        description: 'Canal de discussion général',
        type: 'public',
        creator: demoUser._id,
        participants: [{
          user: demoUser._id,
          role: 'admin'
        }]
      });

      await generalChannel.save();
      console.log('✅ Canal "Général" créé');
    } else {
      console.log('ℹ️ Compte démo déjà existant');
    }
  } catch (error) {
    console.error('❌ Erreur lors de l\'initialisation des données démo:', error);
  }
};

// Gestion des connexions Socket.io
io.on('connection', (socket) => {
  console.log(`Nouvelle connexion Socket.io: ${socket.id}`);

  // Gérer la connexion avec authentification
  socketService.handleConnection(socket);

  // Événements Socket.io
  socket.on('join-channel', (channelId) => {
    socketService.joinChannel(socket, channelId);
  });

  socket.on('leave-channel', (channelId) => {
    socketService.leaveChannel(socket, channelId);
  });

  socket.on('send-message', (messageData) => {
    socketService.sendMessage(socket, messageData);
  });

  socket.on('edit-message', (data) => {
    socketService.editMessage(socket, data.messageId, data.newContent);
  });

  socket.on('delete-message', (messageId) => {
    socketService.deleteMessage(socket, messageId);
  });

  socket.on('add-reaction', (data) => {
    socketService.addReaction(socket, data.messageId, data.emoji);
  });

  socket.on('remove-reaction', (data) => {
    socketService.removeReaction(socket, data.messageId, data.emoji);
  });

  socket.on('change-status', (status) => {
    socketService.changeUserStatus(socket, status);
  });

  socket.on('get-online-users', () => {
    const onlineUsers = socketService.getOnlineUsers();
    socket.emit('online-users', onlineUsers);
  });

  // Gérer la déconnexion
  socket.on('disconnect', () => {
    socketService.handleDisconnection(socket);
  });

  // Erreur Socket.io
  socket.on('error', (error) => {
    console.error('Erreur Socket.io:', error);
    socket.emit('socket-error', { message: 'Erreur de communication' });
  });
});

// Gestion des erreurs du serveur
server.on('error', (error) => {
  if (error.syscall !== 'listen') {
    throw error;
  }

  const bind = typeof PORT === 'string' ? 'Pipe ' + PORT : 'Port ' + PORT;

  // Gérer les erreurs d'écoute spécifiques avec des messages conviviaux
  switch (error.code) {
    case 'EACCES':
      console.error(bind + ' requires elevated privileges');
      process.exit(1);
      break;
    case 'EADDRINUSE':
      console.error(bind + ' is already in use');
      process.exit(1);
      break;
    default:
      throw error;
  }
});

// Démarrage du serveur
const PORT = process.env.PORT || 5000;

// Initialiser les données démo puis démarrer le serveur
initializeDemoData().then(() => {
  server.listen(PORT, () => {
    console.log(`🚀 Serveur démarré sur le port ${PORT}`);
    console.log(`📡 API REST disponible sur http://localhost:${PORT}`);
    console.log(`🔌 Socket.io disponible sur ws://localhost:${PORT}`);
    console.log(`🌍 Environnement: ${process.env.NODE_ENV || 'development'}`);
    console.log(` MongoDB: ${process.env.MONGODB_URI ? 'Connecté' : 'Non configuré'}`);
    console.log(`🎮 Compte démo disponible: demo@demo.com / demo123`);
  });
}).catch((error) => {
  console.error('Erreur fatale lors de l\'initialisation:', error);
  process.exit(1);
});

// Gestion de l'arrêt propre
process.on('SIGTERM', () => {
  console.log('SIGTERM reçu, arrêt du serveur...');
  server.close(() => {
    console.log('Serveur arrêté proprement');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('SIGINT reçu, arrêt du serveur...');
  server.close(() => {
    console.log('Serveur arrêté proprement');
    process.exit(0);
  });
});

module.exports = server;
