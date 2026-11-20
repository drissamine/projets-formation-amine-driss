const jwt = require('jsonwebtoken');
const User = require('../models/User');
const Message = require('../models/Message');
const Channel = require('../models/Channel');

// Map pour stocker les connexions actives
const activeConnections = new Map();
const userSockets = new Map();

class SocketService {
  // Authentifier un socket avec JWT
  authenticateSocket(socket, token) {
    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET || 'votre-secret-jwt-par-defaut');
      return decoded.userId;
    } catch (error) {
      return null;
    }
  }

  // Gérer la connexion d'un utilisateur
  async handleConnection(socket) {
    try {
      const token = socket.handshake.auth.token;
      const userId = this.authenticateSocket(socket, token);

      if (!userId) {
        socket.emit('error', { message: 'Token invalide' });
        socket.disconnect();
        return;
      }

      // Récupérer les informations utilisateur
      const user = await User.findById(userId).select('-password');
      if (!user) {
        socket.emit('error', { message: 'Utilisateur non trouvé' });
        socket.disconnect();
        return;
      }

      // Stocker la connexion
      socket.userId = userId;
      socket.user = user;
      activeConnections.set(socket.id, socket);
      userSockets.set(userId, socket.id);

      // Mettre à jour le statut de l'utilisateur
      user.status = 'online';
      user.lastSeen = new Date();
      await user.save();

      // Rejoindre tous les canaux publics + les canaux privés où l'utilisateur est participant
      const userChannels = await Channel.find({
        isActive: true,
        $or: [
          { type: 'public' }, // Tous les canaux publics
          { 'participants.user': userId } // Plus les canaux privés où l'utilisateur est participant
        ]
      });

      userChannels.forEach(channel => {
        socket.join(channel._id.toString());
      });

      // Notifier les autres utilisateurs de la connexion
      socket.broadcast.emit('user-online', {
        userId: userId,
        username: user.username,
        status: 'online'
      });

      console.log(`Utilisateur ${user.username} connecté (${socket.id})`);

    } catch (error) {
      console.error('Erreur lors de la connexion Socket.io:', error);
      socket.emit('error', { message: 'Erreur de connexion' });
      socket.disconnect();
    }
  }

  // Gérer la déconnexion d'un utilisateur
  async handleDisconnection(socket) {
    try {
      if (socket.userId) {
        const user = await User.findById(socket.userId);
        if (user) {
          user.status = 'offline';
          user.lastSeen = new Date();
          await user.save();

          // Notifier les autres utilisateurs de la déconnexion
          socket.broadcast.emit('user-offline', {
            userId: socket.userId,
            username: user.username
          });
        }

        userSockets.delete(socket.userId);
        console.log(`Utilisateur ${socket.user?.username || socket.userId} déconnecté`);
      }

      activeConnections.delete(socket.id);
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error);
    }
  }

  // Rejoindre un canal
  async joinChannel(socket, channelId) {
    try {
      const channel = await Channel.findById(channelId);
      if (!channel) {
        socket.emit('error', { message: 'Canal non trouvé' });
        return;
      }

      // Pour les canaux privés, vérifier si l'utilisateur est participant
      if (channel.type === 'private' && !channel.isParticipant(socket.userId)) {
        socket.emit('error', { message: 'Accès refusé au canal' });
        return;
      }

      // Pour les canaux publics, ajouter automatiquement l'utilisateur comme participant s'il ne l'est pas déjà
      if (channel.type === 'public' && !channel.isParticipant(socket.userId)) {
        channel.addParticipant(socket.userId, 'member');
        await channel.save();

        // Ajouter le canal à la liste de l'utilisateur
        const user = await User.findById(socket.userId);
        if (user && !user.channels.includes(channelId)) {
          user.channels.push(channelId);
          await user.save();
        }
      }

      socket.join(channelId);

      // Notifier les autres utilisateurs
      socket.to(channelId).emit('user-joined-channel', {
        userId: socket.userId,
        username: socket.user.username,
        channelId: channelId
      });

      console.log(`Utilisateur ${socket.user.username} a rejoint le canal ${channel.name}`);

    } catch (error) {
      console.error('Erreur lors de la rejoint du canal:', error);
      socket.emit('error', { message: 'Erreur lors de la rejoint du canal' });
    }
  }

  // Quitter un canal
  async leaveChannel(socket, channelId) {
    try {
      socket.leave(channelId);

      // Notifier les autres utilisateurs
      socket.to(channelId).emit('user-left-channel', {
        userId: socket.userId,
        username: socket.user?.username || 'Utilisateur inconnu',
        channelId: channelId
      });

      console.log(`Utilisateur ${socket.user?.username || socket.userId} a quitté le canal ${channelId}`);

    } catch (error) {
      console.error('Erreur lors de la quitté du canal:', error);
    }
  }

  // Envoyer un message en temps réel
  async sendMessage(socket, messageData) {
    try {
      const { channelId, content, type = 'text', replyTo } = messageData;

      // Vérifier le canal et les permissions
      const channel = await Channel.findById(channelId);
      if (!channel) {
        socket.emit('error', { message: 'Canal non trouvé' });
        return;
      }

      // Pour les canaux publics, ajouter automatiquement l'utilisateur comme participant s'il ne l'est pas déjà
      if (channel.type === 'public' && !channel.isParticipant(socket.userId)) {
        channel.addParticipant(socket.userId, 'member');
        await channel.save();

        // Ajouter le canal à la liste de l'utilisateur
        const user = await User.findById(socket.userId);
        if (user && !user.channels.includes(channelId)) {
          user.channels.push(channelId);
          await user.save();
        }
      }

      // Pour les canaux privés, vérifier que l'utilisateur est participant
      if (channel.type === 'private' && !channel.isParticipant(socket.userId)) {
        socket.emit('error', { message: 'Vous n\'êtes pas membre de ce canal privé' });
        return;
      }

      // Créer le message
      const message = new Message({
        content: content.trim(),
        channel: channelId,
        author: socket.userId,
        type,
        replyTo
      });

      await message.save();

      // Populer les données pour la réponse
      await message.populate([
        { path: 'author', select: 'username email avatar' },
        { path: 'replyTo', populate: { path: 'author', select: 'username avatar' } }
      ]);

      // Mettre à jour le dernier message du canal
      channel.lastMessage = message._id;
      await channel.save();

      // Envoyer le message à tous les participants du canal
      socket.to(channelId).emit('new-message', {
        channelId,
        message: message.toJSON()
      });

      // Envoyer aussi à l'expéditeur
      socket.emit('message-sent', {
        channelId,
        message: message.toJSON()
      });

      console.log(`Message envoyé par ${socket.user.username} dans ${channel.name}`);

    } catch (error) {
      console.error('Erreur lors de l\'envoi du message:', error);
      socket.emit('error', { message: 'Erreur lors de l\'envoi du message' });
    }
  }

  // Modifier un message en temps réel
  async editMessage(socket, messageId, newContent) {
    try {
      const message = await Message.findById(messageId);
      
      if (!message) {
        socket.emit('error', { message: 'Message non trouvé' });
        return;
      }

      // Vérifier si l'utilisateur est l'auteur
      if (message.author.toString() !== socket.userId) {
        socket.emit('error', { message: 'Vous ne pouvez modifier que vos propres messages' });
        return;
      }

      // Vérifier si le message n'est pas trop ancien
      const hoursSinceCreation = (Date.now() - message.createdAt) / (1000 * 60 * 60);
      if (hoursSinceCreation > 24) {
        socket.emit('error', { message: 'Impossible de modifier un message de plus de 24 heures' });
        return;
      }

      // Modifier le message
      message.edit(newContent.trim());
      await message.save();

      // Populer pour la réponse
      await message.populate('author', 'username email avatar');

      // Notifier tous les participants du canal
      socket.to(message.channel.toString()).emit('message-edited', {
        messageId,
        message: message.toJSON()
      });

      socket.emit('message-edited-self', {
        messageId,
        message: message.toJSON()
      });

    } catch (error) {
      console.error('Erreur lors de la modification du message:', error);
      socket.emit('error', { message: 'Erreur lors de la modification du message' });
    }
  }

  // Supprimer un message en temps réel
  async deleteMessage(socket, messageId) {
    try {
      const message = await Message.findById(messageId).populate('channel');
      
      if (!message) {
        socket.emit('error', { message: 'Message non trouvé' });
        return;
      }

      // Vérifier les permissions (auteur ou admin du canal)
      const isAuthor = message.author.toString() === socket.userId;
      const isAdmin = message.channel.isAdmin(socket.userId);

      if (!isAuthor && !isAdmin) {
        socket.emit('error', { message: 'Accès refusé pour supprimer ce message' });
        return;
      }

      // Marquer comme supprimé
      message.markAsDeleted();
      await message.save();

      // Notifier tous les participants du canal
      socket.to(message.channel._id.toString()).emit('message-deleted', {
        messageId
      });

      socket.emit('message-deleted-self', {
        messageId
      });

    } catch (error) {
      console.error('Erreur lors de la suppression du message:', error);
      socket.emit('error', { message: 'Erreur lors de la suppression du message' });
    }
  }

  // Ajouter une réaction
  async addReaction(socket, messageId, emoji) {
    try {
      const message = await Message.findById(messageId);
      
      if (!message) {
        socket.emit('error', { message: 'Message non trouvé' });
        return;
      }

      // Vérifier l'accès au canal
      const channel = await Channel.findById(message.channel);
      if (!channel.isParticipant(socket.userId)) {
        socket.emit('error', { message: 'Accès refusé' });
        return;
      }

      // Ajouter la réaction
      message.addReaction(socket.userId, emoji);
      await message.save();

      // Populer pour la réponse
      await message.populate('reactions.user', 'username avatar');

      // Notifier tous les participants du canal
      socket.to(message.channel.toString()).emit('reaction-added', {
        messageId,
        message: message.toJSON()
      });

      socket.emit('reaction-added-self', {
        messageId,
        message: message.toJSON()
      });

    } catch (error) {
      console.error('Erreur lors de l\'ajout de réaction:', error);
      socket.emit('error', { message: 'Erreur lors de l\'ajout de réaction' });
    }
  }

  // Retirer une réaction
  async removeReaction(socket, messageId, emoji) {
    try {
      const message = await Message.findById(messageId);
      
      if (!message) {
        socket.emit('error', { message: 'Message non trouvé' });
        return;
      }

      // Retirer la réaction
      message.removeReaction(socket.userId, emoji);
      await message.save();

      // Populer pour la réponse
      await message.populate('reactions.user', 'username avatar');

      // Notifier tous les participants du canal
      socket.to(message.channel.toString()).emit('reaction-removed', {
        messageId,
        message: message.toJSON()
      });

      socket.emit('reaction-removed-self', {
        messageId,
        message: message.toJSON()
      });

    } catch (error) {
      console.error('Erreur lors du retrait de réaction:', error);
      socket.emit('error', { message: 'Erreur lors du retrait de réaction' });
    }
  }

  // Changer le statut utilisateur
  async changeUserStatus(socket, status) {
    try {
      const validStatuses = ['online', 'away', 'offline'];
      if (!validStatuses.includes(status)) {
        socket.emit('error', { message: 'Statut invalide' });
        return;
      }

      const user = await User.findById(socket.userId);
      if (user) {
        user.status = status;
        await user.save();

        // Notifier tous les autres utilisateurs
        socket.broadcast.emit('user-status-changed', {
          userId: socket.userId,
          username: user.username,
          status: status
        });
      }

    } catch (error) {
      console.error('Erreur lors du changement de statut:', error);
    }
  }

  // Obtenir la liste des utilisateurs en ligne
  getOnlineUsers() {
    const onlineUsers = [];
    
    for (const [socketId, socket] of activeConnections) {
      if (socket.user) {
        onlineUsers.push({
          userId: socket.userId,
          username: socket.user.username,
          status: socket.user.status
        });
      }
    }
    
    return onlineUsers;
  }

  // Envoyer une notification à un utilisateur spécifique
  sendNotificationToUser(userId, notification) {
    const socketId = userSockets.get(userId);
    if (socketId) {
      const socket = activeConnections.get(socketId);
      if (socket) {
        socket.emit('notification', notification);
      }
    }
  }

  // Envoyer une notification à tous les utilisateurs d'un canal
  sendNotificationToChannel(channelId, notification) {
    // Cette méthode sera utilisée par les controllers pour les notifications système
  }
}

// Singleton instance
const socketService = new SocketService();

module.exports = socketService;
