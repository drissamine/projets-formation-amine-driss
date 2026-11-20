import api from './api';

class MessageService {
  // Envoyer un nouveau message
  async sendMessage(messageData) {
    try {
      const response = await api.post('/messages', messageData);
      
      if (response.success) {
        return { success: true, message: response.data.message };
      }
      
      return { success: false, message: response.message };
    } catch (error) {
      return { 
        success: false, 
        message: error.message || 'Erreur lors de l\'envoi du message' 
      };
    }
  }

  // Obtenir les messages d'un canal
  async getChannelMessages(channelId, options = {}) {
    try {
      const { page = 1, limit = 50, before } = options;
      let url = `/messages/channel/${channelId}?page=${page}&limit=${limit}`;
      
      if (before) {
        url += `&before=${before}`;
      }

      const response = await api.get(url);
      
      if (response.success) {
        return { 
          success: true, 
          messages: response.data.messages,
          pagination: response.data.pagination
        };
      }
      
      return { success: false, message: response.message };
    } catch (error) {
      return { 
        success: false, 
        message: error.message || 'Erreur lors de la récupération des messages' 
      };
    }
  }

  // Obtenir un message par ID
  async getMessageById(messageId) {
    try {
      const response = await api.get(`/messages/${messageId}`);
      
      if (response.success) {
        return { success: true, message: response.data.message };
      }
      
      return { success: false, message: response.message };
    } catch (error) {
      return { 
        success: false, 
        message: error.message || 'Erreur lors de la récupération du message' 
      };
    }
  }

  // Modifier un message
  async updateMessage(messageId, content) {
    try {
      const response = await api.put(`/messages/${messageId}`, { content });
      
      if (response.success) {
        return { success: true, message: response.data.message };
      }
      
      return { success: false, message: response.message };
    } catch (error) {
      return { 
        success: false, 
        message: error.message || 'Erreur lors de la modification du message' 
      };
    }
  }

  // Supprimer un message
  async deleteMessage(messageId) {
    try {
      const response = await api.delete(`/messages/${messageId}`);
      
      if (response.success) {
        return { success: true, message: response.message };
      }
      
      return { success: false, message: response.message };
    } catch (error) {
      return { 
        success: false, 
        message: error.message || 'Erreur lors de la suppression du message' 
      };
    }
  }

  // Ajouter une réaction à un message
  async addReaction(messageId, emoji) {
    try {
      const response = await api.post(`/messages/${messageId}/reactions`, { emoji });
      
      if (response.success) {
        return { success: true, message: response.data.message };
      }
      
      return { success: false, message: response.message };
    } catch (error) {
      return { 
        success: false, 
        message: error.message || 'Erreur lors de l\'ajout de la réaction' 
      };
    }
  }

  // Retirer une réaction d'un message
  async removeReaction(messageId, emoji) {
    try {
      const response = await api.delete(`/messages/${messageId}/reactions/${emoji}`);
      
      if (response.success) {
        return { success: true, message: response.data.message };
      }
      
      return { success: false, message: response.message };
    } catch (error) {
      return { 
        success: false, 
        message: error.message || 'Erreur lors du retrait de la réaction' 
      };
    }
  }

  // Rechercher dans les messages d'un canal
  async searchMessages(channelId, query, limit = 20) {
    try {
      const response = await api.get(`/messages/search/${channelId}?query=${encodeURIComponent(query)}&limit=${limit}`);
      
      if (response.success) {
        return { 
          success: true, 
          messages: response.data.messages,
          query: response.data.query
        };
      }
      
      return { success: false, message: response.message };
    } catch (error) {
      return { 
        success: false, 
        message: error.message || 'Erreur lors de la recherche de messages' 
      };
    }
  }

  // Vérifier si l'utilisateur peut modifier un message
  canEditMessage(message, currentUserId) {
    if (!message || !currentUserId) return false;
    
    // L'utilisateur peut modifier ses propres messages
    const isAuthor = message.author._id === currentUserId || message.author === currentUserId;
    
    // Vérifier si le message n'est pas trop ancien (24 heures)
    const hoursSinceCreation = (Date.now() - new Date(message.createdAt)) / (1000 * 60 * 60);
    const isRecent = hoursSinceCreation <= 24;
    
    return isAuthor && isRecent && !message.isDeleted;
  }

  // Vérifier si l'utilisateur peut supprimer un message
  canDeleteMessage(message, currentUserId, isChannelAdmin = false) {
    if (!message || message.isDeleted) return false;
    
    // L'utilisateur peut supprimer ses propres messages
    const isAuthor = message.author._id === currentUserId || message.author === currentUserId;
    
    // Les admins du canal peuvent supprimer tous les messages
    const isAdmin = isChannelAdmin;
    
    return isAuthor || isAdmin;
  }

  // Obtenir les statistiques d'un message
  getMessageStats(message) {
    if (!message) return null;
    
    return {
      characterCount: message.content?.length || 0,
      wordCount: message.content?.split(/\s+/).length || 0,
      reactionCount: message.reactions?.length || 0,
      isEdited: message.isEdited,
      isDeleted: message.isDeleted,
      createdAt: message.createdAt,
      editedAt: message.editedAt
    };
  }

  // Formater le contenu du message pour l'affichage
  formatMessageContent(content) {
    if (!content) return '';
    
    return content
      .replace(/\n/g, '<br>') // Nouvelles lignes
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Gras
      .replace(/\*(.*?)\*/g, '<em>$1</em>') // Italique
      .replace(/`(.*?)`/g, '<code>$1</code>') // Code inline
      .replace(/@(\w+)/g, '<span class="mention">@$1</span>'); // Mentions
  }

  // Trier les messages par date (plus anciens en premier)
  sortMessagesChronologically(messages) {
    return [...messages].sort((a, b) => 
      new Date(a.createdAt) - new Date(b.createdAt)
    );
  }

  // Grouper les messages par jour
  groupMessagesByDay(messages) {
    const grouped = {};
    
    messages.forEach(message => {
      const date = new Date(message.createdAt).toDateString();
      if (!grouped[date]) {
        grouped[date] = [];
      }
      grouped[date].push(message);
    });
    
    return grouped;
  }

  // Filtrer les messages par type
  filterMessagesByType(messages, type) {
    if (!type || type === 'all') return messages;
    
    return messages.filter(message => message.type === type);
  }

  // Rechercher dans le contenu des messages
  searchInMessageContent(messages, searchTerm) {
    if (!searchTerm) return messages;
    
    const term = searchTerm.toLowerCase();
    
    return messages.filter(message => 
      message.content?.toLowerCase().includes(term) ||
      message.author?.username?.toLowerCase().includes(term)
    );
  }

  // Formater la date relative (il y a X minutes, etc.)
  formatRelativeTime(date) {
    if (!date) return '';
    
    const now = new Date();
    const messageDate = new Date(date);
    const diffInSeconds = Math.floor((now - messageDate) / 1000);
    
    if (diffInSeconds < 60) return 'à l\'instant';
    if (diffInSeconds < 3600) return `il y a ${Math.floor(diffInSeconds / 60)} min`;
    if (diffInSeconds < 86400) return `il y a ${Math.floor(diffInSeconds / 3600)} h`;
    if (diffInSeconds < 604800) return `il y a ${Math.floor(diffInSeconds / 86400)} j`;
    
    return messageDate.toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'short',
      year: messageDate.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    });
  }
}

export default new MessageService();
