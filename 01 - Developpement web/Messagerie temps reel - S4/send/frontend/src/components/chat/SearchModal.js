import React, { useState } from 'react';
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter, Button, Input, Spinner, Avatar } from '@heroui/react';
import { FaSearch } from 'react-icons/fa';
import messageService from '../../services/messageService';

const SearchModal = ({ isOpen, onClose, selectedChannel }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim() || query.trim().length < 2) return;

    setLoading(true);
    try {
      const response = await messageService.searchMessages(selectedChannel._id, query.trim());
      if (response.success) {
        setResults(response.messages);
      } else {
        setResults([]);
      }
    } catch (error) {
      console.error('Erreur lors de la recherche:', error);
      setResults([]);
    } finally {
      setLoading(false);
      setSearched(true);
    }
  };

  const handleClose = () => {
    setQuery('');
    setResults([]);
    setLoading(false);
    setSearched(false);
    onClose();
  };

  const formatTime = (date) => {
    return new Date(date).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'short',
      year: new Date(date).getFullYear() !== new Date().getFullYear() ? 'numeric' : undefined
    });
  };

  const highlightText = (text, query) => {
    if (!query) return text;
    const regex = new RegExp(`(${query})`, 'gi');
    const parts = text.split(regex);
    return parts.map((part, index) =>
      regex.test(part) ? <mark key={index} className="bg-yellow-200 text-gray-900 px-1 rounded">{part}</mark> : part
    );
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      size="2xl"
      classNames={{
        base: "bg-white dark:bg-gray-800",
        header: "border-b border-gray-200 dark:border-gray-700",
        body: "py-6",
        footer: "border-t border-gray-200 dark:border-gray-700"
      }}
    >
      <ModalContent>
        <ModalHeader className="flex items-center gap-2">
          <FaSearch className="text-gray-400" />
          Rechercher dans #{selectedChannel?.name}
        </ModalHeader>

        <ModalBody>
          <form onSubmit={handleSearch} className="mb-6">
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Rechercher dans les messages..."
              size="lg"
              startContent={<FaSearch className="text-gray-400" />}
              classNames={{
                input: "text-gray-900 dark:text-white",
                inputWrapper: "bg-gray-50 dark:bg-gray-700"
              }}
              autoFocus
            />
          </form>

          {loading && (
            <div className="flex items-center justify-center py-8">
              <Spinner size="lg" color="primary" />
              <span className="ml-3 text-gray-600 dark:text-gray-400">Recherche en cours...</span>
            </div>
          )}

          {searched && !loading && (
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {results.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <FaSearch size={48} className="mx-auto mb-4 opacity-50" />
                  <p className="text-lg font-medium">Aucun résultat trouvé</p>
                  <p className="text-sm">Essayez avec des termes différents</p>
                </div>
              ) : (
                <>
                  <p className="text-sm text-gray-500 mb-4">
                    {results.length} résultat{results.length > 1 ? 's' : ''} pour "{query}"
                  </p>
                  {results.map((message) => (
                    <div
                      key={message._id}
                      className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors cursor-pointer"
                      onClick={() => {
                        // Défiler vers le message (nécessiterait une implémentation)
                        handleClose();
                      }}
                    >
                      <div className="flex items-start gap-3">
                        <Avatar
                          src={message.author.avatar}
                          name={message.author.username}
                          size="sm"
                          className="flex-shrink-0"
                        />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-semibold text-gray-900 dark:text-gray-100">
                              {message.author.username}
                            </span>
                            <span className="text-xs text-gray-500">
                              {formatTime(message.createdAt)}
                            </span>
                          </div>
                          <p className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed">
                            {highlightText(message.content, query)}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </>
              )}
            </div>
          )}
        </ModalBody>

        <ModalFooter>
          <Button variant="light" onPress={handleClose}>
            Fermer
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default SearchModal;
