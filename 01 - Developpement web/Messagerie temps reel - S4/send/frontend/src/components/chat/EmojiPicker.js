import React, { useState } from 'react';
import { Button, Popover, PopoverTrigger, PopoverContent } from '@heroui/react';
import { FaSmile } from 'react-icons/fa';

const EmojiPicker = ({ onEmojiSelect, className = "" }) => {
  const [isOpen, setIsOpen] = useState(false);

  // Emojis communs pour les réactions
  const emojis = [
    '😀', '😂', '😊', '😍', '🥰', '😘', '😉', '😎', '🤔', '😮',
    '😢', '😭', '😤', '😡', '🥺', '😴', '🤤', '🤗', '🤔', '😐',
    '😑', '🙄', '😏', '😒', '🙂', '🤨', '😯', '😦', '😧', '😮',
    '😬', '🙁', '☹️', '😕', '😟', '🥺', '😔', '😞', '😖', '😣',
    '😩', '😫', '🥱', '😪', '😓', '😥', '😰', '😨', '😱', '😵',
    '👍', '👎', '👌', '✌️', '🤞', '👏', '🙌', '🤝', '🙏', '✍️',
    '💯', '🔥', '✨', '💫', '⭐', '🌟', '💥', '💣', '🎉', '🎊'
  ];

  const handleEmojiClick = (emoji) => {
    onEmojiSelect(emoji);
    setIsOpen(false);
  };

  return (
    <Popover
      isOpen={isOpen}
      onOpenChange={setIsOpen}
      placement="top"
      classNames={{
        content: "p-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg"
      }}
    >
      <PopoverTrigger>
        <Button
          isIconOnly
          variant="light"
          size="sm"
          radius="full"
          className={`text-gray-400 hover:text-yellow-500 ${className}`}
        >
          <FaSmile />
        </Button>
      </PopoverTrigger>
      <PopoverContent>
        <div className="grid grid-cols-10 gap-1 max-w-xs">
          {emojis.map((emoji, index) => (
            <button
              key={index}
              onClick={() => handleEmojiClick(emoji)}
              className="w-8 h-8 flex items-center justify-center text-lg hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
              title={`Ajouter ${emoji}`}
            >
              {emoji}
            </button>
          ))}
        </div>
      </PopoverContent>
    </Popover>
  );
};

export default EmojiPicker;
