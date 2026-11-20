import { Image, Send } from 'lucide-react';

const Home = () => {
    return (
        <div className="max-w-4xl mx-auto p-6 space-y-6">
            <header className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-bold bg-linear-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">
                    Fil d'actualité
                </h1>
            </header>

            {/* Create Post Widget */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 transition-all hover:shadow-xl border border-gray-100 dark:border-gray-700">
                <div className="flex space-x-4">
                    <div className="h-12 w-12 rounded-full bg-linear-to-br from-blue-400 to-purple-500 shrink-0" />
                    <div className="flex-1">
                        <input
                            type="text"
                            placeholder="Quoi de neuf ?"
                            className="w-full bg-gray-100 dark:bg-gray-700 rounded-full px-6 py-3 outline-none focus:ring-2 focus:ring-blue-500 transition-all text-gray-900 dark:text-white placeholder-gray-500"
                        />
                        <div className="flex justify-between items-center mt-4 pt-3 border-t border-gray-100 dark:border-gray-700">
                            <button className="flex items-center text-gray-500 hover:text-blue-500 transition-colors px-2 py-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700">
                                <Image className="w-5 h-5 mr-2" />
                                <span className="text-sm font-medium">Photo/Vidéo</span>
                            </button>
                            <button className="bg-blue-600 hover:bg-blue-700 text-white rounded-full py-2 px-6 font-medium transition-all transform hover:scale-105 active:scale-95 flex items-center shadow-md">
                                <Send className="w-4 h-4 mr-2" />
                                Publier
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Feed Stream */}
            <div className="space-y-6">
                {[1, 2, 3].map((post) => (
                    <div key={post} className="bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden hover:shadow-xl transition-all duration-300 border border-gray-100 dark:border-gray-700">
                        <div className="p-4 flex items-center space-x-3">
                            <div className="h-10 w-10 rounded-full bg-linear-to-tr from-yellow-400 to-orange-500" />
                            <div>
                                <h3 className="font-semibold text-gray-900 dark:text-white">Utilisateur {post}</h3>
                                <p className="text-xs text-gray-500">Il y a {post * 2} heures</p>
                            </div>
                        </div>
                        <div className="px-4 pb-2">
                            <p className="text-gray-800 dark:text-gray-200 leading-relaxed">
                                Voici un exemple de contenu de post pour montrer le design. Il utilise des ombres douces et des coins arrondis pour une esthétique moderne.
                            </p>
                        </div>
                        <div className="h-64 bg-gray-200 dark:bg-gray-700 mt-2 mx-4 rounded-lg animate-pulse" />
                        <div className="p-4 flex justify-between text-gray-500 border-t border-gray-100 dark:border-gray-700 mt-4">
                            <button className="flex items-center hover:text-red-500 transition-colors space-x-1">
                                <span>❤️</span> <span>J'aime</span>
                            </button>
                            <button className="flex items-center hover:text-blue-500 transition-colors space-x-1">
                                <span>💬</span> <span>Commenter</span>
                            </button>
                            <button className="flex items-center hover:text-green-500 transition-colors space-x-1">
                                <span>🔄</span> <span>Partager</span>
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
export default Home;
