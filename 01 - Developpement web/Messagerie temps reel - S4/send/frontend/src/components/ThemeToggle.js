import React from 'react';
import { useTheme } from '../context/ThemeContext';
import { motion } from 'framer-motion';

const ThemeToggle = () => {
  const { isDarkMode, toggleTheme } = useTheme();

  return (
    <motion.button
      onClick={toggleTheme}
      className="relative p-2 rounded-full bg-white dark:bg-gray-800 shadow-lg border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50"
      whileTap={{ scale: 0.95 }}
      aria-label="Toggle theme"
      title="Changer de thème"
    >
      <div className="relative w-6 h-6">
        {/* Sun Icon */}
        <motion.div
          className="absolute inset-0 flex items-center justify-center"
          animate={{
            opacity: isDarkMode ? 0 : 1,
            scale: isDarkMode ? 0.5 : 1
          }}
          transition={{ duration: 0.3 }}
        >
          <svg className="w-4 h-4 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
          </svg>
        </motion.div>
        
        {/* Moon Icon */}
        <motion.div
          className="absolute inset-0 flex items-center justify-center"
          animate={{
            opacity: isDarkMode ? 1 : 0,
            scale: isDarkMode ? 1 : 0.5
          }}
          transition={{ duration: 0.3 }}
        >
          <svg className="w-4 h-4 text-indigo-400" fill="currentColor" viewBox="0 0 20 20">
            <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
          </svg>
        </motion.div>
        
        {/* Animated ring */}
        <motion.div
          className="absolute inset-0 rounded-full border-2 border-transparent"
          animate={{
            borderColor: isDarkMode ? '#6366F1' : '#F59E0B',
            scale: isDarkMode ? 1.2 : 1
          }}
          transition={{ duration: 0.3 }}
        />
      </div>
    </motion.button>
  );
};

export default ThemeToggle;