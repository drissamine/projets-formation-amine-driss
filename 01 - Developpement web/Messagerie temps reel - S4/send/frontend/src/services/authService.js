import api, { setAuthToken, setRefreshToken, getStoredToken, clearAuthTokens } from './api';

class AuthService {
  /**
   * Inscrit un nouvel utilisateur
   * @param {Object} userData - Données de l'utilisateur (username, email, password)
   * @returns {Promise<Object>} Résultat de l'inscription avec succès/user/token ou erreur
   */
  async register(userData) {
    try {
      const response = await api.post('/auth/register', userData);
      
      if (response.success) {
        const { user, token, refreshToken } = response.data;
        
        // Stocker les informations d'authentification
        localStorage.setItem('user', JSON.stringify(user));
        setAuthToken(token);
        setRefreshToken(refreshToken);
        
        return { success: true, user, token, refreshToken };
      }
      
      return { success: false, message: response.message };
    } catch (error) {
      return { 
        success: false, 
        message: error.message || 'Erreur lors de l\'inscription' 
      };
    }
  }

  /**
   * Connecte un utilisateur existant
   * @param {string} email - Email de l'utilisateur
   * @param {string} password - Mot de passe de l'utilisateur
   * @returns {Promise<Object>} Résultat de la connexion avec succès/user/token ou erreur
   */
  async login(email, password) {
    try {
      const response = await api.post('/auth/login', { email, password });
      
      if (response.success) {
        console.log('Login response:', response); // Debug login response
        const { user, token, refreshToken } = response.data;
        
        if (!token) {
            console.error('Token manquant dans la réponse de connexion', response);
            return { success: false, message: 'Erreur protocole: Token manquant' };
        }

        // Stocker les informations d'authentification
        localStorage.setItem('user', JSON.stringify(user));
        setAuthToken(token);
        setRefreshToken(refreshToken);
        
        return { success: true, user, token, refreshToken };
      }
      
      return { success: false, message: response.message };
    } catch (error) {
      return { 
        success: false, 
        message: error.message || 'Erreur lors de la connexion' 
      };
    }
  }

  /**
   * Déconnecte l'utilisateur actuel
   * @returns {Promise<void>}
   */
  async logout() {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error);
    } finally {
      // Toujours nettoyer les tokens localement
      this.clearAuthData();
    }
  }

  /**
   * Récupère le profil de l'utilisateur connecté
   * @returns {Promise<Object>} Résultat avec le profil utilisateur ou erreur
   */
  async getProfile() {
    try {
      const response = await api.get('/auth/profile');
      
      if (response.success) {
        const user = response.data.user;
        localStorage.setItem('user', JSON.stringify(user));
        return { success: true, user };
      }
      
      return { success: false, message: response.message };
    } catch (error) {
      return { 
        success: false, 
        message: error.message || 'Erreur lors de la récupération du profil' 
      };
    }
  }

  /**
   * Met à jour le profil de l'utilisateur connecté
   * @param {Object} profileData - Données à mettre à jour (avatar, etc.)
   * @returns {Promise<Object>} Résultat avec le profil mis à jour ou erreur
   */
  async updateProfile(profileData) {
    try {
      const response = await api.put('/auth/profile', profileData);
      
      if (response.success) {
        const user = response.data.user;
        localStorage.setItem('user', JSON.stringify(user));
        return { success: true, user };
      }
      
      return { success: false, message: response.message };
    } catch (error) {
      return { 
        success: false, 
        message: error.message || 'Erreur lors de la mise à jour du profil' 
      };
    }
  }

  /**
   * Renouvelle le token d'accès en utilisant le refresh token
   * @returns {Promise<Object>} Résultat avec les nouveaux tokens ou erreur
   */
  async refreshToken() {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (!refreshToken) {
        throw new Error('Aucun refresh token disponible');
      }

      const response = await api.post('/auth/refresh', { refreshToken });
      
      if (response.success) {
        const { token, refreshToken: newRefreshToken } = response.data;
        setAuthToken(token);
        setRefreshToken(newRefreshToken);
        
        return { success: true, token, refreshToken: newRefreshToken };
      }
      
      return { success: false, message: response.message };
    } catch (error) {
      // Si le refresh échoue, déconnecter l'utilisateur
      this.clearAuthData();
      return { 
        success: false, 
        message: error.message || 'Impossible de renew le token' 
      };
    }
  }

  /**
   * Vérifie si l'utilisateur est actuellement authentifié
   * @returns {boolean} True si l'utilisateur est authentifié, false sinon
   */
  isAuthenticated() {
    const token = getStoredToken();
    const user = localStorage.getItem('user');
    
    return !!(token && user);
  }

  /**
   * Récupère les données utilisateur stockées localement
   * @returns {Object|null} Objet utilisateur ou null si non trouvé
   */
  getStoredUser() {
    try {
      const user = localStorage.getItem('user');
      return user ? JSON.parse(user) : null;
    } catch (error) {
      console.error('Erreur lors de la récupération de l\'utilisateur:', error);
      return null;
    }
  }

  /**
   * Vérifie si un token JWT est expiré
   * @param {string} token - Le token JWT à vérifier
   * @returns {boolean} True si le token est expiré, false sinon
   */
  isTokenExpired(token) {
    try {
      // Décoder le payload du JWT (partie entre les deux points)
      const payload = JSON.parse(atob(token.split('.')[1]));
      // Convertir l'expiration (en secondes) en millisecondes
      const expiry = payload.exp * 1000;
      // Vérifier si le token est expiré
      return Date.now() > expiry;
    } catch (error) {
      // En cas d'erreur de décodage, considérer le token comme expiré
      return true;
    }
  }

  /**
   * Supprime toutes les données d'authentification du stockage local
   */
  clearAuthData() {
    clearAuthTokens(); // Supprimer les tokens via l'API
    localStorage.removeItem('user'); // Supprimer les données utilisateur
  }

  /**
   * Initialise l'authentification au démarrage de l'application
   * Vérifie la validité du token et récupère le profil utilisateur
   * @returns {Promise<Object>} Résultat avec succès/user ou erreur
   */
  async initializeAuth() {
    // Récupérer le token stocké
    const token = getStoredToken();

    if (!token) {
      return { success: false, message: 'Aucun token trouvé' };
    }

    // Vérifier si le token actuel est expiré
    if (this.isTokenExpired(token)) {
      // Tenter de renouveler le token avec le refresh token
      const refreshResult = await this.refreshToken();
      if (!refreshResult.success) {
        this.clearAuthData(); // Nettoyer si le renouvellement échoue
        return { success: false, message: 'Token expiré' };
      }
    }

    // Récupérer les informations du profil utilisateur
    const profileResult = await this.getProfile();

    if (profileResult.success) {
      return { success: true, user: profileResult.user };
    } else {
      this.clearAuthData(); // Nettoyer si la récupération échoue
      return { success: false, message: 'Impossible de récupérer le profil' };
    }
  }
}

const authServiceInstance = new AuthService();
export default authServiceInstance;
