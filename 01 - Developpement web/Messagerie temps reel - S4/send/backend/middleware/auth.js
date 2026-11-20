const { verifyToken } = require('../utils/jwt');
const User = require('../models/User');

/**
 * Middleware d'authentification
 * Vérifie que l'utilisateur possède un token JWT valide
 */
const authMiddleware = async (req, res, next) => {
  try {
    // Récupérer le token du header Authorization
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({
        success: false,
        message: 'Token d\'authentification manquant'
      });
    }

    // Extraire le token
    const token = authHeader.split(' ')[1];

    // Vérifier le token
    const decoded = verifyToken(token);

    // Récupérer l'utilisateur depuis la base de données
    const user = await User.findById(decoded.userId).select('-password');
    
    if (!user) {
      return res.status(401).json({
        success: false,
        message: 'Utilisateur non trouvé'
      });
    }

    // Ajouter l'utilisateur à la requête
    req.user = user;
    next();
  } catch (error) {
    return res.status(401).json({
      success: false,
      message: 'Token invalide ou expiré'
    });
  }
};

/**
 * Middleware optionnel d'authentification
 * Ne bloque pas si pas de token, mais ajoute l'utilisateur si présent
 */
const optionalAuth = async (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;
    
    if (authHeader && authHeader.startsWith('Bearer ')) {
      const token = authHeader.split(' ')[1];
      const decoded = verifyToken(token);
      const user = await User.findById(decoded.userId).select('-password');
      if (user) {
        req.user = user;
      }
    }
    next();
  } catch (error) {
    // Continuer sans authentification
    next();
  }
};

/**
 * Middleware de vérification des permissions de canal
 * Vérifie que l'utilisateur a accès au canal spécifié
 */
const channelPermissionMiddleware = (requiredRole = 'member') => {
  return async (req, res, next) => {
    try {
      const Channel = require('../models/Channel');
      const channelId = req.params.channelId || req.body.channelId;
      
      if (!channelId) {
        return res.status(400).json({
          success: false,
          message: 'ID du canal requis'
        });
      }

      const channel = await Channel.findById(channelId);
      
      if (!channel) {
        return res.status(404).json({
          success: false,
          message: 'Canal non trouvé'
        });
      }

      // Vérifier si l'utilisateur est participant
      const participant = channel.participants.find(
        p => p.user.toString() === req.user._id.toString()
      );

      if (!participant) {
        return res.status(403).json({
          success: false,
          message: 'Accès refusé. Vous n\'êtes pas membre de ce canal.'
        });
      }

      // Vérifier le rôle si requis
      if (requiredRole === 'admin' && participant.role !== 'admin') {
        return res.status(403).json({
          success: false,
          message: 'Accès refusé. Privilèges administrateur requis.'
        });
      }

      req.channel = channel;
      req.participantRole = participant.role;
      next();
    } catch (error) {
      return res.status(500).json({
        success: false,
        message: 'Erreur lors de la vérification des permissions'
      });
    }
  };
};

module.exports = {
  authMiddleware,
  optionalAuth,
  channelPermissionMiddleware
};
