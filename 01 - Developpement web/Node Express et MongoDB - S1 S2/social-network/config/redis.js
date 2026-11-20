const redis = require('redis');

let isRedisConnected = false;

const redisClient = redis.createClient({
  url: process.env.REDIS_URL || 'redis://localhost:6379',
  socket: {
    reconnectStrategy: (retries) => {
      if (retries > 2) {
        console.log('Arrêt des tentatives de reconnexion à Redis.');
        return new Error('Retry Limit Reached');
      }
      return 1000; // Attend 1 seconde entre les essais
    }
  }
});

redisClient.on('error', (err) => {
  // On ne log que si c'était connecté avant ou pour le debug initial
  if (isRedisConnected) console.error('Erreur Redis:', err.message);
});

redisClient.on('connect', () => {
  isRedisConnected = true;
  console.log('Connecté à Redis');
});

redisClient.on('end', () => {
  isRedisConnected = false;
});

const connectRedis = async () => {
  try {
    await redisClient.connect();
  } catch (err) {
    isRedisConnected = false;
    console.log('⚠️ Attention: Redis n\'est pas accessible. Le cache sera désactivé.');
  }
};

// Fonction pour mettre en cache
const cacheSet = async (key, value, ttl = 3600) => {
  if (!isRedisConnected) return;
  try {
    await redisClient.set(key, JSON.stringify(value), { EX: ttl });
  } catch (err) {
    console.warn('Erreur cacheSet (ignorée):', err.message);
  }
};

// Fonction pour récupérer du cache
const cacheGet = async (key) => {
  if (!isRedisConnected) return null;
  try {
    const data = await redisClient.get(key);
    return data ? JSON.parse(data) : null;
  } catch (err) {
    console.warn('Erreur cacheGet (ignorée):', err.message);
    return null;
  }
};

// Fonction pour supprimer du cache
const cacheDel = async (key) => {
  if (!isRedisConnected) return;
  try {
    await redisClient.del(key);
  } catch (err) {
    console.warn('Erreur cacheDel (ignorée):', err.message);
  }
};

module.exports = {
  connectRedis,
  cacheSet,
  cacheGet,
  cacheDel
};