import { useState } from 'react';
import { usePosts } from '../hooks/usePosts';
import { useAuth } from '../hooks/useAuth';
import toast from 'react-hot-toast';
import { Heart, MessageCircle, Trash2, Send, Image as ImageIcon, Loader } from 'lucide-react';
import { PostSkeleton } from '../components/skeletons/PostSkeleton';

const Posts = () => {
    const { user } = useAuth();
    const [page, setPage] = useState(1);
    const { posts, totalPages, isLoading, createPost, isCreating, deletePost, toggleLike } = usePosts(page);
    const [newPostContent, setNewPostContent] = useState('');

    const handleCreatePost = async (e) => {
        e.preventDefault();
        if (!newPostContent.trim()) return;

        try {
            const formData = new FormData();
            formData.append('contenu', newPostContent);

            await createPost(formData);
            setNewPostContent('');
            toast.success('Post publié !');
        } catch (err) {
            toast.error('Impossible de publier le post');
        }
    };

    const handleDelete = async (postId) => {
        if (!window.confirm('Voulez-vous vraiment supprimer ce post ?')) return;
        try {
            await deletePost(postId);
            toast.success('Post supprimé');
        } catch (err) {
            toast.error('Erreur lors de la suppression');
        }
    };

    const handleLike = async (post) => {
        const isLiked = post.likes.includes(user._id);
        try {
            await toggleLike({ postId: post._id, userId: user._id, isLiked });
        } catch (err) {
            toast.error('Erreur action like');
        }
    };

    return (
        <div className="max-w-3xl mx-auto p-4 md:p-6 space-y-6">
            <h1 className="text-3xl font-bold bg-linear-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-6">Fil d'actualité</h1>

            {/* Création de Post */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-100 dark:border-gray-700">
                <form onSubmit={handleCreatePost}>
                    <div className="flex space-x-4">
                        <div className="h-10 w-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold shrink-0">
                            {user?.nom?.charAt(0).toUpperCase()}
                        </div>
                        <div className="flex-1">
                            <textarea
                                className="w-full bg-gray-50 dark:bg-gray-700 rounded-xl p-3 outline-none focus:ring-2 focus:ring-blue-500 transition-all resize-none text-gray-900 dark:text-white"
                                placeholder={`Quoi de neuf, ${user?.nom} ?`}
                                rows="3"
                                value={newPostContent}
                                onChange={(e) => setNewPostContent(e.target.value)}
                            />
                            <div className="flex justify-between items-center mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
                                <button type="button" className="text-gray-500 hover:text-blue-500 transition-colors p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700">
                                    <ImageIcon className="w-5 h-5" />
                                </button>
                                <button
                                    type="submit"
                                    disabled={isCreating || !newPostContent.trim()}
                                    className="bg-blue-600 hover:bg-blue-700 text-white rounded-full py-2 px-6 font-medium transition-all transform hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                                >
                                    <span className="flex items-center">
                                        {isCreating ? <Loader className="w-4 h-4 animate-spin mr-2" /> : <Send className="w-4 h-4 mr-2" />}
                                        Publier
                                    </span>
                                </button>
                            </div>
                        </div>
                    </div>
                </form>
            </div>

            {/* Liste des Posts */}
            {isLoading ? (
                <PostSkeleton />
            ) : (
                <div className="space-y-6">
                    {posts.map(post => (
                        <article key={post._id} className="bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden border border-gray-100 dark:border-gray-700 hover:shadow-lg transition-shadow duration-300">
                            <div className="p-4">
                                <div className="flex justify-between items-start">
                                    <div className="flex items-center space-x-3 mb-4">
                                        <div className="h-10 w-10 rounded-full bg-linear-to-tr from-yellow-400 to-orange-500 flex items-center justify-center text-white font-bold text-sm select-none">
                                            {post.auteur?.nom?.charAt(0).toUpperCase() || '?'}
                                        </div>
                                        <div>
                                            <h3 className="font-semibold text-gray-900 dark:text-white">{post.auteur?.nom || 'Utilisateur inconnu'}</h3>
                                            <p className="text-xs text-gray-500">{new Date(post.createdAt).toLocaleDateString()} à {new Date(post.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
                                        </div>
                                    </div>
                                    {user._id === post.auteur?._id && (
                                        <button onClick={() => handleDelete(post._id)} className="text-gray-400 hover:text-red-500 transition-colors p-1">
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    )}
                                </div>

                                <p className="text-gray-800 dark:text-gray-200 whitespace-pre-wrap mb-4 px-1">{post.contenu}</p>

                                {/* Images placeholder (si on en a) */}
                                {post.images && post.images.length > 0 && (
                                    <div className="mb-4 rounded-lg overflow-hidden bg-gray-200 dark:bg-gray-900 h-64 flex items-center justify-center">
                                        <span className="text-gray-500 italic">Image: {post.images[0]}</span>
                                    </div>
                                )}

                                <div className="flex items-center space-x-6 pt-4 border-t border-gray-100 dark:border-gray-700">
                                    <button
                                        onClick={() => handleLike(post)}
                                        className={`flex items-center space-x-2 transition-colors ${post.likes.includes(user._id) ? 'text-red-500' : 'text-gray-500 hover:text-red-500'}`}
                                    >
                                        <Heart className={`w-5 h-5 ${post.likes.includes(user._id) ? 'fill-current' : ''}`} />
                                        <span className="text-sm font-medium">{post.nombreLikes}</span>
                                    </button>

                                    <button className="flex items-center space-x-2 text-gray-500 hover:text-blue-500 transition-colors">
                                        <MessageCircle className="w-5 h-5" />
                                        <span className="text-sm font-medium">{post.commentaires?.length || 0}</span>
                                    </button>
                                </div>
                            </div>
                        </article>
                    ))}

                    {posts.length === 0 && (
                        <div className="text-center py-10 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
                            <p className="text-gray-500">Aucun post pour le moment. Soyez le premier à publier !</p>
                        </div>
                    )}

                    {page < totalPages && (
                        <div className="text-center pt-4">
                            <button
                                onClick={() => {
                                    setPage(old => old + 1);
                                }}
                                className="px-6 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-full text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors shadow-sm"
                            >
                                Charger plus
                            </button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default Posts;
