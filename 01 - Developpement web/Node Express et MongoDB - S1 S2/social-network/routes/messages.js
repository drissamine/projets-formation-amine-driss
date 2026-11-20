const express = require('express');
const router = express.Router();
const Message = require('../models/Message');
const User = require('../models/User');
const { auth } = require('../middleware/auth');

// GET - Tous les messages d'une conversation
router.get('/:userId/conversations/:otherUserId', async (req, res) => {
  try {
    const { userId, otherUserId } = req.params;
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const skip = (page - 1) * limit;
    
    // Vérifier que les utilisateurs existent
    const user1 = await User.findById(userId);
    const user2 = await User.findById(otherUserId);
    
    if (!user1 || !user2) {
      return res.status(404).json({
        success: false,
        erreur: 'Utilisateur non trouvé'
      });
    }
    
    // Générer l'ID de conversation
    const conversationId = Message.generateConversationId(userId, otherUserId);
    
    // Récupérer les messages de la conversation
    const messages = await Message.find({ conversationId })
      .sort({ createdAt: 1 })
      .skip(skip)
      .limit(limit);
    
    const total = await Message.countDocuments({ conversationId });
    
    res.json({
      success: true,
      conversationId,
      count: messages.length,
      total,
      page,
      totalPages: Math.ceil(total / limit),
      data: messages
    });
  } catch (err) {
    res.status(500).json({ success: false, erreur: err.message });
  }
});

// POST - Envoyer un message
router.post('/', auth, async (req, res) => {
  try {
    const { receiver, content } = req.body;
    const sender = req.user.userId;
    
    if (!receiver || !content) {
      return res.status(400).json({
        success: false,
        erreur: 'Destinataire et contenu requis'
      });
    }
    
    // Vérifier que les utilisateurs existent
    const senderUser = await User.findById(sender);
    const receiverUser = await User.findById(receiver);
    
    if (!senderUser || !receiverUser) {
      return res.status(404).json({
        success: false,
        erreur: 'Utilisateur non trouvé'
      });
    }
    
    // Générer l'ID de conversation
    const conversationId = Message.generateConversationId(sender, receiver);
    
    // Créer le message
    const message = await Message.create({
      conversationId,
      sender,
      receiver,
      content
    });
    
    res.status(201).json({
      success: true,
      message: 'Message envoyé',
      data: message
    });
  } catch (err) {
    res.status(400).json({ success: false, erreur: err.message });
  }
});

// PUT - Marquer un message comme lu
router.put('/:id/read', async (req, res) => {
  try {
    const message = await Message.findById(req.params.id);
    
    if (!message) {
      return res.status(404).json({
        success: false,
        erreur: 'Message non trouvé'
      });
    }
    
    await message.markAsRead();
    
    res.json({
      success: true,
      message: 'Message marqué comme lu',
      data: message
    });
  } catch (err) {
    res.status(400).json({ success: false, erreur: err.message });
  }
});

// GET - Toutes les conversations d'un utilisateur
router.get('/:userId/conversations', auth, async (req, res) => {
  try {
    const { userId } = req.params;
    
    // Vérifier que l'utilisateur est bien celui connecté
    if (req.user.userId !== userId) {
      return res.status(403).json({
        success: false,
        erreur: 'Non autorisé à accéder à ces conversations'
      });
    }
    
    // Vérifier que l'utilisateur existe
    const user = await User.findById(userId);
    
    if (!user) {
      return res.status(404).json({
        success: false,
        erreur: 'Utilisateur non trouvé'
      });
    }
    
    // Trouver toutes les conversations où l'utilisateur est impliqué
    const messages = await Message.find({
      $or: [{ sender: userId }, { receiver: userId }]
    }).sort({ createdAt: -1 });
    
    // Extraire les IDs uniques des autres utilisateurs
    const otherUserIds = new Set();
    messages.forEach(msg => {
      if (msg.sender.toString() !== userId) {
        otherUserIds.add(msg.sender.toString());
      }
      if (msg.receiver.toString() !== userId) {
        otherUserIds.add(msg.receiver.toString());
      }
    });
    
    // Récupérer les informations des autres utilisateurs
    const otherUsers = await User.find({
      _id: { $in: Array.from(otherUserIds) }
    }).select('nom avatar');
    
    res.json({
      success: true,
      count: otherUsers.length,
      data: otherUsers
    });
  } catch (err) {
    res.status(500).json({ success: false, erreur: err.message });
  }
});

module.exports = router;