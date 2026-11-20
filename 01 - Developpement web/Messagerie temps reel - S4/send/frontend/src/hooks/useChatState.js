import { useState, useEffect, useCallback } from 'react';
import toast from 'react-hot-toast';
import ChannelService from '../services/channelService';
import MessageService from '../services/messageService';
import { useSocket } from './useSocket';

export const useChatState = (user) => {
  const [channels, setChannels] = useState([]);
  const [selectedChannel, setSelectedChannel] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sendingMessage, setSendingMessage] = useState(false);
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [channelsLoaded, setChannelsLoaded] = useState(false);
  const [unreadCounts, setUnreadCounts] = useState(() => {
    // Charger les compteurs depuis localStorage au démarrage
    try {
      const saved = localStorage.getItem('chatUnreadCounts');
      return saved ? JSON.parse(saved) : {};
    } catch {
      return {};
    }
  });

  // Socket interface
  const {
    socket,
    isConnected,
    onlineUsers: socketOnlineUsers,
    joinChannel,
    leaveChannel,
    sendMessage: sendSocketMessage,
  } = useSocket();

  // Sauvegarder les compteurs de messages non lus dans localStorage
  const saveUnreadCounts = useCallback((counts) => {
    try {
      localStorage.setItem('chatUnreadCounts', JSON.stringify(counts));
    } catch (error) {
      console.error('Erreur sauvegarde compteurs:', error);
    }
  }, []);

  // Marquer un canal comme lu
  const markChannelAsRead = useCallback((channelId) => {
    setUnreadCounts(prev => {
      const newCounts = { ...prev };
      delete newCounts[channelId];
      saveUnreadCounts(newCounts);
      return newCounts;
    });
  }, [saveUnreadCounts]);

  // Demander la permission pour les notifications du navigateur
  const requestNotificationPermission = useCallback(async () => {
    if ('Notification' in window) {
      try {
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
          toast.success('Notifications activées !');
        } else {
          toast.error('Permission de notifications refusée');
        }
        return permission;
      } catch (error) {
        console.error('Erreur permission notifications:', error);
        toast.error('Erreur lors de la demande de permission');
      }
    } else {
      toast.error('Les notifications ne sont pas supportées par ce navigateur');
    }
  }, []);

  // Mettre à jour les canaux avec les compteurs de messages non lus
  const channelsWithUnreadCount = channels.map(channel => ({
    ...channel,
    unreadCount: unreadCounts[channel._id] || 0
  }));

  // Load channels
  const loadChannels = useCallback(async () => {
    try {
      const result = await ChannelService.getUserChannels();
      if (result.success) {
        const sortedChannels = ChannelService.sortChannelsByActivity(result.channels);
        setChannels(sortedChannels);
        setChannelsLoaded(true);
      }
    } catch (error) {
      console.error('Erreur chargement canaux:', error);
      toast.error('Erreur chargement canaux');
    } finally {
      setLoading(false);
    }
  }, []);

  // Sélection automatique du premier canal lorsque les canaux sont chargés
  useEffect(() => {
    if (channelsLoaded && channels.length > 0 && !selectedChannel) {
      setSelectedChannel(channels[0]);
    }
  }, [channelsLoaded, channels, selectedChannel]);

  // Load messages
  const loadMessages = useCallback(async (channelId) => {
    try {
      const result = await MessageService.getChannelMessages(channelId);
      if (result.success) {
        setMessages(result.messages);
      }
    } catch (error) {
      console.error('Erreur chargement messages:', error);
      toast.error('Erreur chargement messages');
    }
  }, []);

  // Initialize
  useEffect(() => {
    loadChannels();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Sync online users
  useEffect(() => {
    setOnlineUsers(socketOnlineUsers);
  }, [socketOnlineUsers]);

  // Channel selection effects
  useEffect(() => {
    if (selectedChannel) {
      // Marquer le canal comme lu
      markChannelAsRead(selectedChannel._id);

      // Ne charger les messages que si nous ne les avons pas déjà pour ce canal
      const hasMessages = messages.length > 0 && messages[0]?.channelId === selectedChannel._id;
      if (!hasMessages) {
        loadMessages(selectedChannel._id);
      }
      joinChannel(selectedChannel._id);
    }

    return () => {
      if (selectedChannel) {
        leaveChannel(selectedChannel._id);
      }
    };
  }, [selectedChannel, joinChannel, leaveChannel, loadMessages, messages, markChannelAsRead]);

  // Socket event listeners
  useEffect(() => {
    if (!socket) return;

    const handleNewMessage = (data) => {
      const { channelId, message } = data;

      // Si c'est le canal sélectionné, ajouter le message à la liste
      if (selectedChannel && channelId === selectedChannel._id) {
        setMessages(prev => {
          const exists = prev.find(m => m._id === message._id);
          if (!exists) return [...prev, message];
          return prev;
        });
      } else {
        // Si c'est un autre canal, incrémenter le compteur de messages non lus
        const channel = channels.find(c => c._id === channelId);
        if (channel && message.author._id !== user?._id) {
          setUnreadCounts(prev => {
            const newCounts = { ...prev };
            newCounts[channelId] = (newCounts[channelId] || 0) + 1;
            saveUnreadCounts(newCounts);
            return newCounts;
          });

          // Afficher une notification toast
          const channelName = channel.name;
          const authorName = message.author?.username || 'Utilisateur inconnu';
          const previewText = message.content.length > 50
            ? message.content.substring(0, 50) + '...'
            : message.content;

          toast.success(
            <div className="flex flex-col gap-1">
              <div className="font-semibold text-sm">#{channelName}</div>
              <div className="text-xs opacity-80">{authorName}: {previewText}</div>
            </div>,
            {
              duration: 4000,
              action: {
                label: 'Voir',
                onClick: () => {
                  // Trouver le canal et le sélectionner
                  const targetChannel = channels.find(c => c._id === channelId);
                  if (targetChannel) {
                    setSelectedChannel(targetChannel);
                    markChannelAsRead(channelId);
                  }
                }
              }
            }
          );

          // Notification du navigateur (si permission accordée)
          if ('Notification' in window && Notification.permission === 'granted' && document.hidden) {
            const notification = new Notification(`Nouveau message dans #${channelName}`, {
              body: `${authorName}: ${previewText}`,
              icon: '/logo192.png',
              tag: `channel-${channelId}`
            });

            notification.onclick = () => {
              window.focus();
              const targetChannel = channels.find(c => c._id === channelId);
              if (targetChannel) {
                setSelectedChannel(targetChannel);
                markChannelAsRead(channelId);
              }
              notification.close();
            };
          }
        }
      }
    };

    const handleMessageEdited = (data) => {
      const { messageId, message } = data;
      setMessages(prev => prev.map(m => m._id === messageId ? message : m));
    };

    const handleMessageDeleted = (data) => {
      const { messageId } = data;
      setMessages(prev => prev.filter(m => m._id !== messageId));
    };

    const handleReaction = (data) => {
      const { messageId, message } = data;
      setMessages(prev => prev.map(m => m._id === messageId ? message : m));
    };

    socket.on('new-message', handleNewMessage);
    socket.on('message-edited', handleMessageEdited);
    socket.on('message-deleted', handleMessageDeleted);
    socket.on('reaction-added', handleReaction);
    socket.on('reaction-removed', handleReaction);

    return () => {
      socket.off('new-message', handleNewMessage);
      socket.off('message-edited', handleMessageEdited);
      socket.off('message-deleted', handleMessageDeleted);
      socket.off('reaction-added', handleReaction);
      socket.off('reaction-removed', handleReaction);
    };
  }, [socket, selectedChannel, channels, user, markChannelAsRead, saveUnreadCounts]);

  // Actions
  const handleSendMessage = async (content) => {
    if (!selectedChannel) return;
    
    setSendingMessage(true);
    try {
      if (isConnected) {
        sendSocketMessage({
          content,
          channelId: selectedChannel._id
        });
      } else {
        const result = await MessageService.sendMessage({
          content,
          channelId: selectedChannel._id
        });
        if (result.success) {
          setMessages(prev => [...prev, result.message]);
        }
      }
    } catch (error) {
      console.error('Erreur envoi message:', error);
      toast.error('Erreur envoi message');
    } finally {
      setSendingMessage(false);
    }
  };

  const handleCreateChannel = async (name, description) => {
    try {
      const result = await ChannelService.createChannel({
        name,
        description,
        type: 'public'
      });

      if (result.success) {
        toast.success('Canal créé avec succès');
        setChannels(prev => [result.channel, ...prev]);
        setSelectedChannel(result.channel);
        return true;
      } else {
        toast.error(result.message || 'Erreur création canal');
        return false;
      }
    } catch (error) {
      console.error('Erreur création canal:', error);
      toast.error('Erreur lors de la création du canal');
      return false;
    }
  };

  const handleDeleteChannel = async (channelId) => {
    try {
      const result = await ChannelService.deleteChannel(channelId);

      if (result.success) {
        toast.success('Canal supprimé avec succès');
        setChannels(prev => prev.filter(channel => channel._id !== channelId));
        if (selectedChannel && selectedChannel._id === channelId) {
          setSelectedChannel(null);
        }
        return true;
      } else {
        toast.error(result.message || 'Erreur suppression canal');
        return false;
      }
    } catch (error) {
      console.error('Erreur suppression canal:', error);
      toast.error('Erreur lors de la suppression du canal');
      return false;
    }
  };

  return {
    channels: channelsWithUnreadCount,
    selectedChannel,
    messages,
    loading,
    sendingMessage,
    onlineUsers,
    isConnected,
    setChannels,
    setSelectedChannel,
    setMessages,
    sendMessage: handleSendMessage,
    createChannel: handleCreateChannel,
    deleteChannel: handleDeleteChannel,
    requestNotificationPermission,
    markChannelAsRead,
  };
};
