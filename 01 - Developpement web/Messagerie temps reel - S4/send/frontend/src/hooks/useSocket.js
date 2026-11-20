import { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import io from 'socket.io-client';

// Fonction pour obtenir l'URL du serveur Socket.io
const getSocketUrl = () => {
  // En production, utiliser l'URL configurée
  if (process.env.NODE_ENV === 'production') {
    return process.env.REACT_APP_SOCKET_URL || 'https://your-backend-url.railway.app';
  }
  // En développement, utiliser localhost
  return process.env.REACT_APP_SOCKET_URL || 'http://localhost:5000';
};

const SOCKET_URL = getSocketUrl();

export const useSocket = () => {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [error, setError] = useState(null);
  
  const { user, isAuthenticated } = useAuth();
  const token = localStorage.getItem('token');
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  // Initialiser la connexion Socket.io
  useEffect(() => {
    if (!isAuthenticated || !user || !token) {
      return;
    }

    const socketInstance = io(SOCKET_URL, {
      auth: {
        token: token
      },
      transports: ['websocket', 'polling']
    });

    // Gestion de la connexion
    socketInstance.on('connect', () => {
      console.log('Connecté au serveur Socket.io');
      setIsConnected(true);
      setError(null);
      reconnectAttempts.current = 0;
      
      // Demander la liste des utilisateurs en ligne
      socketInstance.emit('get-online-users');
    });

    // Gestion de la déconnexion
    socketInstance.on('disconnect', (reason) => {
      console.log('Déconnecté du serveur Socket.io:', reason);
      setIsConnected(false);
      
      if (reason === 'io server disconnect') {
        // Le serveur a déconnecté, tenter de reconnexion automatique
        socketInstance.connect();
      }
    });

    // Gestion des erreurs de connexion
    socketInstance.on('connect_error', (error) => {
      console.error('Erreur de connexion Socket.io:', error);
      setError('Erreur de connexion au serveur temps réel');
      setIsConnected(false);
    });

    // Événements utilisateur
    socketInstance.on('user-online', (userData) => {
      setOnlineUsers(prev => {
        const exists = prev.find(u => u.userId === userData.userId);
        if (!exists) {
          return [...prev, { ...userData, status: 'online' }];
        }
        return prev.map(u => 
          u.userId === userData.userId 
            ? { ...u, status: 'online' }
            : u
        );
      });
    });

    socketInstance.on('user-offline', (userData) => {
      setOnlineUsers(prev => 
        prev.filter(u => u.userId !== userData.userId)
      );
    });

    socketInstance.on('user-status-changed', (userData) => {
      setOnlineUsers(prev =>
        prev.map(u =>
          u.userId === userData.userId
            ? { ...u, status: userData.status }
            : u
        )
      );
    });

    // Réponse à la demande de liste des utilisateurs en ligne
    socketInstance.on('online-users', (users) => {
      setOnlineUsers(users);
    });

    // Événements de canal
    socketInstance.on('user-joined-channel', (data) => {
      console.log(`Utilisateur ${data.username} a rejoint le canal`);
      // Ici vous pouvez déclencher une notification
    });

    socketInstance.on('user-left-channel', (data) => {
      console.log(`Utilisateur ${data.username} a quitté le canal`);
    });

    // Événements de messages
    socketInstance.on('new-message', (data) => {
      // Le message sera traité par le composant Chat
      window.dispatchEvent(new CustomEvent('new-message', { detail: data }));
    });

    socketInstance.on('message-sent', (data) => {
      window.dispatchEvent(new CustomEvent('message-sent', { detail: data }));
    });

    socketInstance.on('message-edited', (data) => {
      window.dispatchEvent(new CustomEvent('message-edited', { detail: data }));
    });

    socketInstance.on('message-edited-self', (data) => {
      window.dispatchEvent(new CustomEvent('message-edited-self', { detail: data }));
    });

    socketInstance.on('message-deleted', (data) => {
      window.dispatchEvent(new CustomEvent('message-deleted', { detail: data }));
    });

    socketInstance.on('message-deleted-self', (data) => {
      window.dispatchEvent(new CustomEvent('message-deleted-self', { detail: data }));
    });

    // Événements de réactions
    socketInstance.on('reaction-added', (data) => {
      window.dispatchEvent(new CustomEvent('reaction-added', { detail: data }));
    });

    socketInstance.on('reaction-added-self', (data) => {
      window.dispatchEvent(new CustomEvent('reaction-added-self', { detail: data }));
    });

    socketInstance.on('reaction-removed', (data) => {
      window.dispatchEvent(new CustomEvent('reaction-removed', { detail: data }));
    });

    socketInstance.on('reaction-removed-self', (data) => {
      window.dispatchEvent(new CustomEvent('reaction-removed-self', { detail: data }));
    });

    // Événements d'erreur
    socketInstance.on('error', (error) => {
      console.error('Erreur Socket.io:', error);
      setError(error.message || 'Erreur de communication');
    });

    socketInstance.on('socket-error', (error) => {
      console.error('Erreur Socket.io:', error);
      setError(error.message);
    });

    setSocket(socketInstance);

    // Cleanup lors du démontage
    return () => {
      socketInstance.disconnect();
      setSocket(null);
      setIsConnected(false);
    };
  }, [isAuthenticated, user, token]);

  // Fonctions pour interagir avec Socket.io (stabilisées avec useCallback)
  const joinChannel = useCallback((channelId) => {
    if (socket && isConnected) {
      socket.emit('join-channel', channelId);
    }
  }, [socket, isConnected]);

  const leaveChannel = useCallback((channelId) => {
    if (socket && isConnected) {
      socket.emit('leave-channel', channelId);
    }
  }, [socket, isConnected]);

  const sendMessage = useCallback((messageData) => {
    if (socket && isConnected) {
      socket.emit('send-message', messageData);
    }
  }, [socket, isConnected]);

  const editMessage = useCallback((messageId, newContent) => {
    if (socket && isConnected) {
      socket.emit('edit-message', { messageId, newContent });
    }
  }, [socket, isConnected]);

  const deleteMessage = useCallback((messageId) => {
    if (socket && isConnected) {
      socket.emit('delete-message', messageId);
    }
  }, [socket, isConnected]);

  const addReaction = useCallback((messageId, emoji) => {
    if (socket && isConnected) {
      socket.emit('add-reaction', { messageId, emoji });
    }
  }, [socket, isConnected]);

  const removeReaction = useCallback((messageId, emoji) => {
    if (socket && isConnected) {
      socket.emit('remove-reaction', { messageId, emoji });
    }
  }, [socket, isConnected]);

  const changeUserStatus = useCallback((status) => {
    if (socket && isConnected) {
      socket.emit('change-status', status);
    }
  }, [socket, isConnected]);

  const getOnlineUsers = useCallback(() => {
    if (socket && isConnected) {
      socket.emit('get-online-users');
    }
  }, [socket, isConnected]);

  // Reconnexion manuelle
  const reconnect = useCallback(() => {
    if (socket && reconnectAttempts.current < maxReconnectAttempts) {
      reconnectAttempts.current++;
      console.log(`Tentative de reconnexion ${reconnectAttempts.current}/${maxReconnectAttempts}`);
      socket.connect();
    } else {
      setError('Nombre maximum de tentatives de reconnexion atteint');
    }
  }, [socket]);

  return {
    socket,
    isConnected,
    onlineUsers,
    error,
    
    // Actions
    joinChannel,
    leaveChannel,
    sendMessage,
    editMessage,
    deleteMessage,
    addReaction,
    removeReaction,
    changeUserStatus,
    getOnlineUsers,
    reconnect,
    
    // Utilitaires
    clearError: () => setError(null)
  };
};
