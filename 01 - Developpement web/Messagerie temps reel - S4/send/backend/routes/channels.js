const express = require('express');
const router = express.Router();
const {
  createChannel,
  getUserChannels,
  getChannelById,
  joinChannel,
  leaveChannel,
  updateChannel,
  deleteChannel,
  searchChannels,
  createOrGetDirectChannel,
  getUsers
} = require('../controllers/channelController');
const { authMiddleware } = require('../middleware/auth');

// Toutes les routes de canaux nécessitent une authentification
router.use(authMiddleware);

// @desc    Obtenir tous les utilisateurs (pour les messages directs)
// @route   GET /api/channels/users
// @access  Private
router.get('/users', getUsers);

// @desc    Rechercher des canaux
// @route   GET /api/channels/search
// @access  Private
router.get('/search', searchChannels);

// @desc    Obtenir tous les canaux de l'utilisateur
// @route   GET /api/channels
// @access  Private
router.get('/', getUserChannels);

// @desc    Créer un nouveau canal
// @route   POST /api/channels
// @access  Private
router.post('/', createChannel);

// @desc    Obtenir un canal par ID
// @route   GET /api/channels/:id
// @access  Private
router.get('/:id', getChannelById);

// @desc    Mettre à jour un canal
// @route   PUT /api/channels/:id
// @access  Private
router.put('/:id', updateChannel);

// @desc    Supprimer un canal
// @route   DELETE /api/channels/:id
// @access  Private
router.delete('/:id', deleteChannel);

// @desc    Rejoindre un canal
// @route   POST /api/channels/:id/join
// @access  Private
router.post('/:id/join', joinChannel);

// @desc    Quitter un canal
// @route   POST /api/channels/:id/leave
// @access  Private
router.post('/:id/leave', leaveChannel);

// @desc    Créer ou retrouver un canal direct avec un utilisateur
// @route   POST /api/channels/direct/:userId
// @access  Private
router.post('/direct/:userId', createOrGetDirectChannel);

module.exports = router;
