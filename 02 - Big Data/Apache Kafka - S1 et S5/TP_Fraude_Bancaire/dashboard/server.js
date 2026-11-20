// Créé par DRISS Amine
require('dotenv').config();
const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const { Kafka } = require('kafkajs');
const helmet = require('helmet');
const compression = require('compression');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

// Configuration Kafka depuis les variables d'environnement
const kafka = new Kafka({
  clientId: process.env.KAFKA_CLIENT_ID || 'fraud-dashboard',
  brokers: (process.env.KAFKA_BROKERS || 'localhost:9092').split(',')
});

const consumer = kafka.consumer({
  groupId: process.env.KAFKA_GROUP_ID || 'dashboard-group'
});

// État du dashboard
let alertCounters = {
  HIGH: 0,
  MEDIUM: 0,
  LOW: 0
};

let lastAlerts = [];
let lastAlertTimestamp = null;

// Sécurité et optimisation
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
      fontSrc: ["'self'", "https://fonts.gstatic.com"],
      scriptSrc: ["'self'", "'unsafe-inline'"],
      connectSrc: ["'self'", "ws:", "wss:"],
    },
  },
}));
app.use(compression());

// Servir les fichiers statiques
app.use(express.static('public'));

// Route principale
app.get('/', (req, res) => {
  res.sendFile(__dirname + '/public/index.html');
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    connections: io.engine.clientsCount
  });
});

// Connexion WebSocket
io.on('connection', (socket) => {
  console.log('Client connecté au dashboard');

  // Envoyer l'état initial
  socket.emit('initialState', {
    counters: alertCounters,
    lastAlerts: lastAlerts,
    lastTimestamp: lastAlertTimestamp
  });

  socket.on('disconnect', () => {
    console.log('Client déconnecté du dashboard');
  });
});

// Fonction pour traiter les alertes
function processAlert(alert) {
  // Incrémenter le compteur
  if (alert.severity in alertCounters) {
    alertCounters[alert.severity]++;
  }

  // Ajouter aux dernières alertes (garder seulement 5)
  // Note: receivedAt sera défini côté client lors de la réception WebSocket
  lastAlerts.unshift(alert);

  if (lastAlerts.length > 5) {
    lastAlerts = lastAlerts.slice(0, 5);
  }

  // Mettre à jour le timestamp
  lastAlertTimestamp = alert.timestamp;

  // Diffuser la mise à jour à tous les clients
  io.emit('alertUpdate', {
    counters: alertCounters,
    lastAlerts: lastAlerts,
    lastTimestamp: lastAlertTimestamp,
    newAlert: alert
  });
}

// Démarrage du consumer Kafka
async function startKafkaConsumer() {
  try {
    await consumer.connect();
    await consumer.subscribe({ topic: 'alertes', fromBeginning: false });

    console.log('Consumer Kafka connecté au topic "alertes"');

    await consumer.run({
      eachMessage: async ({ topic, partition, message }) => {
        try {
          const alert = JSON.parse(message.value.toString());
          console.log('Nouvelle alerte reçue:', alert);
          processAlert(alert);
        } catch (error) {
          console.error('Erreur lors du traitement de l\'alerte:', error);
        }
      },
    });
  } catch (error) {
    console.error('Erreur Kafka:', error);
  }
}

// Démarrage du serveur
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Dashboard démarré sur http://localhost:${PORT}`);
  startKafkaConsumer();
});

// Gestion des erreurs
process.on('SIGINT', async () => {
  console.log('Arrêt du dashboard...');
  await consumer.disconnect();
  process.exit(0);
});
