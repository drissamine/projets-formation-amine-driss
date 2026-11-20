import { useState, useRef, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useMessages } from '../hooks/useMessages';
import { Send, User as UserIcon, MoreVertical, Search, MessageCircle } from 'lucide-react';
import toast from 'react-hot-toast';

const Messages = () => {
    const { user } = useAuth();
    const [activeConversation, setActiveConversation] = useState(null); // Conversation/User object
    const [newMessage, setNewMessage] = useState('');
    const messagesEndRef = useRef(null);

    const {
        conversations,
        messages,
        isLoadingConversations,
        isLoadingMessages,
        sendMessage
    } = useMessages(user?._id, activeConversation?._id);

    // Auto scroll to bottom when messages change
    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!newMessage.trim() || !activeConversation) return;

        try {
            await sendMessage({ conversationId: activeConversation._id, content: newMessage });
            setNewMessage('');
        } catch (err) {
            toast.error('Erreur envoi message');
        }
    };

    return (
        <div className="flex h-[calc(100vh-(--spacing(24)))] bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden max-w-6xl mx-auto my-6">

            {/* Sidebar - Liste des conversations */}
            <div className={`w-full md:w-1/3 border-r border-gray-200 dark:border-gray-700 flex flex-col ${activeConversation ? 'hidden md:flex' : 'flex'}`}>
                <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
                    <h2 className="text-xl font-bold text-gray-800 dark:text-white mb-4">Messages</h2>
                    <div className="relative">
                        <input
                            type="text"
                            placeholder="Rechercher..."
                            className="w-full pl-10 pr-4 py-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none"
                        />
                        <Search className="w-5 h-5 text-gray-400 absolute left-3 top-2.5" />
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto">
                    {isLoadingConversations ? (
                        <div className="flex justify-center p-4"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div></div>
                    ) : (
                        <div className="divide-y divide-gray-100 dark:divide-gray-800">
                            {conversations.map(conv => (
                                <div
                                    key={conv._id}
                                    onClick={() => setActiveConversation(conv)}
                                    className={`p-4 flex items-center space-x-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${activeConversation?._id === conv._id ? 'bg-blue-50 dark:bg-gray-700 border-l-4 border-blue-500' : ''}`}
                                >
                                    <div className="relative h-12 w-12">
                                        <div className="h-12 w-12 rounded-full bg-linear-to-tr from-purple-400 to-pink-500 flex items-center justify-center text-white font-bold text-lg">
                                            {conv.nom?.charAt(0).toUpperCase()}
                                        </div>
                                        {/* Online Status Indicator (Mock) */}
                                        <span className="absolute bottom-0 right-0 h-3 w-3 rounded-full bg-green-500 border-2 border-white dark:border-gray-800"></span>
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <h3 className="font-semibold text-gray-900 dark:text-white truncate">{conv.nom}</h3>
                                        <p className="text-sm text-gray-500 truncate">Cliquez pour voir la discussion</p>
                                    </div>
                                </div>
                            ))}
                            {conversations.length === 0 && (
                                <div className="p-8 text-center text-gray-500">
                                    Aucune conversation. Recherchez des utilisateurs pour discuter ! (Non implémenté)
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>

            {/* Chat Area */}
            <div className={`w-full md:w-2/3 flex flex-col ${!activeConversation ? 'hidden md:flex' : 'flex'}`}>
                {activeConversation ? (
                    <>
                        <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center bg-white dark:bg-gray-800">
                            <div className="flex items-center space-x-3">
                                <button onClick={() => setActiveConversation(null)} className="md:hidden text-gray-500 hover:text-gray-700">
                                    ←
                                </button>
                                <div className="h-10 w-10 rounded-full bg-linear-to-tr from-purple-400 to-pink-500 flex items-center justify-center text-white font-bold">
                                    {activeConversation.nom?.charAt(0).toUpperCase()}
                                </div>
                                <div>
                                    <h3 className="font-bold text-gray-900 dark:text-white">{activeConversation.nom}</h3>
                                    <span className="text-xs text-green-500 flex items-center">● En ligne</span>
                                </div>
                            </div>
                            <button className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700">
                                <MoreVertical className="w-5 h-5" />
                            </button>
                        </div>

                        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900 scrollbar-thin scrollbar-thumb-gray-300">
                            {messages.map(msg => {
                                const isMe = msg.sender === user?._id;
                                return (
                                    <div key={msg._id} className={`flex ${isMe ? 'justify-end' : 'justify-start'}`}>
                                        <div className={`max-w-[75%] rounded-2xl p-3 px-4 shadow-sm ${isMe
                                            ? 'bg-blue-600 text-white rounded-br-none'
                                            : 'bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 border border-gray-200 dark:border-gray-700 rounded-bl-none'
                                            }`}>
                                            <p>{msg.content}</p>
                                            <p className={`text-[10px] mt-1 text-right ${isMe ? 'text-blue-200' : 'text-gray-400'}`}>
                                                {new Date(msg.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                            </p>
                                        </div>
                                    </div>
                                );
                            })}
                            <div ref={messagesEndRef} />
                        </div>

                        <div className="p-4 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
                            <form onSubmit={handleSendMessage} className="flex space-x-2">
                                <input
                                    type="text"
                                    value={newMessage}
                                    onChange={(e) => setNewMessage(e.target.value)}
                                    placeholder="Écrivez un message..."
                                    className="flex-1 bg-gray-100 dark:bg-gray-700 border-none rounded-full px-5 py-3 focus:ring-2 focus:ring-blue-500 outline-none text-gray-900 dark:text-white"
                                />
                                <button
                                    type="submit"
                                    disabled={!newMessage.trim()}
                                    className="bg-blue-600 hover:bg-blue-700 text-white rounded-full p-3 transition-transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
                                >
                                    <Send className="w-5 h-5" />
                                </button>
                            </form>
                        </div>
                    </>
                ) : (
                    <div className="flex-1 flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-900 text-gray-500">
                        <div className="w-24 h-24 bg-gray-200 dark:bg-gray-800 rounded-full flex items-center justify-center mb-4">
                            <MessageCircle className="w-12 h-12 text-gray-400" />
                        </div>
                        <h3 className="text-xl font-semibold text-gray-700 dark:text-gray-300">Vos Messages</h3>
                        <p>Sélectionnez une conversation pour commencer à discuter</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Messages;
