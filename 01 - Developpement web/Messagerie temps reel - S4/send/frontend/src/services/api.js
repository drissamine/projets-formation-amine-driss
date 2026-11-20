import axios from 'axios';

// Configuration de base d'axios
const getApiBaseUrl = () => {
  // En production, utiliser l'URL configurée
  if (process.env.NODE_ENV === 'production') {
    return process.env.REACT_APP_API_URL || 'https://your-backend-url.railway.app/api';
  }
  // En développement, utiliser localhost
  return process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
};

const api = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token JWT aux requêtes
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Intercepteur pour gérer les réponses et les erreurs
api.interceptors.response.use(
  (response) => {
    return response.data; // Retourner directement les données
  },
  (error) => {
    // Gérer les erreurs globales
    if (error.response?.status === 401) {
      // Ne pas déconnecter si l'erreur vient de la tentative de connexion elle-même
      const isLoginRequest = error.config.url.endsWith('/auth/login');
      
      if (!isLoginRequest) {
        // Token expiré ou invalide pour les autres requêtes
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }
    
    if (error.response?.status === 403) {
      console.error('Accès refusé:', error.response.data.message);
    }
    
    if (error.response?.status === 500) {
      console.error('Erreur serveur:', error.response.data.message);
    }
    
    // Retourner l'erreur avec plus de détails
    return Promise.reject({
      message: error.response?.data?.message || 'Erreur de connexion',
      status: error.response?.status,
      data: error.response?.data
    });
  }
);

// Méthodes utilitaires
export const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    localStorage.setItem('token', token);
  } else {
    delete api.defaults.headers.common['Authorization'];
    localStorage.removeItem('token');
  }
};

export const setRefreshToken = (refreshToken) => {
  if (refreshToken) {
    localStorage.setItem('refreshToken', refreshToken);
  } else {
    localStorage.removeItem('refreshToken');
  }
};

export const getStoredToken = () => {
  return localStorage.getItem('token');
};

export const getStoredRefreshToken = () => {
  return localStorage.getItem('refreshToken');
};

export const clearAuthTokens = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('user');
  delete api.defaults.headers.common['Authorization'];
};

export default api;
