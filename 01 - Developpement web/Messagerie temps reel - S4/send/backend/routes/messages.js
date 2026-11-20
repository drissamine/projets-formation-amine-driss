const express = require('express');
const router = express.Router();
const { 
  sendMessage,
  getChannelMessages,
  getMessageById,
  updateMessage,
  deleteMessage,
  addReaction,
  removeReaction,
  searchMessages
} = require('../controllers/messageController');
const { authMiddleware, channelPermissionMiddleware } = require('../middleware/auth');

// @desc    Envoyer un nouveau message
// @route   POST /api/messages
// @access  Private
router.post('/', authMiddleware, sendMessage);

// @desc    Obtenir les messages d'un canal
// @route   GET /api/messages/channel/:channelId
// @access  Private
router.get('/channel/:channelId', 
  authMiddleware, 
  channelPermissionMiddleware(), 
  getChannelMessages
);

// @desc    Obtenir un message par ID
// @route   GET /api/messages/:id
// @access  Private
router.get('/:id', authMiddleware, getMessageById);

// @desc    Modifier un message
// @route   PUT /api/messages/:id
// @access  Private
router.put('/:id', authMiddleware, updateMessage);

// @desc    Supprimer un message
// @route   DELETE /api/messages/:id
// @access  Private
router.delete('/:id', authMiddleware, deleteMessage);

// @desc    Ajouter une réaction à un message
// @route   POST /api/messages/:id/reactions
// @access  Private
router.post('/:id/reactions', authMiddleware, addReaction);

// @desc    Retirer une réaction d'un message
// @route   DELETE /api/messages/:id/reactions/:emoji
// @access  Private
router.delete('/:id/reactions/:emoji', authMiddleware, removeReaction);

// @desc    Rechercher dans les messages d'un canal
// @route   GET /api/messages/search/:channelId
// @access  Private
router.get('/search/:channelId', 
  authMiddleware, 
  channelPermissionMiddleware(), 
  searchMessages
);

module.exports = router;
