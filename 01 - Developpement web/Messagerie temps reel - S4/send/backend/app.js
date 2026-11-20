const express = require('express');
const path = require('path');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const connectDB = require('./config/database');

// Charger les variables d'environnement
require('dotenv').config();

const app = express();

// Connecter à la base de données
connectDB();

// Middleware de sécurité
app.use(helmet({
  crossOriginEmbedderPolicy: false,
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
}));

// Configuration CORS
app.use(cors({
  origin: function (origin, callback) {
    // En production Heroku, autoriser le domaine frontend
    if (process.env.NODE_ENV === 'production') {
      const allowedOrigins = [
        'https://driss-app-messagerie-d9e447e9f569.herokuapp.com',
        'https://driss-app-messagerie.vercel.app'
      ].filter(Boolean);
      
      // Autoriser les requêtes sans origine (comme mobile apps, curl, etc.)
      if (!origin) return callback(null, true);
      
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
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// Limitation du taux de requêtes
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: process.env.NODE_ENV === 'production' ? 1000 : 5000, // limite chaque IP à 1000 requêtes en prod, 5000 en dev
  message: {
    success: false,
    message: 'Trop de requêtes depuis cette IP, veuillez réessayer plus tard.'
  },
  standardHeaders: true,
  legacyHeaders: false,
  // Configuration pour Heroku
  trustProxy: true,
  skip: (req) => {
    // Ne pas limiter les requêtes depuis localhost en développement
    return process.env.NODE_ENV !== 'production' && req.ip === '127.0.0.1';
  }
});

app.use('/api/', limiter);

// Rate limit plus strict pour l'authentification
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: process.env.NODE_ENV === 'production' ? 100 : 500, // limite chaque IP à 100 tentatives en prod, 500 en dev
  message: {
    success: false,
    message: 'Trop de tentatives de connexion, veuillez réessayer plus tard.'
  },
  skipSuccessfulRequests: true,
  // Configuration pour Heroku
  trustProxy: true,
});

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Middleware de journalisation
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// Servir les fichiers statiques du frontend en production
if (process.env.NODE_ENV === 'production') {
  app.use(express.static(path.join(__dirname, '../frontend/build')));
}

// Routes
app.use('/api/auth', authLimiter, require('./routes/auth'));
app.use('/api/channels', require('./routes/channels'));
app.use('/api/messages', require('./routes/messages'));

// Route de test
app.get('/api/health', (req, res) => {
  res.json({
    success: true,
    message: 'Serveur fonctionne correctement',
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development'
  });
});

// Servir l'application React pour toutes les autres routes (SPA routing)
if (process.env.NODE_ENV === 'production') {
  app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, '../frontend/build/index.html'));
  });
} else {
  // Route par défaut en développement
  app.get('/', (req, res) => {
    res.json({
      success: true,
      message: 'API de l\'application de messagerie',
      version: '1.0.0',
      endpoints: {
        auth: '/api/auth',
        health: '/api/health'
      }
    });
  });
}

// Middleware de gestion d'erreurs
app.use((err, req, res, next) => {
  console.error('Erreur non gérée:', err.stack);
  
  // Erreur de validation Mongoose
  if (err.name === 'ValidationError') {
    const errors = Object.values(err.errors).map(val => val.message);
    return res.status(400).json({
      success: false,
      message: 'Erreur de validation',
      errors
    });
  }
  
  // Erreur de duplication Mongoose
  if (err.code === 11000) {
    const field = Object.keys(err.keyValue)[0];
    return res.status(400).json({
      success: false,
      message: `Le ${field} existe déjà`
    });
  }
  
  // Erreur de Cast (ID invalide)
  if (err.name === 'CastError') {
    return res.status(400).json({
      success: false,
      message: 'ID invalide'
    });
  }
  
  // Erreur par défaut
  res.status(err.status || 500).json({
    success: false,
    message: err.message || 'Erreur interne du serveur'
  });
});

// Middleware pour les routes non trouvées
app.use('*', (req, res) => {
  res.status(404).json({
    success: false,
    message: 'Route non trouvée'
  });
});

module.exports = app;
