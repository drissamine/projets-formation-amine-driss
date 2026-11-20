import React, { createContext, useContext, useReducer, useEffect, useCallback } from 'react';
import AuthService from '../services/authService';
import toast from 'react-hot-toast';

// État initial
const initialState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null
};

// Types d'actions
const AUTH_ACTIONS = {
  LOGIN_START: 'LOGIN_START',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILURE: 'LOGIN_FAILURE',
  LOGOUT: 'LOGOUT',
  REGISTER_START: 'REGISTER_START',
  REGISTER_SUCCESS: 'REGISTER_SUCCESS',
  REGISTER_FAILURE: 'REGISTER_FAILURE',
  UPDATE_USER: 'UPDATE_USER',
  SET_LOADING: 'SET_LOADING',
  CLEAR_ERROR: 'CLEAR_ERROR'
};

// Reducer pour gérer l'état d'authentification
const authReducer = (state, action) => {
  switch (action.type) {
    case AUTH_ACTIONS.LOGIN_START:
    case AUTH_ACTIONS.REGISTER_START:
      return {
        ...state,
        isLoading: true,
        error: null
      };

    case AUTH_ACTIONS.LOGIN_SUCCESS:
    case AUTH_ACTIONS.REGISTER_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        isAuthenticated: true,
        isLoading: false,
        error: null
      };

    case AUTH_ACTIONS.LOGIN_FAILURE:
    case AUTH_ACTIONS.REGISTER_FAILURE:
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload.error
      };

    case AUTH_ACTIONS.LOGOUT:
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null
      };

    case AUTH_ACTIONS.UPDATE_USER:
      return {
        ...state,
        user: { ...state.user, ...action.payload }
      };

    case AUTH_ACTIONS.SET_LOADING:
      return {
        ...state,
        isLoading: action.payload
      };

    case AUTH_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null
      };

    default:
      return state;
  }
};

// Créer le contexte
const AuthContext = createContext();

// Provider d'authentification
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  const initializeAuth = useCallback(async () => {
    try {
      dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: true });

      const result = await AuthService.initializeAuth();

      if (result.success) {
        dispatch({
          type: AUTH_ACTIONS.LOGIN_SUCCESS,
          payload: { user: result.user }
        });
      } else {
        dispatch({ type: AUTH_ACTIONS.LOGOUT });
      }
    } catch (error) {
      console.error('Erreur lors de l\'initialisation de l\'auth:', error);
      dispatch({ type: AUTH_ACTIONS.LOGOUT });
    }
  }, []);

  // Initialiser l'authentification au chargement
  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  // Connexion
  const login = useCallback(async (email, password) => {
    try {
      dispatch({ type: AUTH_ACTIONS.LOGIN_START });
      
      const result = await AuthService.login(email, password);
      
      if (result.success) {
        dispatch({ 
          type: AUTH_ACTIONS.LOGIN_SUCCESS, 
          payload: { user: result.user } 
        });
        toast.success('Connexion réussie !');
        return { success: true };
      } else {
        dispatch({ 
          type: AUTH_ACTIONS.LOGIN_FAILURE, 
          payload: { error: result.message } 
        });
        toast.error(result.message);
        return { success: false, message: result.message };
      }
    } catch (error) {
      const errorMessage = error.message || 'Erreur lors de la connexion';
      dispatch({ 
        type: AUTH_ACTIONS.LOGIN_FAILURE, 
        payload: { error: errorMessage } 
      });
      toast.error(errorMessage);
      return { success: false, message: errorMessage };
    }
  }, []);



  // Inscription
  const register = useCallback(async (userData) => {
    try {
      dispatch({ type: AUTH_ACTIONS.REGISTER_START });
      
      const result = await AuthService.register(userData);
      
      if (result.success) {
        dispatch({ 
          type: AUTH_ACTIONS.REGISTER_SUCCESS, 
          payload: { user: result.user } 
        });
        toast.success('Inscription réussie ! Bienvenue !');
        return { success: true };
      } else {
        dispatch({ 
          type: AUTH_ACTIONS.REGISTER_FAILURE, 
          payload: { error: result.message } 
        });
        toast.error(result.message);
        return { success: false, message: result.message };
      }
    } catch (error) {
      const errorMessage = error.message || 'Erreur lors de l\'inscription';
      dispatch({ 
        type: AUTH_ACTIONS.REGISTER_FAILURE, 
        payload: { error: errorMessage } 
      });
      toast.error(errorMessage);
      return { success: false, message: errorMessage };
    }
  }, []);

  // Déconnexion
  const logout = useCallback(async () => {
    try {
      await AuthService.logout();
      dispatch({ type: AUTH_ACTIONS.LOGOUT });
      toast.success('Déconnexion réussie');
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error);
      dispatch({ type: AUTH_ACTIONS.LOGOUT });
    }
  }, []);

  // Mettre à jour le profil
  const updateProfile = useCallback(async (profileData) => {
    try {
      const result = await AuthService.updateProfile(profileData);
      
      if (result.success) {
        dispatch({ 
          type: AUTH_ACTIONS.UPDATE_USER, 
          payload: result.user 
        });
        toast.success('Profil mis à jour avec succès');
        return { success: true };
      } else {
        toast.error(result.message);
        return { success: false, message: result.message };
      }
    } catch (error) {
      const errorMessage = error.message || 'Erreur lors de la mise à jour';
      toast.error(errorMessage);
      return { success: false, message: errorMessage };
    }
  }, []);

  // Rafraîchir le profil
  const refreshProfile = useCallback(async () => {
    try {
      const result = await AuthService.getProfile();
      
      if (result.success) {
        dispatch({ 
          type: AUTH_ACTIONS.UPDATE_USER, 
          payload: result.user 
        });
        return { success: true };
      } else {
        return { success: false, message: result.message };
      }
    } catch (error) {
      return { success: false, message: error.message };
    }
  }, []);

  // Effacer l'erreur
  const clearError = useCallback(() => {
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
  }, []);

  // Vérifier si l'utilisateur est admin d'un canal
  const isChannelAdmin = useCallback((channel) => {
    if (!state.user || !channel) return false;
    
    const participant = channel.participants?.find(p => 
      p.user._id === state.user._id || p.user === state.user._id
    );
    
    return participant?.role === 'admin';
  }, [state.user]);

  // Valeurs du contexte
  const value = React.useMemo(() => ({
    // État
    user: state.user,
    isAuthenticated: state.isAuthenticated,
    isLoading: state.isLoading,
    error: state.error,
    
    // Actions
    login,
    register,
    logout,
    updateProfile,
    refreshProfile,
    clearError,
    isChannelAdmin,
    initializeAuth
  }), [
    state.user, 
    state.isAuthenticated, 
    state.isLoading, 
    state.error,
    login,
    register,
    logout,
    updateProfile,
    refreshProfile,
    clearError,
    isChannelAdmin,
    initializeAuth
  ]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook pour utiliser le contexte d'authentification
export const useAuth = () => {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth doit être utilisé dans un AuthProvider');
  }
  
  return context;
};

export default AuthContext;
