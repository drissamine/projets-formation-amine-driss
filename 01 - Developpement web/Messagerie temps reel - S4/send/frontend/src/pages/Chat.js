/**
 * Page principale du chat - Interface de messagerie avec canaux et messages
 * Gère l'affichage des canaux, messages, et les interactions utilisateur
 */
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useChatState } from '../hooks/useChatState';
import { Button, Avatar, Tooltip, Divider } from '@heroui/react';
import { FaSearch, FaInfoCircle, FaPlus, FaHashtag, FaLock, FaUsers } from 'react-icons/fa';

// Composants de l'interface chat
import ChatSidebar from '../components/chat/ChatSidebar';
import ChatMessages from '../components/chat/ChatMessages';
import ChatInput from '../components/chat/ChatInput';
import CreateChannelModal from '../components/chat/CreateChannelModal';
import SearchModal from '../components/chat/SearchModal';
import ChannelInfoModal from '../components/chat/ChannelInfoModal';
import DirectMessageModal from '../components/chat/DirectMessageModal';

const Chat = () => {
  const { user, logout } = useAuth();
  const [showCreateModal, setShowCreateModal] = useState(false); // État de la modal de création
  const [showSearchModal, setShowSearchModal] = useState(false); // État de la modal de recherche
  const [showInfoModal, setShowInfoModal] = useState(false); // État de la modal d'informations
  const [showDirectMessageModal, setShowDirectMessageModal] = useState(false); // État de la modal de message direct

  const {
    channels,
    selectedChannel,
    messages,
    loading,
    sendingMessage,
    onlineUsers,
    isConnected,
    setSelectedChannel,
    sendMessage,
    createChannel,
    deleteChannel,
    requestNotificationPermission
  } = useChatState(user);

  const onCreateChannel = async (name, description) => {
    const success = await createChannel(name, description);
    if (success) {
      setShowCreateModal(false);
    }
  };

  const handleCreateChannelClick = () => {
    setShowCreateModal(true);
  };

  const closeCreateModal = () => {
    setShowCreateModal(false);
  };

  const handleDirectMessageClick = () => {
    setShowDirectMessageModal(true);
  };

  const closeDirectMessageModal = () => {
    setShowDirectMessageModal(false);
  };

  const onChannelCreated = (channel) => {
    // Actualiser les canaux et sélectionner le nouveau canal
    setSelectedChannel(channel);
  };

  const getChannelIcon = (channel) => {
    switch (channel.type) {
      case 'private': return <FaLock className="text-gray-400" />;
      case 'direct': return <FaUsers className="text-gray-400" />;
      default: return <FaHashtag className="text-gray-400" />;
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gray-50 dark:bg-gray-900 text-gray-600 dark:text-gray-400">
        <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mb-4"></div>
        <p className="font-medium">Chargement de votre espace...</p>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-100 dark:bg-gray-900 overflow-hidden font-sans">
      <ChatSidebar
        user={user}
        channels={channels}
        selectedChannel={selectedChannel}
        logout={logout}
        onlineUsers={onlineUsers}
        onSelectChannel={setSelectedChannel}
        onCreateChannelClick={handleCreateChannelClick}
        onDirectMessageClick={handleDirectMessageClick}
        onDeleteChannel={deleteChannel}
        onRequestNotifications={requestNotificationPermission}
        isConnected={isConnected}
      />

      <div className="flex-1 flex flex-col min-w-0 bg-white dark:bg-gray-900 relative">
         {selectedChannel ? (
            <>
               {/* Header */}
               <div className="h-16 border-b border-gray-200 dark:border-gray-800 px-6 flex items-center justify-between bg-white dark:bg-gray-900/80 backdrop-blur-md sticky top-0 z-20">
                  <div className="flex flex-col justify-center">
                      <div className="flex items-center gap-2 text-gray-800 dark:text-gray-100 font-bold text-lg">
                          <span className="text-gray-400 sm:hidden md:inline">{getChannelIcon(selectedChannel)}</span>
                          <span className="text-gray-400 md:hidden">#</span>
                          {selectedChannel.name}
                      </div>
                      <p className="text-xs text-gray-500 truncate max-w-xs md:max-w-md">
                        {selectedChannel.description || "Discussion générale"}
                      </p>
                  </div>
                  <div className="flex items-center gap-3">
                      <div className="hidden md:flex items-center -space-x-2 mr-2">
                         {onlineUsers.slice(0, 3).map((u, index) => (
                             <Tooltip key={`${u.userId}-${index}`} content={u.username}>
                                <div className="border-2 border-white dark:border-gray-900 rounded-full cursor-pointer hover:z-10 transition-transform hover:scale-105">
                                    <Avatar name={u.username} size="sm" className="w-7 h-7 text-[10px]" />
                                </div>
                             </Tooltip>
                         ))}
                         {onlineUsers.length > 3 && (
                             <div className="w-7 h-7 rounded-full bg-gray-100 dark:bg-gray-800 border-2 border-white dark:border-gray-900 flex items-center justify-center text-[10px] font-bold text-gray-500">
                                 +{onlineUsers.length - 3}
                             </div>
                         )}
                      </div>
                      <Divider orientation="vertical" className="h-6 hidden md:block" />
                      <Button
                        isIconOnly
                        variant="light"
                        radius="full"
                        className="text-gray-400 hover:text-gray-600 hidden sm:flex"
                        onClick={() => setShowSearchModal(true)}
                      >
                         <FaSearch />
                      </Button>
                      <Button
                        isIconOnly
                        variant="light"
                        radius="full"
                        className="text-gray-400 hover:text-indigo-600"
                        onClick={() => setShowInfoModal(true)}
                      >
                         <FaInfoCircle />
                      </Button>
                  </div>
               </div>

               <ChatMessages 
                 messages={messages} 
                 user={user} 
                 onlineUsers={onlineUsers} 
                 selectedChannel={selectedChannel}
               />

               <ChatInput 
                 selectedChannel={selectedChannel}
                 OnSendMessage={sendMessage}
                 isConnected={isConnected}
                 sendingMessage={sendingMessage}
               />
            </>
         ) : (
            <div className="flex-1 flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-900 text-center p-8 bg-grid-pattern">
                <div className="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-xl mb-8 transform transition-all hover:scale-105 border border-gray-100 dark:border-gray-700">
                     <div className="w-20 h-20 bg-indigo-100 dark:bg-indigo-900/40 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse-slow">
                        <FaHashtag className="w-8 h-8 text-indigo-500" />
                     </div>
                     <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">Bienvenue !</h2>
                     <p className="text-gray-500 dark:text-gray-400 max-w-sm mx-auto leading-relaxed">
                        Sélectionnez un canal pour commencer à discuter ou créez une nouvelle communauté.
                     </p>
                </div>
                <Button 
                   color="primary" 
                   size="lg" 
                   onPress={() => setShowCreateModal(true)}
                   startContent={<FaPlus />}
                   className="shadow-lg hover:translate-y-[-2px] transition-transform bg-indigo-600 font-semibold"
                >
                    Créer un nouveau canal
                </Button>
            </div>
         )}
      </div>

      <CreateChannelModal
        isOpen={showCreateModal}
        onClose={closeCreateModal}
        onCreateChannel={onCreateChannel}
      />

      <SearchModal
        isOpen={showSearchModal}
        onClose={() => setShowSearchModal(false)}
        selectedChannel={selectedChannel}
      />

      <ChannelInfoModal
        isOpen={showInfoModal}
        onClose={() => setShowInfoModal(false)}
        selectedChannel={selectedChannel}
        currentUser={user}
      />

      <DirectMessageModal
        isOpen={showDirectMessageModal}
        onClose={closeDirectMessageModal}
        onChannelCreated={onChannelCreated}
      />
    </div>
  );
};

export default Chat;
