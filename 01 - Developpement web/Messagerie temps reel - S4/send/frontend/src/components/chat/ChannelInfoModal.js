import React, { useState, useEffect, useCallback } from 'react';
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter, Button, Avatar, Badge, Spinner } from '@heroui/react';
import { FaInfoCircle, FaUsers, FaCalendarAlt, FaHashtag, FaUser } from 'react-icons/fa';
import channelService from '../../services/channelService';

const ChannelInfoModal = ({ isOpen, onClose, selectedChannel, currentUser }) => {
  const [channelDetails, setChannelDetails] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadChannelDetails = useCallback(async () => {
    setLoading(true);
    try {
      console.log('Loading channel details for:', selectedChannel._id);
      const response = await channelService.getChannelDetails(selectedChannel._id);
      console.log('Channel details response:', response);
      if (response.success) {
        setChannelDetails(response.channel);
      } else {
        console.error('Channel details error:', response.message);
        setChannelDetails(null);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des détails du canal:', error);
      setChannelDetails(null);
    } finally {
      setLoading(false);
    }
  }, [selectedChannel?._id]);

  useEffect(() => {
    if (isOpen && selectedChannel) {
      loadChannelDetails();
    }
  }, [isOpen, selectedChannel, loadChannelDetails]);

  const formatDate = (date) => {
    return new Date(date).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  };



  const getChannelTypeLabel = (type) => {
    switch (type) {
      case 'private': return 'Privé';
      case 'direct': return 'Conversation directe';
      default: return 'Public';
    }
  };

  if (!selectedChannel) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      size="lg"
      classNames={{
        base: "bg-white dark:bg-gray-800",
        header: "border-b border-gray-200 dark:border-gray-700",
        body: "py-6",
        footer: "border-t border-gray-200 dark:border-gray-700"
      }}
    >
      <ModalContent>
        <ModalHeader className="flex items-center gap-3">
          <div className="p-2 bg-indigo-100 dark:bg-indigo-900/40 rounded-full">
            <FaInfoCircle className="text-indigo-500" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Informations du canal
            </h3>
            <p className="text-sm text-gray-500">#{selectedChannel.name}</p>
          </div>
        </ModalHeader>

        <ModalBody>
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Spinner size="lg" color="primary" />
              <span className="ml-3 text-gray-600 dark:text-gray-400">Chargement...</span>
            </div>
          ) : channelDetails ? (
            <div className="space-y-6">
              {/* Informations générales */}
              <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center gap-2">
                  <FaHashtag className="text-gray-400" />
                  Informations générales
                </h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Nom du canal</span>
                    <span className="font-medium text-gray-900 dark:text-gray-100">#{channelDetails.name}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Type</span>
                    <Badge color={channelDetails.type === 'private' ? 'danger' : 'primary'} variant="flat">
                      {getChannelTypeLabel(channelDetails.type)}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Créé le</span>
                    <span className="font-medium text-gray-900 dark:text-gray-100">
                      {formatDate(channelDetails.createdAt)}
                    </span>
                  </div>
                  <div className="flex items-start justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Description</span>
                    <span className="font-medium text-gray-900 dark:text-gray-100 text-right max-w-xs">
                      {channelDetails.description || 'Aucune description'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Créateur */}
              <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center gap-2">
                  <FaUser className="text-gray-400" />
                  Créateur
                </h4>
                <div className="flex items-center gap-3">
                  <Avatar
                    src={channelDetails.creator.avatar}
                    name={channelDetails.creator.username}
                    size="sm"
                  />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-gray-100">
                      {channelDetails.creator.username}
                    </p>
                    <p className="text-sm text-gray-500">
                      {channelDetails.creator.email}
                    </p>
                  </div>
                </div>
              </div>

              {/* Membres */}
              <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center gap-2">
                  <FaUsers className="text-gray-400" />
                  Membres ({channelDetails.participants?.length || 0})
                </h4>
                <div className="space-y-3 max-h-48 overflow-y-auto">
                  {channelDetails.participants?.map((participant) => (
                    <div key={participant.user._id} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Avatar
                          src={participant.user.avatar}
                          name={participant.user.username}
                          size="sm"
                        />
                        <div>
                          <p className="font-medium text-gray-900 dark:text-gray-100">
                            {participant.user.username}
                            {participant.user._id === currentUser?._id && (
                              <span className="text-xs text-indigo-500 ml-2">(Vous)</span>
                            )}
                          </p>
                          <p className="text-sm text-gray-500">
                            {participant.user.email}
                          </p>
                        </div>
                      </div>
                      <Badge
                        color={participant.role === 'admin' ? 'primary' : 'default'}
                        variant="flat"
                        size="sm"
                      >
                        {participant.role === 'admin' ? 'Admin' : 'Membre'}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>

              {/* Statistiques */}
              <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center gap-2">
                  <FaCalendarAlt className="text-gray-400" />
                  Statistiques
                </h4>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-indigo-500">
                      {channelDetails.participants?.length || 0}
                    </p>
                    <p className="text-sm text-gray-500">Membres</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-500">
                      {channelDetails.lastMessage ? '1+' : '0'}
                    </p>
                    <p className="text-sm text-gray-500">Messages</p>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <FaInfoCircle size={48} className="mx-auto mb-4 opacity-50" />
              <p className="font-medium mb-2">Impossible de charger les informations du canal</p>
              <p className="text-sm text-gray-400">ID du canal: {selectedChannel?._id}</p>
              <p className="text-sm text-gray-400">Nom: {selectedChannel?.name}</p>
              <p className="text-sm text-gray-400">Vérifiez la console pour plus de détails</p>
            </div>
          )}
        </ModalBody>

        <ModalFooter>
          <Button variant="light" onPress={onClose}>
            Fermer
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default ChannelInfoModal;
