import React, { useState } from 'react';
import { Button, Input, Tooltip } from '@heroui/react';
import { FaPlus, FaPaperPlane } from 'react-icons/fa';
import EmojiPicker from './EmojiPicker';

const ChatInput = ({ selectedChannel, OnSendMessage, isConnected, sendingMessage }) => {
  const [newMessage, setNewMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedChannel || sendingMessage) return;
    
    OnSendMessage(newMessage.trim());
    setNewMessage('');
  };

  return (
    <div className="p-4 md:p-6 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 z-10">
      <form onSubmit={handleSubmit} className="relative max-w-4xl mx-auto shadow-sm rounded-2xl bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 focus-within:ring-2 focus-within:ring-indigo-500/50 focus-within:border-indigo-500 transition-all">
         <div className="absolute left-2 top-1/2 -translate-y-1/2 z-10 hidden sm:block">
            <Tooltip content="Pièces jointes bientôt disponibles" placement="top">
               <Button isIconOnly variant="light" size="sm" radius="full" className="text-gray-400 hover:text-indigo-500" isDisabled>
                  <FaPlus />
               </Button>
            </Tooltip>
         </div>
         <Input
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder={`Message à #${selectedChannel.name}...`}
            className="w-full"
            size="lg"
            radius="none"
            isDisabled={sendingMessage}
            classNames={{
               input: "pl-2 sm:pl-10 pr-20 text-gray-900 dark:text-white bg-transparent text-sm md:text-base",
               inputWrapper: "bg-transparent shadow-none hover:bg-transparent border-none py-3 h-auto"
            }}
         />
         <div className="absolute right-2 top-1/2 -translate-y-1/2 z-10 flex items-center gap-1">
            <EmojiPicker
                onEmojiSelect={(emoji) => setNewMessage(prev => prev + emoji)}
                className="hidden sm:flex"
            />
            <Button
                type="submit"
                isIconOnly
                color={!newMessage.trim() ? "default" : "primary"}
                variant={!newMessage.trim() ? "light" : "shadow"}
                isDisabled={!newMessage.trim() || sendingMessage}
                isLoading={sendingMessage}
                size="sm"
                radius="full"
                className={!newMessage.trim() ? "text-gray-400" : "bg-indigo-600"}
            >
                {!sendingMessage && <FaPaperPlane size={12} />}
            </Button>
         </div>
      </form>
      <div className="text-center mt-3">
           <p className="text-[10px] text-gray-400 flex items-center justify-center gap-2">
              {isConnected ? (
                  <span className="flex items-center gap-1.5 text-green-600 dark:text-green-500/70">
                      <span className="w-1.5 h-1.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]"></span>
                      Connecté au serveur temps réel
                  </span>
              ) : (
                  <span className="text-yellow-500 flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-yellow-500"></span>
                      Mode déconnecté (API)
                  </span>
              )}
           </p>
      </div>
    </div>
  );
};

export default ChatInput;
