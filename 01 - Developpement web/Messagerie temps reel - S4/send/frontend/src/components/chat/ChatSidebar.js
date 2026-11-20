/**
 * Composant Sidebar du chat - Barre latérale affichant les canaux et informations utilisateur
 * Permet la navigation entre canaux, affichage du statut et déconnexion
 */
import React from 'react';
import { Button, Avatar } from '@heroui/react';
import { FaSignOutAlt, FaPlus, FaUsers, FaHashtag, FaLock, FaTrash, FaBell } from 'react-icons/fa';

const ChatSidebar = ({
  user,              // Utilisateur connecté
  channels,          // Liste des canaux de l'utilisateur
  selectedChannel,   // Canal actuellement sélectionné
  logout,            // Fonction de déconnexion
  onlineUsers,       // Liste des utilisateurs en ligne
  onSelectChannel,   // Fonction appelée lors de la sélection d'un canal
  onCreateChannelClick, // Fonction appelée pour créer un canal
  onDeleteChannel,   // Fonction appelée pour supprimer un canal
  onDirectMessageClick, // Fonction appelée pour ouvrir les messages directs
  isConnected,       // Statut de connexion Socket.io
  onRequestNotifications, // Fonction pour demander les permissions de notifications
}) => {
  const getChannelIcon = (channel) => {
    switch (channel.type) {
      case 'private': return <FaLock className="text-gray-400" />;
      case 'direct': return <FaUsers className="text-gray-400" />;
      default: return <FaHashtag className="text-gray-400" />; // public
    }
  };

  const handleDeleteChannel = (channelId, channelName) => {
    if (window.confirm(`Êtes-vous sûr de vouloir supprimer le canal "${channelName}" ? Cette action est irréversible.`)) {
      onDeleteChannel(channelId);
    }
  };

  return (
    <div className="hidden md:flex w-72 bg-gray-900 text-gray-100 flex-col border-r border-gray-800">
      
      {/* Sidebar Header */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-gray-800 bg-gray-900">
        <h1 className="text-lg font-bold tracking-wide text-white flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
            <span className="text-sm font-bold text-white">M</span>
          </div>
          Messagerie
        </h1>
      </div>

      {/* User Info & Connection Status */}
      <div className="p-4 bg-gray-800/30 border-b border-gray-800">
          <div className="flex items-center gap-3 mb-3">
              <Avatar 
                name={user?.username} 
                className="w-10 h-10 text-large ring-2 ring-indigo-500/30"
                showFallback 
              />
              <div className="flex flex-col">
                  <span className="font-semibold text-sm text-gray-100">{user?.username}</span>
                  <span className="text-xs text-green-400 flex items-center gap-1.5 font-medium">
                      <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                      </span>
                      En ligne
                  </span>
              </div>
          </div>
          
          <div className={`text-xs px-3 py-2 rounded-lg bg-black/20 flex items-center justify-between border ${isConnected ? 'border-green-500/20 text-green-400' : 'border-red-500/20 text-red-400'}`}>
              <span className="flex items-center gap-1.5 font-medium">
                 {isConnected ? 'Connecté' : 'Déconnecté'}
              </span>
              <span className="bg-gray-800 px-2 py-0.5 rounded text-gray-300 flex items-center gap-1">
                 {onlineUsers.length} <FaUsers className="text-[10px]"/>
              </span>
          </div>
      </div>

      {/* Channels List */}
      <div className="flex-1 overflow-y-auto py-4 px-3 custom-scrollbar">
        <div className="px-2 mb-3 flex items-center justify-between group">
           <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider group-hover:text-gray-300 transition-colors">Canaux</h3>
           <div className="flex items-center gap-1">
             <button
               onClick={onRequestNotifications}
               className="text-gray-500 hover:text-white transition-all p-1.5 rounded-md hover:bg-gray-800"
               title="Activer les notifications"
             >
                <FaBell size={10} />
             </button>
             <button
               onClick={onDirectMessageClick}
               className="text-gray-500 hover:text-white transition-all p-1.5 rounded-md hover:bg-gray-800"
               title="Message direct"
             >
                <FaUsers size={10} />
             </button>
             <button
               onClick={onCreateChannelClick}
               className="text-gray-500 hover:text-white transition-all p-1.5 rounded-md hover:bg-gray-800"
               title="Créer un canal"
             >
                <FaPlus size={10} />
             </button>
           </div>
        </div>
        
        <div className="space-y-1">
          {channels.map(channel => (
            <div
              key={channel._id}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group text-sm font-medium cursor-pointer ${
                selectedChannel?._id === channel._id
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-900/20'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-gray-100'
              }`}
              onClick={() => onSelectChannel(channel)}
            >
              <span className={`flex-shrink-0 ${selectedChannel?._id === channel._id ? 'text-indigo-200' : 'text-gray-500 group-hover:text-gray-400'}`}>
                  {getChannelIcon(channel)}
              </span>
              <span className="truncate flex-1">{channel.name}</span>
              {channel.creator && channel.creator._id === user._id && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteChannel(channel._id, channel.name);
                  }}
                  className="ml-auto p-1 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                  title="Supprimer le canal"
                >
                  <FaTrash size={12} />
                </button>
              )}
              {channel.unreadCount > 0 && ! (channel.creator && channel.creator._id === user._id) && (
                  <span className="ml-auto bg-indigo-500 text-white text-[10px] px-1.5 py-0.5 rounded-full min-w-[1.25rem] text-center font-bold">
                      {channel.unreadCount}
                  </span>
              )}
              {channel.unreadCount > 0 && channel.creator && channel.creator._id === user._id && (
                  <span className="bg-indigo-500 text-white text-[10px] px-1.5 py-0.5 rounded-full min-w-[1.25rem] text-center font-bold">
                      {channel.unreadCount}
                  </span>
              )}
            </div>
          ))}
          
          {channels.length === 0 && (
              <div className="text-center py-8 text-gray-600 text-xs px-4 border border-dashed border-gray-800 rounded-lg mx-2">
                  Aucun canal. <br/>Créez-en un pour discuter !
              </div>
          )}
        </div>
      </div>

      {/* Footer Sidebar (Logout) */}
      <div className="p-4 border-t border-gray-800 bg-gray-900">
           <Button 
              variant="light" 
              color="danger" 
              className="w-full justify-start text-red-400 hover:text-red-300 hover:bg-red-500/10 px-3 font-medium"
              startContent={<FaSignOutAlt />}
              onClick={logout}
           >
              Déconnexion
           </Button>
      </div>
    </div>
  );
};

export default ChatSidebar;
