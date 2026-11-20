import React, { useState, useEffect } from 'react';
import { FaTimes, FaUser, FaSearch, FaEnvelope } from 'react-icons/fa';
import { Avatar } from '@heroui/react';
import channelService from '../../services/channelService';
import { useAuth } from '../../context/AuthContext';

const DirectMessageModal = ({ isOpen, onClose, onChannelCreated }) => {
  const { user: currentUser } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [creating, setCreating] = useState(false);

  // Charger la liste des utilisateurs depuis l'API
  useEffect(() => {
    const loadUsers = async () => {
      try {
        const result = await channelService.getUsers();
        if (result.success) {
          setUsers(result.users);
          setFilteredUsers(result.users);
        } else {
          console.error('Erreur lors du chargement des utilisateurs:', result.message);
          // En cas d'erreur, afficher une liste vide
          setUsers([]);
          setFilteredUsers([]);
        }
      } catch (error) {
        console.error('Erreur lors du chargement des utilisateurs:', error);
        setUsers([]);
        setFilteredUsers([]);
      }
    };

    loadUsers();
  }, []);

  // Filtrer les utilisateurs selon la recherche
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredUsers(users);
    } else {
      const filtered = users.filter(user =>
        user.username.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredUsers(filtered);
    }
  }, [searchQuery, users]);

  // Empêcher le scroll du body quand le modal est ouvert
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  const handleCreateDirectChannel = async (targetUser) => {
    if (creating) return;

    setCreating(true);
    try {
      const result = await channelService.createOrGetDirectChannel(targetUser._id);

      if (result.success) {
        onChannelCreated(result.channel);
        onClose();
        // Afficher un message de succès
        if (result.isNew) {
          alert(`Canal direct créé avec ${targetUser.username}`);
        } else {
          alert(`Canal direct ouvert avec ${targetUser.username}`);
        }
      } else {
        alert(`Erreur: ${result.message}`);
      }
    } catch (error) {
      alert('Erreur lors de la création du canal direct');
    } finally {
      setCreating(false);
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-[9998] backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 flex items-center justify-center z-[9999] p-4">
        <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-md border border-gray-200 dark:border-gray-800">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-100 dark:border-gray-800">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 dark:bg-blue-900/50 rounded-lg">
                <FaEnvelope className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">Message direct</h2>
                <p className="text-sm text-gray-500">Démarrer une conversation privée</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
            >
              <FaTimes className="w-5 h-5 text-gray-400" />
            </button>
          </div>

          {/* Search */}
          <div className="p-6 border-b border-gray-100 dark:border-gray-800">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <FaSearch className="w-4 h-4 text-gray-400" />
              </div>
              <input
                type="text"
                placeholder="Rechercher un utilisateur..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-3 py-3 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500"
                autoFocus
              />
            </div>
          </div>

          {/* User List */}
          <div className="max-h-80 overflow-y-auto">
            {filteredUsers.length === 0 ? (
              <div className="p-6 text-center text-gray-500">
                <FaUser className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                <p>Aucun utilisateur trouvé</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-100 dark:divide-gray-800">
                {filteredUsers
                  .filter(user => user._id !== currentUser._id) // Ne pas afficher l'utilisateur actuel
                  .map(user => (
                  <div
                    key={user._id}
                    className="flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors cursor-pointer"
                    onClick={() => handleCreateDirectChannel(user)}
                  >
                    <div className="flex items-center gap-3">
                      <Avatar
                        name={user.username}
                        src={user.avatar}
                        className="w-10 h-10 text-large"
                        showFallback
                      />
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">{user.username}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`inline-flex h-2 w-2 rounded-full ${
                        user.status === 'online' ? 'bg-green-400' :
                        user.status === 'away' ? 'bg-yellow-400' : 'bg-gray-400'
                      }`} />
                      <span className="text-xs text-gray-500 capitalize">{user.status}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-100 dark:border-gray-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
            >
              Annuler
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default DirectMessageModal;
