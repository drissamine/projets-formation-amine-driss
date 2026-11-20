import api from './api';

class ChannelService {
  /**
   * Récupère tous les canaux de l'utilisateur connecté
   * @returns {Promise<Object>} Résultat avec la liste des canaux ou erreur
   */
  async getUserChannels() {
    try {
      const response = await api.get('/channels');
      
      if (response.success) {
        return { success: true, channels: response.data.channels };
      }
      
      return { success: false, message: response.message };
    } catch (error) {
      return { 
        success: false, 
        message: error.message || 'Erreur lors du chargement des canaux' 
      };
    }
  }

  /**
   * Crée un nouveau canal
   * @param {Object} channelData - Données du canal (name, description, type)
   * @returns {Promise<Object>} Résultat avec le canal créé ou erreur
   */
  async createChannel(channelData) {
    try {
      const response = await api.post('/channels', channelData);
      
      if (response.success) {
        return { success: true, channel: response.data.channel };
      }
      
      return { success: false, message: response.message };
    } catch (error) {
      return { 
        success: false, 
        message: error.message || 'Erreur lors de la création du canal' 
      };
    }
  }

  /**
   * Rejoint un canal existant
   * @param {string} channelId - ID du canal à rejoindre
   * @returns {Promise<Object>} Résultat de l'opération ou erreur
   */
  async joinChannel(channelId) {
    try {
      const response = await api.post(`/channels/${channelId}/join`);
      
      if (response.success) {
        return { success: true, message: response.message };
      }
      
      return { success: false, message: response.message };
    } catch (error) {
      return { 
        success: false, 
        message: error.message || 'Erreur lors de l\'adhésion au canal' 
      };
    }
  }

  /**
   * Quitte un canal
   * @param {string} channelId - ID du canal à quitter
   * @returns {Promise<Object>} Résultat de l'opération ou erreur
   */
  async leaveChannel(channelId) {
    try {
      const response = await api.post(`/channels/${channelId}/leave`);
      
      if (response.success) {
        return { success: true, message: response.message };
      }
      
      return { success: false, message: response.message };
    } catch (error) {
      return { 
        success: false, 
        message: error.message || 'Erreur lors du départ du canal' 
      };
    }
  }

  /**
   * Récupère les détails complets d'un canal
   * @param {string} channelId - ID du canal
   * @returns {Promise<Object>} Résultat avec les détails du canal ou erreur
   */
  async getChannelDetails(channelId) {
    try {
      console.log('ChannelService: Fetching channel details for ID:', channelId);
      const response = await api.get(`/channels/${channelId}`);
      console.log('ChannelService: Raw response:', response);

      if (response.success) {
        return { success: true, channel: response.data.channel };
      }

      return { success: false, message: response.message };
    } catch (error) {
      console.error('ChannelService: Error fetching channel details:', error);
      return {
        success: false,
        message: error.message || 'Erreur lors de la récupération du canal'
      };
    }
  }

  /**
   * Supprime un canal
   * @param {string} channelId - ID du canal à supprimer
   * @returns {Promise<Object>} Résultat de l'opération ou erreur
   */
  async deleteChannel(channelId) {
    try {
      const response = await api.delete(`/channels/${channelId}`);

      if (response.success) {
        return { success: true, message: response.message };
      }

      return { success: false, message: response.message };
    } catch (error) {
      return {
        success: false,
        message: error.message || 'Erreur lors de la suppression du canal'
      };
    }
  }

  /**
   * Trie les canaux par activité (dernier message)
   * @param {Array} channels - Liste des canaux à trier
   * @returns {Array} Liste des canaux triés par activité décroissante
   */
  sortChannelsByActivity(channels) {
    if (!channels) return [];
    
    return [...channels].sort((a, b) => {
      // Utiliser la date du dernier message, sinon la date de création
      const dateA = a.lastMessage?.createdAt ? new Date(a.lastMessage.createdAt) : new Date(a.createdAt);
      const dateB = b.lastMessage?.createdAt ? new Date(b.lastMessage.createdAt) : new Date(b.createdAt);
      
      // Tri décroissant (plus récent en premier)
      return dateB - dateA;
    });
  }

  /**
   * Filtre les canaux par type
   * @param {Array} channels - Liste des canaux à filtrer
   * @param {string} type - Type de canal ('public', 'private', 'direct', 'all')
   * @returns {Array} Liste des canaux filtrés
   */
  filterChannelsByType(channels, type) {
    if (!type || type === 'all') return channels;
    return channels.filter(channel => channel.type === type);
  }

  /**
   * Crée ou retrouve un canal direct avec un utilisateur
   * @param {string} targetUserId - ID de l'utilisateur cible
   * @returns {Promise<Object>} Résultat avec le canal direct ou erreur
   */
  async createOrGetDirectChannel(targetUserId) {
    try {
      const response = await api.post(`/channels/direct/${targetUserId}`);

      if (response.success) {
        return {
          success: true,
          channel: response.data.channel,
          isNew: response.data.isNew
        };
      }

      return { success: false, message: response.message };
    } catch (error) {
      return {
        success: false,
        message: error.message || 'Erreur lors de la création du canal direct'
      };
    }
  }

  /**
   * Récupère tous les utilisateurs (pour les messages directs)
   * @returns {Promise<Object>} Résultat avec la liste des utilisateurs ou erreur
   */
  async getUsers() {
    try {
      const response = await api.get('/channels/users');

      if (response.success) {
        return { success: true, users: response.data.users };
      }

      return { success: false, message: response.message };
    } catch (error) {
      return {
        success: false,
        message: error.message || 'Erreur lors du chargement des utilisateurs'
      };
    }
  }

  /**
   * Recherche dans les canaux par nom ou description
   * @param {Array} channels - Liste des canaux à rechercher
   * @param {string} query - Terme de recherche
   * @returns {Array} Liste des canaux correspondant à la recherche
   */
  searchChannels(channels, query) {
    if (!query) return channels;

    const term = query.toLowerCase();
    return channels.filter(channel =>
      channel.name.toLowerCase().includes(term) ||
      channel.description?.toLowerCase().includes(term)
    );
  }
}

const channelService = new ChannelService();
export default channelService;
