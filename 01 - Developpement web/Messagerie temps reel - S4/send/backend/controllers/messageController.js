const Message = require('../models/Message');
const Channel = require('../models/Channel');

// @desc    Envoyer un nouveau message
// @route   POST /api/messages
// @access  Private
const sendMessage = async (req, res) => {
  try {
    const { content, channelId, type = 'text', attachments = [] } = req.body;

    // Validation des données
    if (!content || !channelId) {
      return res.status(400).json({
        success: false,
        message: 'Le contenu et l\'ID du canal sont requis.'
      });
    }

    // Vérifier si le canal existe et si l'utilisateur est membre
    const channel = await Channel.findById(channelId);
    if (!channel) {
      return res.status(404).json({
        success: false,
        message: 'Canal non trouvé.'
      });
    }

    if (!channel.isParticipant(req.user._id)) {
      return res.status(403).json({
        success: false,
        message: 'Vous n\'êtes pas membre de ce canal.'
      });
    }

    // Créer le message
    const message = new Message({
      content: content.trim(),
      author: req.user._id,
      channel: channelId,
      type,
      attachments
    });

    await message.save();

    // Mettre à jour le dernier message du canal
    channel.lastMessage = message._id;
    await channel.save();

    // Populer les données pour la réponse
    await message.populate('author', 'username avatar');

    res.status(201).json({
      success: true,
      message: 'Message envoyé avec succès.',
      data: {
        message
      }
    });

  } catch (error) {
    console.error('Erreur lors de l\'envoi du message:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de l\'envoi du message.'
    });
  }
};

// @desc    Obtenir les messages d'un canal
// @route   GET /api/messages/channel/:channelId
// @access  Private
const getChannelMessages = async (req, res) => {
  try {
    const { channelId } = req.params;
    const { page = 1, limit = 50, before } = req.query;

    // Vérifier si le canal existe
    const channel = await Channel.findById(channelId);
    if (!channel) {
      return res.status(404).json({
        success: false,
        message: 'Canal non trouvé.'
      });
    }

    // Vérifier les permissions d'accès
    // Pour les canaux publics, tout le monde peut voir les messages
    // Pour les canaux privés, seulement les participants
    if (channel.type === 'private' && !channel.isParticipant(req.user._id)) {
      return res.status(403).json({
        success: false,
        message: 'Accès refusé. Vous n\'êtes pas membre de ce canal.'
      });
    }

    const query = {
      channel: channelId,
      isDeleted: false
    };

    // Si on demande les messages avant une certaine date
    if (before) {
      query.createdAt = { $lt: new Date(before) };
    }

    const messages = await Message.find(query)
      .populate('author', 'username avatar status')
      .populate('replyTo', 'content author')
      .sort({ createdAt: -1 })
      .limit(parseInt(limit))
      .skip((parseInt(page) - 1) * parseInt(limit));

    const total = await Message.countDocuments(query);

    res.json({
      success: true,
      data: {
        messages: messages.reverse(), // Inverser pour avoir l'ordre chronologique
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total,
          pages: Math.ceil(total / parseInt(limit))
        }
      }
    });

  } catch (error) {
    console.error('Erreur lors de la récupération des messages:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la récupération des messages.'
    });
  }
};

// @desc    Obtenir un message par ID
// @route   GET /api/messages/:id
// @access  Private
const getMessageById = async (req, res) => {
  try {
    const message = await Message.findById(req.params.id)
      .populate('author', 'username avatar')
      .populate('replyTo', 'content author');

    if (!message || message.isDeleted) {
      return res.status(404).json({
        success: false,
        message: 'Message non trouvé.'
      });
    }

    res.json({
      success: true,
      data: {
        message
      }
    });

  } catch (error) {
    console.error('Erreur lors de la récupération du message:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la récupération du message.'
    });
  }
};

// @desc    Modifier un message
// @route   PUT /api/messages/:id
// @access  Private
const updateMessage = async (req, res) => {
  try {
    const { content } = req.body;
    const message = await Message.findById(req.params.id);

    if (!message || message.isDeleted) {
      return res.status(404).json({
        success: false,
        message: 'Message non trouvé.'
      });
    }

    // Vérifier que l'utilisateur est l'auteur
    if (message.author.toString() !== req.user._id.toString()) {
      return res.status(403).json({
        success: false,
        message: 'Vous ne pouvez modifier que vos propres messages.'
      });
    }

    if (!content || !content.trim()) {
      return res.status(400).json({
        success: false,
        message: 'Le contenu du message est requis.'
      });
    }

    message.content = content.trim();
    message.isEdited = true;
    message.editedAt = new Date();
    await message.save();

    await message.populate('author', 'username avatar');

    res.json({
      success: true,
      message: 'Message modifié avec succès.',
      data: {
        message
      }
    });

  } catch (error) {
    console.error('Erreur lors de la modification du message:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la modification du message.'
    });
  }
};

// @desc    Supprimer un message
// @route   DELETE /api/messages/:id
// @access  Private
const deleteMessage = async (req, res) => {
  try {
    const message = await Message.findById(req.params.id);

    if (!message || message.isDeleted) {
      return res.status(404).json({
        success: false,
        message: 'Message non trouvé.'
      });
    }

    // Vérifier que l'utilisateur est l'auteur
    if (message.author.toString() !== req.user._id.toString()) {
      return res.status(403).json({
        success: false,
        message: 'Vous ne pouvez supprimer que vos propres messages.'
      });
    }

    // Soft delete
    message.isDeleted = true;
    message.deletedAt = new Date();
    await message.save();

    res.json({
      success: true,
      message: 'Message supprimé avec succès.'
    });

  } catch (error) {
    console.error('Erreur lors de la suppression du message:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la suppression du message.'
    });
  }
};

// @desc    Ajouter une réaction à un message
// @route   POST /api/messages/:id/reactions
// @access  Private
const addReaction = async (req, res) => {
  try {
    const { emoji } = req.body;
    const message = await Message.findById(req.params.id);

    if (!message || message.isDeleted) {
      return res.status(404).json({
        success: false,
        message: 'Message non trouvé.'
      });
    }

    if (!emoji) {
      return res.status(400).json({
        success: false,
        message: 'L\'emoji est requis.'
      });
    }

    // Utiliser la méthode du modèle pour ajouter la réaction
    message.addReaction(req.user._id, emoji);
    await message.save();

    res.json({
      success: true,
      message: 'Réaction ajoutée avec succès.',
      data: {
        reactions: message.reactions
      }
    });

  } catch (error) {
    console.error('Erreur lors de l\'ajout de la réaction:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de l\'ajout de la réaction.'
    });
  }
};

// @desc    Retirer une réaction d'un message
// @route   DELETE /api/messages/:id/reactions/:emoji
// @access  Private
const removeReaction = async (req, res) => {
  try {
    const { emoji } = req.params;
    const message = await Message.findById(req.params.id);

    if (!message || message.isDeleted) {
      return res.status(404).json({
        success: false,
        message: 'Message non trouvé.'
      });
    }

    // Utiliser la méthode du modèle pour retirer la réaction
    message.removeReaction(req.user._id, emoji);
    await message.save();

    res.json({
      success: true,
      message: 'Réaction retirée avec succès.',
      data: {
        reactions: message.reactions
      }
    });

  } catch (error) {
    console.error('Erreur lors du retrait de la réaction:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors du retrait de la réaction.'
    });
  }
};

// @desc    Rechercher dans les messages d'un canal
// @route   GET /api/messages/search/:channelId
// @access  Private
const searchMessages = async (req, res) => {
  try {
    const { channelId } = req.params;
    const { query, limit = 20 } = req.query;

    if (!query || query.trim().length < 2) {
      return res.status(400).json({
        success: false,
        message: 'Veuillez fournir au moins 2 caractères pour la recherche.'
      });
    }

    const messages = await Message.find({
      channel: channelId,
      isDeleted: false,
      content: { $regex: query.trim(), $options: 'i' }
    })
      .populate('author', 'username avatar')
      .sort({ createdAt: -1 })
      .limit(parseInt(limit));

    res.json({
      success: true,
      data: {
        messages,
        query: query.trim()
      }
    });

  } catch (error) {
    console.error('Erreur lors de la recherche de messages:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la recherche de messages.'
    });
  }
};

module.exports = {
  sendMessage,
  getChannelMessages,
  getMessageById,
  updateMessage,
  deleteMessage,
  addReaction,
  removeReaction,
  searchMessages
};
