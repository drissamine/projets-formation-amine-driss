import React, { useMemo, useRef, useEffect, useState } from 'react';
import { Avatar, Tooltip, Button, Textarea, Modal, ModalContent, ModalHeader, ModalBody, ModalFooter } from '@heroui/react';
import { FaHashtag, FaEdit, FaTrash, FaCheck, FaTimes, FaEllipsisV, FaPaperclip } from 'react-icons/fa';
import { Popover, PopoverTrigger, PopoverContent } from '@heroui/react';
import messageService from '../../services/messageService';
import { useSocket } from '../../hooks/useSocket';

const ChatMessages = ({ messages, user, onlineUsers, selectedChannel }) => {
  const messagesEndRef = useRef(null);
  const [editingMessage, setEditingMessage] = useState(null);
  const [editContent, setEditContent] = useState('');
  const [deleteModal, setDeleteModal] = useState({ open: false, message: null });

  const { editMessage, deleteMessage } = useSocket();

  // Optimisation : Créer un ensemble d'IDs utilisateurs en ligne pour des recherches O(1)
  const onlineUserIds = useMemo(() => {
    return new Set(onlineUsers.map(u => u.userId));
  }, [onlineUsers]);

  const isUserOnline = (userId) => {
    return onlineUserIds.has(userId);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleReactionClick = async (messageId, emoji) => {
    try {
      // Vérifier si l'utilisateur a déjà réagi avec cet emoji
      const message = messages.find(m => m._id === messageId);
      const reaction = message?.reactions?.find(r => r.emoji === emoji);
      const userId = user._id || user.id;
      const hasReacted = reaction?.users?.includes(userId);

      if (hasReacted) {
        // Remove reaction
        await messageService.removeReaction(messageId, emoji);
      } else {
        // Add reaction
        await messageService.addReaction(messageId, emoji);
      }

      // La mise à jour de la réaction sera gérée via les mises à jour socket/temps réel
      // Pour l'instant, nous allons juste appeler l'API
    } catch (error) {
      console.error('Erreur lors de la gestion de la réaction:', error);
    }
  };

  // Vérifier si l'utilisateur peut modifier un message
  const canEditMessage = (message) => {
    if (!message || !user) return false;

    // Vérifier l'auteur de différentes manières pour plus de robustesse
    const messageAuthorId = message.author?._id || message.author?.id;
    const userId = user._id || user.id;
    const isAuthor = messageAuthorId === userId;

    const hoursSinceCreation = (Date.now() - new Date(message.createdAt)) / (1000 * 60 * 60);

    // Log pour déboguer (temporaire)
    if (process.env.NODE_ENV === 'development') {
      console.log('canEditMessage check:', {
        messageId: message._id,
        messageAuthorId,
        userId,
        isAuthor,
        hoursSinceCreation,
        isDeleted: message.isDeleted,
        canEdit: isAuthor && hoursSinceCreation <= 24 && !message.isDeleted
      });
    }

    return isAuthor && hoursSinceCreation <= 24 && !message.isDeleted;
  };

  // Vérifier si l'utilisateur peut supprimer un message
  const canDeleteMessage = (message) => {
    if (!message || message.isDeleted) return false;

    // Vérifier l'auteur de différentes manières pour plus de robustesse
    const messageAuthorId = message.author?._id || message.author?.id;
    const userId = user._id || user.id;
    const isAuthor = messageAuthorId === userId;

    // Log pour déboguer (temporaire)
    if (process.env.NODE_ENV === 'development') {
      console.log('canDeleteMessage check:', {
        messageId: message._id,
        messageAuthorId,
        userId,
        isAuthor,
        isDeleted: message.isDeleted,
        canDelete: isAuthor
      });
    }

    // Pour l'instant, seuls les auteurs peuvent supprimer (pas d'admin côté frontend)
    return isAuthor;
  };

  // Démarrer l'édition d'un message
  const startEditing = (message) => {
    setEditingMessage(message._id);
    setEditContent(message.content);
  };

  // Annuler l'édition
  const cancelEditing = () => {
    setEditingMessage(null);
    setEditContent('');
  };

  // Sauvegarder l'édition
  const saveEditing = async () => {
    if (!editingMessage || !editContent.trim()) return;

    try {
      editMessage(editingMessage, editContent.trim());
      cancelEditing();
    } catch (error) {
      console.error('Erreur lors de la modification du message:', error);
    }
  };

  // Confirmer la suppression
  const confirmDelete = (message) => {
    setDeleteModal({ open: true, message });
  };

  // Supprimer le message
  const handleDelete = async () => {
    if (!deleteModal.message) return;

    try {
      deleteMessage(deleteModal.message._id);
      setDeleteModal({ open: false, message: null });
    } catch (error) {
      console.error('Erreur lors de la suppression du message:', error);
    }
  };

  if (messages.length === 0) {
    return (
      <div className="flex-1 overflow-y-auto px-4 md:px-8 py-6 space-y-6 bg-gray-50 dark:bg-gray-900/50 scroll-smooth">
          <div className="h-full flex flex-col items-center justify-center text-gray-400 opacity-60">
              <div className="w-20 h-20 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mb-4 shadow-inner">
                  <FaHashtag size={30} className="text-indigo-300 dark:text-indigo-700" />
              </div>
              <h3 className="text-xl font-semibold text-gray-700 dark:text-gray-300">C'est calme ici...</h3>
              <p className="text-sm max-w-xs text-center mt-2 text-gray-500">Soyez le premier à envoyer un message dans #{selectedChannel.name} !</p>
          </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto px-4 md:px-8 py-6 space-y-6 bg-gray-50 dark:bg-gray-900/50 scroll-smooth">
      {messages.map((message, index) => {
         const userId = user._id || user.id;
         const isMe = message.author && (message.author._id === userId || message.author.id === userId);
         // Vérifier si le message précédent était du même auteur pour une vue compacte
         const isSequence = index > 0 && messages[index-1].author && message.author && messages[index-1].author._id === message.author._id;
         
         return (
             <div key={message._id} className={`group flex gap-4 ${isSequence ? 'mt-1' : 'mt-6'} ${isMe ? 'flex-row-reverse' : ''} animate-in fade-in slide-in-from-bottom-2`}>
                 {!isSequence ? (
                     <div className="flex-shrink-0 mt-1">
                         <Tooltip content={message.author?.username || 'Utilisateur inconnu'} placement={isMe ? "left" : "right"}>
                             <div className="relative">
                                 <Avatar
                                    src={message.author?.avatar}
                                    name={message.author?.username || 'Inconnu'}
                                    className="w-9 h-9 text-sm shadow-sm"
                                    isBordered={message.author && isUserOnline(message.author._id)}
                                    color={message.author && isUserOnline(message.author._id) ? "success" : "default"}
                                 />
                                 {message.author && isUserOnline(message.author._id) && (
                                     <span className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-green-500 border-2 border-white dark:border-gray-900 rounded-full"></span>
                                 )}
                             </div>
                         </Tooltip>
                     </div>
                 ) : (
                     <div className="w-9 flex-shrink-0" />
                 )}
                 
                 <div className={`flex flex-col max-w-[80%] ${isMe ? 'items-end' : 'items-start'}`}>
                     {!isSequence && (
                         <div className={`flex items-baseline gap-2 mb-1 ${isMe ? 'flex-row-reverse' : ''}`}>
                             <span className="font-bold text-gray-900 dark:text-gray-100 text-sm hover:underline cursor-pointer">
                                {message.author?.username || 'Utilisateur inconnu'}
                             </span>
                             <span className="text-[10px] text-gray-400">
                                {formatTime(message.createdAt)}
                             </span>
                             {/* Menu d'actions pour les messages de l'utilisateur */}
                             {canEditMessage(message) || canDeleteMessage(message) ? (
                                 <div className={`opacity-0 group-hover:opacity-100 transition-opacity ${isMe ? 'order-first' : ''}`}>
                                     <Popover placement={isMe ? "left" : "right"}>
                                         <PopoverTrigger>
                                             <Button
                                                 isIconOnly
                                                 size="sm"
                                                 variant="light"
                                                 className="w-6 h-6 min-w-6 p-0"
                                             >
                                                 <FaEllipsisV className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" size={12} />
                                             </Button>
                                         </PopoverTrigger>
                                         <PopoverContent className="p-1">
                                             <div className="flex flex-col gap-1 min-w-[120px]">
                                                 {canEditMessage(message) && (
                                                     <Button
                                                         size="sm"
                                                         variant="light"
                                                         startContent={<FaEdit size={14} />}
                                                         onClick={() => startEditing(message)}
                                                         className="justify-start"
                                                     >
                                                         Modifier
                                                     </Button>
                                                 )}
                                                 {canDeleteMessage(message) && (
                                                     <Button
                                                         size="sm"
                                                         variant="light"
                                                         color="danger"
                                                         startContent={<FaTrash size={14} />}
                                                         onClick={() => confirmDelete(message)}
                                                         className="justify-start"
                                                     >
                                                         Supprimer
                                                     </Button>
                                                 )}
                                             </div>
                                         </PopoverContent>
                                     </Popover>
                                 </div>
                             ) : null}
                         </div>
                     )}

                     {/* Mode édition */}
                     {editingMessage === message._id ? (
                         <div className={`w-full ${isMe ? 'flex flex-col items-end' : ''}`}>
                             <Textarea
                                 value={editContent}
                                 onChange={(e) => setEditContent(e.target.value)}
                                 className="min-h-[80px] mb-2"
                                 placeholder="Modifier le message..."
                                 onKeyDown={(e) => {
                                     if (e.key === 'Enter' && !e.shiftKey) {
                                         e.preventDefault();
                                         saveEditing();
                                     } else if (e.key === 'Escape') {
                                         cancelEditing();
                                     }
                                 }}
                             />
                             <div className="flex gap-2">
                                 <Button
                                     size="sm"
                                     color="primary"
                                     onClick={saveEditing}
                                     startContent={<FaCheck size={12} />}
                                 >
                                     Sauvegarder
                                 </Button>
                                 <Button
                                     size="sm"
                                     variant="flat"
                                     onClick={cancelEditing}
                                     startContent={<FaTimes size={12} />}
                                 >
                                     Annuler
                                 </Button>
                             </div>
                         </div>
                     ) : (
                         <div
                            className={`px-4 py-2 rounded-2xl shadow-sm text-sm leading-relaxed whitespace-pre-wrap break-words relative
                              ${isMe
                                  ? 'bg-indigo-600 text-white rounded-tr-none'
                                  : 'bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-100 border border-gray-100 dark:border-gray-700 rounded-tl-none'
                              }
                            `}
                         >
                             {message.isDeleted ? (
                                 <span className="italic text-gray-500 dark:text-gray-400">[Message supprimé]</span>
                             ) : (
                                 <>
                                     {message.content}
                                     {message.isEdited && <span className="text-[9px] opacity-70 ml-1 italic">(modifié)</span>}
                                     {/* Affichage des pièces jointes (bientôt disponible) */}
                                     {message.attachments && message.attachments.length > 0 && (
                                         <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-600">
                                             <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                                                 <FaPaperclip size={10} />
                                                 <span>{message.attachments.length} pièce{message.attachments.length > 1 ? 's' : ''} jointe{message.attachments.length > 1 ? 's' : ''} (affichage bientôt disponible)</span>
                                             </div>
                                         </div>
                                     )}
                                 </>
                             )}
                         </div>
                     )}

                     {/* Reactions */}
                     {message.reactions && message.reactions.length > 0 && !message.isDeleted && (
                         <div className={`flex flex-wrap gap-1 mt-1.5 ${isMe ? 'justify-end' : 'justify-start'}`}>
                             {message.reactions.map((r, i) => {
                               const userId = user._id || user.id;
                               const hasReacted = r.users?.includes(userId);
                               return (
                                 <button
                                   key={i}
                                   onClick={() => handleReactionClick(message._id, r.emoji)}
                                   className={`inline-flex items-center px-1.5 py-0.5 rounded-full text-[10px] border shadow-sm hover:scale-105 transition-transform cursor-pointer ${
                                     hasReacted
                                       ? 'bg-indigo-100 dark:bg-indigo-900/40 border-indigo-300 dark:border-indigo-600 text-indigo-700 dark:text-indigo-300'
                                       : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 border-gray-200 dark:border-gray-700'
                                   }`}
                                 >
                                     {r.emoji} <span className="ml-1 font-semibold">{r.users?.length || 0}</span>
                                 </button>
                               );
                             })}
                         </div>
                     )}
                 </div>
             </div>
         );
      })}
      <div ref={messagesEndRef} />

      {/* Modal de confirmation de suppression */}
      <Modal isOpen={deleteModal.open} onOpenChange={() => setDeleteModal({ open: false, message: null })}>
        <ModalContent>
          <ModalHeader>Confirmer la suppression</ModalHeader>
          <ModalBody>
            <p>Êtes-vous sûr de vouloir supprimer ce message ?</p>
            {deleteModal.message && (
              <div className="mt-2 p-3 bg-gray-100 dark:bg-gray-800 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400 italic">
                  "{deleteModal.message.content}"
                </p>
              </div>
            )}
            <p className="text-sm text-gray-500 mt-2">
              Cette action ne peut pas être annulée.
            </p>
          </ModalBody>
          <ModalFooter>
            <Button
              variant="flat"
              onClick={() => setDeleteModal({ open: false, message: null })}
            >
              Annuler
            </Button>
            <Button
              color="danger"
              onClick={handleDelete}
            >
              Supprimer
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </div>
  );
};

export default ChatMessages;
