const Channel = require('../models/Channel');
const User = require('../models/User');

// @desc    Obtenir tous les utilisateurs (pour les messages directs)
// @route   GET /api/channels/users
// @access  Private
const getUsers = async (req, res) => {
  try {
    const users = await User.find({ _id: { $ne: req.user._id } })
      .select('username avatar status lastSeen')
      .sort({ username: 1 });

    res.json({
      success: true,
      data: {
        users
      }
    });

  } catch (error) {
    console.error('Erreur lors de la récupération des utilisateurs:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la récupération des utilisateurs.'
    });
  }
};

// @desc    Créer un nouveau canal
// @route   POST /api/channels
// @access  Private
const createChannel = async (req, res) => {
  try {
    const { name, description, type = 'public' } = req.body;

    // Validation des données
    if (!name) {
      return res.status(400).json({
        success: false,
        message: 'Le nom du canal est requis.'
      });
    }

    // Vérifier si le nom de canal existe déjà
    const existingChannel = await Channel.findOne({ 
      name: name.trim(),
      creator: req.user._id 
    });

    if (existingChannel) {
      return res.status(400).json({
        success: false,
        message: 'Un canal avec ce nom existe déjà.'
      });
    }

    // Créer le nouveau canal
    const channel = new Channel({
      name: name.trim(),
      description: description?.trim() || '',
      type,
      creator: req.user._id,
      participants: [{
        user: req.user._id,
        role: 'admin'
      }]
    });

    await channel.save();

    // Populer les données pour la réponse
    await channel.populate([
      { path: 'creator', select: 'username avatar' },
      { path: 'participants.user', select: 'username avatar status' }
    ]);

    // Ajouter le canal à la liste de l'utilisateur
    req.user.channels.push(channel._id);
    await req.user.save();

    res.status(201).json({
      success: true,
      message: 'Canal créé avec succès.',
      data: {
        channel
      }
    });

  } catch (error) {
    console.error('Erreur lors de la création du canal:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la création du canal.'
    });
  }
};

// @desc    Obtenir tous les canaux de l'utilisateur
// @route   GET /api/channels
// @access  Private
const getUserChannels = async (req, res) => {
  try {
    const channels = await Channel.find({
      isActive: true,
      $or: [
        { type: 'public' }, // Tous les canaux publics sont visibles
        { 'participants.user': req.user._id } // Plus les canaux privés où l'utilisateur est participant
      ]
    })
      .populate('creator', 'username avatar')
      .populate('participants.user', 'username avatar status')
      .populate('lastMessage')
      .sort({ updatedAt: -1 });

    res.json({
      success: true,
      data: {
        channels
      }
    });

  } catch (error) {
    console.error('Erreur lors de la récupération des canaux:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la récupération des canaux.'
    });
  }
};

// @desc    Obtenir un canal par ID
// @route   GET /api/channels/:id
// @access  Private
const getChannelById = async (req, res) => {
  try {
    const channel = await Channel.findById(req.params.id)
      .populate('creator', 'username avatar')
      .populate('participants.user', 'username avatar status')
      .populate('lastMessage');

    if (!channel) {
      return res.status(404).json({
        success: false,
        message: 'Canal non trouvé.'
      });
    }

    // Temporairement désactivé pour debug
    // // Vérifier si l'utilisateur est participant
    // if (!channel.isParticipant(req.user._id)) {
    //   return res.status(403).json({
    //     success: false,
    //     message: 'Accès refusé. Vous n\'êtes pas participant de ce canal.'
    //   });
    // }

    console.log('Channel found:', channel._id);
    console.log('User ID:', req.user._id);
    console.log('Is participant:', channel.isParticipant(req.user._id));

    res.json({
      success: true,
      data: {
        channel
      }
    });

  } catch (error) {
    console.error('Erreur lors de la récupération du canal:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la récupération du canal.'
    });
  }
};

// @desc    Rejoindre un canal
// @route   POST /api/channels/:id/join
// @access  Private
const joinChannel = async (req, res) => {
  try {
    const channel = await Channel.findById(req.params.id);

    if (!channel) {
      return res.status(404).json({
        success: false,
        message: 'Canal non trouvé.'
      });
    }

    // Vérifier si l'utilisateur est déjà participant
    if (channel.isParticipant(req.user._id)) {
      return res.status(400).json({
        success: false,
        message: 'Vous êtes déjà participant de ce canal.'
      });
    }

    // Vérifier si le canal est privé (nécessite invitation)
    if (channel.type === 'private') {
      return res.status(403).json({
        success: false,
        message: 'Ce canal est privé. Une invitation est requise.'
      });
    }

    // Ajouter l'utilisateur au canal
    channel.addParticipant(req.user._id, 'member');
    await channel.save();

    // Ajouter le canal à la liste de l'utilisateur
    req.user.channels.push(channel._id);
    await req.user.save();

    // Populer les données pour la réponse
    await channel.populate('participants.user', 'username avatar status');

    res.json({
      success: true,
      message: 'Vous avez rejoint le canal avec succès.',
      data: {
        channel
      }
    });

  } catch (error) {
    console.error('Erreur lors de la rejoindre du canal:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la rejoint du canal.'
    });
  }
};

// @desc    Quitter un canal
// @route   POST /api/channels/:id/leave
// @access  Private
const leaveChannel = async (req, res) => {
  try {
    const channel = await Channel.findById(req.params.id);

    if (!channel) {
      return res.status(404).json({
        success: false,
        message: 'Canal non trouvé.'
      });
    }

    // Vérifier si l'utilisateur est participant
    if (!channel.isParticipant(req.user._id)) {
      return res.status(400).json({
        success: false,
        message: 'Vous n\'êtes pas participant de ce canal.'
      });
    }

    // Vérifier si l'utilisateur est le créateur
    if (channel.creator.toString() === req.user._id.toString()) {
      return res.status(400).json({
        success: false,
        message: 'Le créateur ne peut pas quitter le canal. Transférez d\'abord la propriété.'
      });
    }

    // Retirer l'utilisateur du canal
    channel.removeParticipant(req.user._id);
    await channel.save();

    // Retirer le canal de la liste de l'utilisateur
    req.user.channels = req.user.channels.filter(
      id => id.toString() !== channel._id.toString()
    );
    await req.user.save();

    res.json({
      success: true,
      message: 'Vous avez quitté le canal avec succès.'
    });

  } catch (error) {
    console.error('Erreur lors de la quitté du canal:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la quitté du canal.'
    });
  }
};

// @desc    Mettre à jour un canal
// @route   PUT /api/channels/:id
// @access  Private
const updateChannel = async (req, res) => {
  try {
    const { name, description, type } = req.body;
    const channel = await Channel.findById(req.params.id);

    if (!channel) {
      return res.status(404).json({
        success: false,
        message: 'Canal non trouvé.'
      });
    }

    // Vérifier les permissions (seulement le créateur ou un admin)
    if (!channel.isAdmin(req.user._id)) {
      return res.status(403).json({
        success: false,
        message: 'Accès refusé. Privilèges administrateur requis.'
      });
    }

    // Vérifier si le nouveau nom existe déjà
    if (name && name !== channel.name) {
      const existingChannel = await Channel.findOne({ 
        name: name.trim(),
        _id: { $ne: channel._id }
      });

      if (existingChannel) {
        return res.status(400).json({
          success: false,
          message: 'Un canal avec ce nom existe déjà.'
        });
      }

      channel.name = name.trim();
    }

    // Mettre à jour les autres champs
    if (description !== undefined) channel.description = description.trim();
    if (type) channel.type = type;

    await channel.save();

    // Populer les données pour la réponse
    await channel.populate([
      { path: 'creator', select: 'username avatar' },
      { path: 'participants.user', select: 'username avatar status' }
    ]);

    res.json({
      success: true,
      message: 'Canal mis à jour avec succès.',
      data: {
        channel
      }
    });

  } catch (error) {
    console.error('Erreur lors de la mise à jour du canal:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la mise à jour du canal.'
    });
  }
};

// @desc    Supprimer un canal
// @route   DELETE /api/channels/:id
// @access  Private
const deleteChannel = async (req, res) => {
  try {
    const channel = await Channel.findById(req.params.id);

    if (!channel) {
      return res.status(404).json({
        success: false,
        message: 'Canal non trouvé.'
      });
    }

    // Vérifier les permissions (seulement le créateur)
    if (channel.creator.toString() !== req.user._id.toString()) {
      return res.status(403).json({
        success: false,
        message: 'Accès refusé. Seul le créateur peut supprimer le canal.'
      });
    }

    // Marquer le canal comme inactif au lieu de le supprimer complètement
    channel.isActive = false;
    await channel.save();

    // Retirer le canal de tous les utilisateurs participants
    const participantIds = channel.participants.map(p => p.user);
    await User.updateMany(
      { _id: { $in: participantIds } },
      { $pull: { channels: channel._id } }
    );

    res.json({
      success: true,
      message: 'Canal supprimé avec succès.'
    });

  } catch (error) {
    console.error('Erreur lors de la suppression du canal:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la suppression du canal.'
    });
  }
};

// @desc    Rechercher des canaux
// @route   GET /api/channels/search
// @access  Private
const searchChannels = async (req, res) => {
  try {
    const { query } = req.query;

    if (!query || query.trim().length < 2) {
      return res.status(400).json({
        success: false,
        message: 'Veuillez fournir au moins 2 caractères pour la recherche.'
      });
    }

    const channels = await Channel.find({
      $text: { $search: query.trim() },
      isActive: true,
      type: 'public'
    })
      .populate('creator', 'username avatar')
      .populate('participants.user', 'username avatar status')
      .limit(20);

    res.json({
      success: true,
      data: {
        channels,
        query: query.trim()
      }
    });

  } catch (error) {
    console.error('Erreur lors de la recherche de canaux:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la recherche de canaux.'
    });
  }
};

// @desc    Créer ou retrouver un canal direct avec un utilisateur
// @route   POST /api/channels/direct/:userId
// @access  Private
const createOrGetDirectChannel = async (req, res) => {
  try {
    const targetUserId = req.params.userId;

    // Vérifier que l'utilisateur cible existe
    const targetUser = await User.findById(targetUserId);
    if (!targetUser) {
      return res.status(404).json({
        success: false,
        message: 'Utilisateur non trouvé.'
      });
    }

    // Empêcher de créer un canal direct avec soi-même
    if (targetUserId === req.user._id.toString()) {
      return res.status(400).json({
        success: false,
        message: 'Vous ne pouvez pas créer un canal direct avec vous-même.'
      });
    }

    // Chercher s'il existe déjà un canal direct entre ces deux utilisateurs
    const existingDirectChannel = await Channel.findOne({
      type: 'direct',
      isActive: true,
      participants: {
        $all: [
          { $elemMatch: { user: req.user._id } },
          { $elemMatch: { user: targetUserId } }
        ],
        $size: 2 // Exactement 2 participants
      }
    });

    if (existingDirectChannel) {
      // Retourner le canal existant
      await existingDirectChannel.populate([
        { path: 'creator', select: 'username avatar' },
        { path: 'participants.user', select: 'username avatar status' },
        { path: 'lastMessage' }
      ]);

      return res.json({
        success: true,
        message: 'Canal direct existant trouvé.',
        data: {
          channel: existingDirectChannel,
          isNew: false
        }
      });
    }

    // Créer un nouveau canal direct
    const directChannel = new Channel({
      name: `Direct - ${req.user.username} & ${targetUser.username}`,
      description: 'Conversation directe',
      type: 'direct',
      creator: req.user._id,
      participants: [
        {
          user: req.user._id,
          role: 'admin'
        },
        {
          user: targetUserId,
          role: 'admin'
        }
      ]
    });

    await directChannel.save();

    // Populer les données pour la réponse
    await directChannel.populate([
      { path: 'creator', select: 'username avatar' },
      { path: 'participants.user', select: 'username avatar status' }
    ]);

    // Ajouter le canal aux listes des deux utilisateurs
    req.user.channels.push(directChannel._id);
    await req.user.save();

    targetUser.channels.push(directChannel._id);
    await targetUser.save();

    res.status(201).json({
      success: true,
      message: 'Canal direct créé avec succès.',
      data: {
        channel: directChannel,
        isNew: true
      }
    });

  } catch (error) {
    console.error('Erreur lors de la création du canal direct:', error);
    res.status(500).json({
      success: false,
      message: 'Erreur lors de la création du canal direct.'
    });
  }
};

module.exports = {
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
};
