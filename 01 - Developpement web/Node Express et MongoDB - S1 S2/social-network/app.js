require('dotenv').config();
const express = require('express');
const cors = require('cors');
const connectDB = require('./config/mongodb');
const { connectRedis } = require('./config/redis');
const User = require('./models/User');
const Post = require('./models/Post');
const Notification = require('./models/Notification');
const Message = require('./models/Message');
console.log('Resolving users route:', require.resolve('./routes/users'));
const usersRoutes = require('./routes/users');
const postsRoutes = require('./routes/posts');
const searchRoutes = require('./routes/search');
const messagesRoutes = require('./routes/messages');
const statsRoutes = require('./routes/stats');
const uploadRoutes = require('./routes/upload');

const app = express();

// Connexion BD
connectDB();

// Connexion Redis
connectRedis();

// Rendre les modèles disponibles dans l'app
app.locals.User = User;
app.locals.Post = Post;
app.locals.Notification = Notification;
app.locals.Message = Message;

// Middlewares 
app.use(cors());
app.use(express.json());

// Routes API
app.use('/api/users', usersRoutes);
app.use('/api/posts', postsRoutes);
app.use('/api/search', searchRoutes);
app.use('/api/messages', messagesRoutes);
app.use('/api/stats', statsRoutes);
app.use('/api/upload', uploadRoutes);

// Route test
app.get('/', (req, res) => {
  res.json({
    message: 'API Reseau Social',
    routes: {
      users: '/api/users',
      posts: '/api/posts'
    },
    models: {
      User: 'Disponible via app.locals.User',
      Post: 'Disponible via app.locals.Post'
    }
  });
});

// Route pour favicon.ico
app.get('/favicon.ico', (req, res) => {
  res.status(204).end();
});

// Erreur 404 
app.use((req, res) => {
  res.status(404).json({ erreur: 'Route non trouvee' });
});

// Demarrer 

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Serveur sur http://localhost:${PORT}`);
  console.log('Modèles disponibles:');
  console.log('- User:', User.modelName);
  console.log('- Post:', Post.modelName);
  console.log('Routes disponibles:');
  console.log('- /api/users (CRUD + gestion followers + notifications)');
  console.log('- /api/posts (CRUD + likes + commentaires)');
  console.log('- /api/search (recherche globale)');
  console.log('- /api/messages (messagerie privée)');
  console.log('- /api/stats (statistiques)');
  console.log('- /api/upload (upload d\'images)');
});
