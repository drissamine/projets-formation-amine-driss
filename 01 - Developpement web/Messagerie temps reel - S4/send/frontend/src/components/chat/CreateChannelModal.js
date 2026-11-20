import React, { useState, useEffect } from 'react';
import { FaHashtag, FaTimes } from 'react-icons/fa';

const CreateChannelModal = ({ isOpen, onClose, onCreateChannel }) => {
  const [newChannelName, setNewChannelName] = useState('');
  const [newChannelDesc, setNewChannelDesc] = useState('');
  const [loading, setLoading] = useState(false);

  // Empêcher le défilement du corps lorsque la modal est ouverte
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!newChannelName.trim()) return;
    setLoading(true);
    await onCreateChannel(newChannelName, newChannelDesc);
    setLoading(false);
    setNewChannelName('');
    setNewChannelDesc('');
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
              <div className="p-2 bg-indigo-100 dark:bg-indigo-900/50 rounded-lg">
                <FaHashtag className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">Créer un canal</h2>
                <p className="text-sm text-gray-500">Créez un espace pour un nouveau sujet.</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
            >
              <FaTimes className="w-5 h-5 text-gray-400" />
            </button>
          </div>

          {/* Body */}
          <form onSubmit={handleSubmit} className="p-6 space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Nom du canal
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <FaHashtag className="w-4 h-4 text-gray-400" />
                </div>
                <input
                  type="text"
                  placeholder="ex: projet-design"
                  value={newChannelName}
                  onChange={(e) => setNewChannelName(e.target.value)}
                  maxLength={30}
                  required
                  autoFocus
                  className="w-full pl-10 pr-3 py-3 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500"
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">Utilisez des minuscules, sans espaces.</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Description
              </label>
              <textarea
                placeholder="De quoi parle ce canal ?"
                value={newChannelDesc}
                onChange={(e) => setNewChannelDesc(e.target.value)}
                maxLength={200}
                rows={3}
                className="w-full px-3 py-3 border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 resize-none"
              />
            </div>
          </form>

          {/* Footer */}
          <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-100 dark:border-gray-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
            >
              Annuler
            </button>
            <button
              type="submit"
              onClick={handleSubmit}
              disabled={!newChannelName.trim() || loading}
              className="px-6 py-2 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed rounded-lg transition-colors shadow-md"
            >
              {loading ? 'Création...' : 'Créer le canal'}
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default CreateChannelModal;
